"""Adds config flow for Waterkotte Heatpump."""
import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.helpers import selector
from homeassistant.util import uuid as uuid_util

from homeassistant.const import CONF_ID, CONF_HOST, CONF_USERNAME, CONF_PASSWORD

from .const import (
    DOMAIN,
    TITLE,
    CONF_POLLING_INTERVAL,
    CONF_TAGS_PER_REQUEST,
    CONF_BIOS,
    CONF_FW,
    CONF_SERIAL,
    CONF_SERIES,
    CONF_SYSTEMTYPE,
    CONF_ADD_SCHEDULE_ENTITIES,
    CONF_ADD_SERIAL_AS_ID,
    CONF_USE_DISINFECTION,
    CONF_USE_HEATING_CURVE,
    CONF_USE_VENT,
    CONF_USE_POOL
)

from custom_components.waterkotte_heatpump.pywaterkotte_ha import WaterkotteClient
from custom_components.waterkotte_heatpump.pywaterkotte_ha.const import EASYCON, ECOTOUCH
from custom_components.waterkotte_heatpump.pywaterkotte_ha.tags import WKHPTag
from .pywaterkotte_ha.error import Http404Exception

_LOGGER: logging.Logger = logging.getLogger(__package__)


class WaterkotteHeatpumpFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for waterkotte_heatpump."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    def __init__(self):
        """Initialize."""
        self._errors = {}
        self._user_step_user_input = None
        self._bios = ""
        self._firmware = ""
        self._id = ""
        self._series = ""
        self._serial = ""

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        self._errors = {}

        if user_input is not None:
            if CONF_SYSTEMTYPE in user_input:
                # it really sucks, that translation keys have to be lower case...
                user_input[CONF_SYSTEMTYPE] = user_input[CONF_SYSTEMTYPE].upper()

                if user_input[CONF_SYSTEMTYPE] == EASYCON:
                    return await self.async_step_user_easycon()
                else:
                    return await self.async_step_user_ecotouch()
        else:
            user_input = {}
            user_input[CONF_SYSTEMTYPE] = ECOTOUCH

        # it really sucks, that translation keys have to be lower case... so we need to make sure that our
        # options are all translate to lower case!
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_SYSTEMTYPE, default=(user_input.get(CONF_SYSTEMTYPE, ECOTOUCH)).lower()):
                    selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=[ECOTOUCH.lower(), EASYCON.lower()],
                            mode=selector.SelectSelectorMode.DROPDOWN,
                            translation_key=CONF_SYSTEMTYPE
                        )
                    ),
            }),
            last_step=False,
            errors=self._errors
        )

    async def async_step_user_easycon(self, user_input=None):
        """Handle a flow initialized by the user."""
        self._errors = {}

        # Uncomment the next 2 lines if only a single instance of the integration is allowed:
        # if self._async_current_entries():
        #     return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            user_input[CONF_SYSTEMTYPE] = EASYCON
            user_input[CONF_ADD_SCHEDULE_ENTITIES] = False
            valid = await self._test_credentials(
                host=user_input[CONF_HOST],
                username=None,
                pwd=None,
                system_type=user_input[CONF_SYSTEMTYPE],
                tags_per_request=user_input[CONF_TAGS_PER_REQUEST],
            )
            if valid:
                user_input[CONF_BIOS] = self._bios
                user_input[CONF_FW] = self._firmware
                user_input[CONF_SERIES] = self._series
                user_input[CONF_SERIAL] = self._serial
                user_input[CONF_ID] = self._id
                self._user_step_user_input = dict(user_input)
                return await self.async_step_features()
            else:
                self._errors["base"] = "type"
        else:
            user_input = {}
            user_input[CONF_HOST] = ""
            user_input[CONF_ADD_SERIAL_AS_ID] = False

        return self.async_show_form(
            step_id="user_easycon",
            data_schema=vol.Schema({
                vol.Required(CONF_HOST, default=user_input.get(CONF_HOST)): str,
                vol.Required(CONF_POLLING_INTERVAL, default=500): int,
                vol.Required(CONF_TAGS_PER_REQUEST, default=25): int,
                vol.Required(CONF_ADD_SERIAL_AS_ID, default=False): bool
            }),
            last_step=False,
            errors=self._errors
        )

    async def async_step_user_ecotouch(self, user_input=None):
        """Handle a flow initialized by the user."""
        self._errors = {}

        # Uncomment the next 2 lines if only a single instance of the integration is allowed:
        # if self._async_current_entries():
        #     return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            user_input[CONF_SYSTEMTYPE] = ECOTOUCH
            valid = await self._test_credentials(
                host=user_input[CONF_HOST],
                username=user_input[CONF_USERNAME],
                pwd=user_input[CONF_PASSWORD],
                system_type=user_input[CONF_SYSTEMTYPE],
                tags_per_request=user_input[CONF_TAGS_PER_REQUEST],
            )
            if valid:
                user_input[CONF_BIOS] = self._bios
                user_input[CONF_FW] = self._firmware
                user_input[CONF_SERIES] = self._series
                user_input[CONF_SERIAL] = self._serial
                user_input[CONF_ID] = self._id
                self._user_step_user_input = dict(user_input)
                return await self.async_step_features()
            else:
                self._errors["base"] = "auth"
        else:
            user_input = {}
            user_input[CONF_HOST] = ""
            user_input[CONF_USERNAME] = "waterkotte"
            user_input[CONF_PASSWORD] = "waterkotte"
            user_input[CONF_ADD_SCHEDULE_ENTITIES] = False
            user_input[CONF_ADD_SERIAL_AS_ID] = False

        return self.async_show_form(
            step_id="user_ecotouch",
            data_schema=vol.Schema({
                vol.Required(CONF_HOST, default=user_input.get(CONF_HOST)): str,
                vol.Optional(CONF_USERNAME, default=user_input.get(CONF_USERNAME)): str,
                vol.Required(CONF_PASSWORD, default=user_input.get(CONF_PASSWORD)): str,
                vol.Required(CONF_POLLING_INTERVAL, default=60): int,
                vol.Required(CONF_TAGS_PER_REQUEST, default=75): int,
                vol.Required(CONF_ADD_SCHEDULE_ENTITIES, default=False): bool,
                vol.Required(CONF_ADD_SERIAL_AS_ID, default=False): bool,
            }),
            last_step=False,
            errors=self._errors
        )

    async def async_step_features(self, user_input=None):
        self._errors = {}
        if user_input is not None:
            for k, v in user_input.items():
                self._user_step_user_input[k] = v

            return self.async_create_entry(title=TITLE, data=self._user_step_user_input)
        else:
            return self.async_show_form(
                step_id="features",
                data_schema=vol.Schema({
                    vol.Required(CONF_USE_VENT, default=False): bool,
                    vol.Required(CONF_USE_HEATING_CURVE, default=False): bool,
                    vol.Required(CONF_USE_DISINFECTION, default=False): bool,
                    vol.Required(CONF_USE_POOL, default=False): bool,
                }),
                last_step=True,
                errors=self._errors
            )

    async def _test_credentials(self, host, username, pwd, system_type, tags_per_request):
        try:
            session = async_create_clientsession(self.hass)
            client = WaterkotteClient(host=host, username=username, pwd=pwd, system_type=system_type,
                                      web_session=session, tags=None, tags_per_request=tags_per_request,
                                      lang=self.hass.config.language.lower())
            await client.login()
            init_tags = [
                WKHPTag.VERSION_BIOS,
                WKHPTag.VERSION_CONTROLLER,
                WKHPTag.INFO_ID,
                WKHPTag.INFO_SERIAL,
                WKHPTag.INFO_SERIES,
            ]
            ret = await client.async_read_values(init_tags)

            self._bios = ret[WKHPTag.VERSION_BIOS]["value"]
            self._firmware = ret[WKHPTag.VERSION_CONTROLLER]["value"]
            self._id = str(ret[WKHPTag.INFO_ID]["value"])
            self._series = str(ret[WKHPTag.INFO_SERIES]["value"])
            self._serial = str(ret[WKHPTag.INFO_SERIAL]["value"])
            if self._serial is None or self._serial == "None":
                self._serial = uuid_util.random_uuid_hex()

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

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Optional(CONF_USERNAME, default=self.options.get(CONF_USERNAME, "waterkotte")): str,
                vol.Required(CONF_PASSWORD, default=self.options.get(CONF_PASSWORD, "waterkotte")): str,
                vol.Required(CONF_POLLING_INTERVAL, default=self.options.get(CONF_POLLING_INTERVAL, 60)): int,
                vol.Required(CONF_TAGS_PER_REQUEST, default=self.options.get(CONF_TAGS_PER_REQUEST, 75)): int,
                vol.Required(CONF_ADD_SCHEDULE_ENTITIES, default=self.options.get(CONF_ADD_SCHEDULE_ENTITIES, False)): bool
            }),
        )

    async def _update_options(self):
        return self.async_create_entry(title=TITLE, data=self.options)
