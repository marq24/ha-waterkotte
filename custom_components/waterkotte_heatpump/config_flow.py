"""Adds config flow for Waterkotte Heatpump."""
import logging
import voluptuous as vol

from socket import gethostbyname

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.helpers.selector import selector

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
    CONF_PASSWORD,
    CONF_USERNAME,
)

from .api import WaterkotteHeatpumpApiClient
from custom_components.waterkotte_heatpump.pywaterkotte_ha.const import EASYCON, ECOTOUCH
from custom_components.waterkotte_heatpump.pywaterkotte_ha.ecotouch import EcotouchTag

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
        self._system_type = ""
        self._tags_per_request = 75

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        self._errors = {}

        # Uncomment the next 2 lines if only a single instance of the integration is allowed:
        # if self._async_current_entries():
        #     return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            valid = await self._test_credentials(
                user_input[CONF_USERNAME],
                user_input[CONF_PASSWORD],
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
                user_input[CONF_SYSTEMTYPE] = self._system_type
                user_input[CONF_TAGS_PER_REQUEST] = self._tags_per_request
                return self.async_create_entry(title=TITLE, data=user_input)
            else:
                if user_input[CONF_SYSTEMTYPE] == EASYCON:
                    self._errors["base"] = "type"
                else:
                    self._errors["base"] = "auth"

            return await self._show_config_form(user_input)

        return await self._show_config_form(user_input)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return WaterkotteHeatpumpOptionsFlowHandler(config_entry)

    async def _show_config_form(self, user_input):  # pylint: disable=unused-argument
        """Show the configuration form to edit location data."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST, default=""): str,
                    vol.Required(CONF_USERNAME, default="waterkotte"): str,
                    vol.Required(CONF_PASSWORD, default="waterkotte"): str,
                    vol.Required(CONF_SYSTEMTYPE, default=ECOTOUCH): selector(
                        {
                            "select": {
                                "options": [
                                    {"label": "EcoTouch Mode [require Username & Password]", "value": ECOTOUCH},
                                    {"label": "EasyCon Mode [older Waterkotte Models without login credentials]", "value": EASYCON},
                                ],
                                "mode": "dropdown",
                            }
                        }
                    ),
                    vol.Required(CONF_TAGS_PER_REQUEST, default=75): int,
                }
            ),
            errors=self._errors,
        )

    async def _test_credentials(self, username, password, host, system_type, tags_per_request):
        """Return true if credentials is valid."""
        try:
            hasPort = host.find(":")
            _LOGGER.debug(f"host entered: {host} has port? {hasPort}")
            if hasPort == -1:
                self._ip = gethostbyname(host)
            else:
                self._ip = gethostbyname(host[:hasPort])

            _LOGGER.debug(f"ip detected: {self._ip}")
            session = async_create_clientsession(self.hass)
            client = WaterkotteHeatpumpApiClient(
                host=host,
                username=username,
                password=password,
                session=session,
                tags=None,
                systemType=system_type,
                tagsPerRequest=tags_per_request,
                lang=self.hass.config.language.lower()
            )
            await client.login()
            init_tags = [
                EcotouchTag.VERSION_BIOS,
                EcotouchTag.VERSION_CONTROLLER,
                # EcotouchTag.VERSION_CONTROLLER_BUILD,
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
            self._system_type = system_type
            self._tags_per_request = tags_per_request
            _LOGGER.info(f"successfully validated login -> result: {ret}")
            return True

        except Exception as exec:  # pylint: disable=broad-except
            if isinstance(exec, FileNotFoundError):
                _LOGGER.error(f"EASYCON Mode caused HTTP 404")
            else:
                _LOGGER.error(f"Exception while test credentials: {exec}")
        return False


class WaterkotteHeatpumpOptionsFlowHandler(config_entries.OptionsFlow):
    """Config flow options handler for waterkotte_heatpump."""

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

        dataSchema = vol.Schema(
            {
                vol.Required(
                    CONF_POLLING_INTERVAL, default=self.options.get(CONF_POLLING_INTERVAL, 60),
                ): int,  # pylint: disable=line-too-long
                vol.Required(
                    CONF_TAGS_PER_REQUEST, default=self.options.get(CONF_TAGS_PER_REQUEST, 75),
                ): int,  # pylint: disable=line-too-long
                vol.Required(
                    CONF_USERNAME, default=self.options.get(CONF_USERNAME)
                ): str,
                vol.Required(
                    CONF_PASSWORD, default=self.options.get(CONF_USERNAME)
                ): str,
                vol.Required(
                    CONF_SYSTEMTYPE, default=self.options.get(CONF_SYSTEMTYPE)
                ): selector(
                    {
                        "select": {
                            "options": [
                                {"label": "EcoTouch Mode", "value": ECOTOUCH},
                                {"label": "EasyCon Mode", "value": EASYCON},
                            ],
                            "mode": "dropdown",
                        }
                    }
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=dataSchema,
        )

    async def _update_options(self):
        """Update config entry options."""
        return self.async_create_entry(title=TITLE, data=self.options)
