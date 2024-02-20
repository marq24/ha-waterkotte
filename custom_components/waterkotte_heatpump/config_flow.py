"""Adds config flow for Waterkotte Heatpump."""
import logging
import voluptuous as vol

from socket import gethostbyname

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
    TITLE,
    CONF_POLLING_INTERVAL,
    CONF_TAGS_PER_REQUEST,
    CONF_BIOS,
    CONF_FW,
    CONF_SERIAL,
    CONF_ID,
    CONF_SERIES,
    CONF_SYSTEMTYPE,
    CONF_HOST,
    CONF_IP,
)

from custom_components.waterkotte_heatpump.pywaterkotte_ha import WaterkotteClient
from custom_components.waterkotte_heatpump.pywaterkotte_ha.const import EASYCON, ECOTOUCH
from custom_components.waterkotte_heatpump.pywaterkotte_ha.ecotouch import EcotouchTag
from .pywaterkotte_ha.error import Http404Exception

_LOGGER: logging.Logger = logging.getLogger(__package__)


class WaterkotteHeatpumpFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for waterkotte_heatpump."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    def __init__(self):
        """Initialize."""
        self._errors = {}
        self._ip = ""
        self._bios = ""
        self._firmware = ""
        self._ID = ""  # pylint: disable=invalid-name
        self._series = ""
        self._serial = ""

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        self._errors = {}

        # Uncomment the next 2 lines if only a single instance of the integration is allowed:
        # if self._async_current_entries():
        #     return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            if CONF_SYSTEMTYPE in user_input:
                # it really sucks, that translation keys have to be lower case...
                user_input[CONF_SYSTEMTYPE] = user_input[CONF_SYSTEMTYPE].upper()

            valid = await self._test_credentials(
                user_input[CONF_HOST],
                user_input[CONF_SYSTEMTYPE],
                user_input[CONF_TAGS_PER_REQUEST],
            )

            if valid:
                user_input[CONF_IP] = self._ip
                user_input[CONF_BIOS] = self._bios
                user_input[CONF_FW] = self._firmware
                user_input[CONF_SERIES] = self._series
                user_input[CONF_SERIAL] = self._serial
                user_input[CONF_ID] = self._ID
                return self.async_create_entry(title=TITLE, data=user_input)
            else:
                if user_input[CONF_SYSTEMTYPE] == EASYCON:
                    self._errors["base"] = "type"
                else:
                    self._errors["base"] = "auth"
        else:
            user_input = {}
            user_input[CONF_HOST] = ""
            user_input[CONF_SYSTEMTYPE] = ECOTOUCH

        # it really sucks, that translation keys have to be lower case... so we need to make sure that our
        # options are all translate to lower case!
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_HOST, default=user_input.get(CONF_HOST)): str,
                vol.Required(CONF_SYSTEMTYPE, default=(user_input.get(CONF_SYSTEMTYPE, ECOTOUCH)).lower()):
                    selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=[ECOTOUCH.lower(), EASYCON.lower()],
                            mode=selector.SelectSelectorMode.DROPDOWN,
                            translation_key=CONF_SYSTEMTYPE
                        )
                    ),
                vol.Required(CONF_POLLING_INTERVAL, default=60): int,
                vol.Required(CONF_TAGS_PER_REQUEST, default=75): int,
            }),
            last_step=True,
            errors=self._errors
        )

    async def _test_credentials(self, host, system_type, tags_per_request):
        try:
            hasPort = host.find(":")
            _LOGGER.debug(f"host entered: {host} has port? {hasPort}")
            if hasPort == -1:
                self._ip = gethostbyname(host)
            else:
                self._ip = gethostbyname(host[:hasPort])

            _LOGGER.debug(f"ip detected: {self._ip}")
            session = async_create_clientsession(self.hass)
            client = WaterkotteClient(
                host=host,
                system_type=system_type,
                web_session=session,
                tags=None,
                tags_per_request=tags_per_request,
                lang=self.hass.config.language.lower()
            )
            await client.login()
            init_tags = [
                EcotouchTag.VERSION_BIOS,
                EcotouchTag.VERSION_CONTROLLER,
                EcotouchTag.INFO_ID,
                EcotouchTag.INFO_SERIAL,
                EcotouchTag.INFO_SERIES,
            ]
            ret = await client.async_read_values(init_tags)
            self._bios = ret[EcotouchTag.VERSION_BIOS]["value"]
            self._firmware = ret[EcotouchTag.VERSION_CONTROLLER]["value"]
            self._ID = str(ret[EcotouchTag.INFO_ID]["value"])
            self._series = str(ret[EcotouchTag.INFO_SERIES]["value"])
            self._serial = str(ret[EcotouchTag.INFO_SERIAL]["value"])
            _LOGGER.info(f"successfully validated login -> result: {ret}")
            return True

        except Exception as exc:
            if isinstance(exc, Http404Exception):
                _LOGGER.error(f"EASYCON Mode caused HTTP 404")
            else:
                _LOGGER.error(f"Exception while test credentials: {exc}")
        return False

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return WaterkotteHeatpumpOptionsFlowHandler(config_entry)


class WaterkotteHeatpumpOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        """Initialize HACS options flow."""
        self.config_entry = config_entry
        if len(dict(config_entry.options)) == 0:
            self.options = dict(config_entry.data)
        else:
            self.options = dict(config_entry.options)

    async def async_step_init(self, user_input=None):  # pylint: disable=unused-argument
        """Manage the options."""
        return await self.async_step_user()

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        if user_input is not None:
            self.options.update(user_input)
            return await self._update_options()

        dataSchema = vol.Schema({
            vol.Required(CONF_POLLING_INTERVAL, default=self.options.get(CONF_POLLING_INTERVAL, 60)): int,
            vol.Required(CONF_TAGS_PER_REQUEST, default=self.options.get(CONF_TAGS_PER_REQUEST, 75)): int
        })

        return self.async_show_form(
            step_id="user",
            data_schema=dataSchema,
        )

    async def _update_options(self):
        return self.async_create_entry(title=TITLE, data=self.options)
