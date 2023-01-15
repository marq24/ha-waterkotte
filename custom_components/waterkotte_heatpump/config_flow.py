"""Adds config flow for Waterkotte Heatpump."""
from socket import gethostbyname
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from custom_components.waterkotte_heatpump.pywaterkotte.ecotouch import EcotouchTag


# from custom_components.pywaterkotte import pywaterkotte
# from .pywaterkotte.ecotouch import Ecotouch, EcotouchTag
from .api import WaterkotteHeatpumpApiClient

from .const import CONF_HOST, CONF_IP, CONF_PASSWORD, CONF_USERNAME
from .const import CONF_POLLING_INTERVAL, CONF_BIOS, CONF_FW, CONF_SERIAL, CONF_ID, CONF_SERIES
from .const import DOMAIN, SELECT, SENSOR, BINARY_SENSOR, TITLE


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
            valid = await self._test_credentials(
                user_input[CONF_USERNAME],
                user_input[CONF_PASSWORD],
                user_input[CONF_HOST],
            )
            if valid:
                user_input[CONF_IP] = self._ip
                user_input[CONF_BIOS] = self._bios
                user_input[CONF_FW] = self._firmware
                user_input[CONF_SERIES] = self._series
                user_input[CONF_SERIAL] = self._serial
                user_input[CONF_ID] = self._ID
                return self.async_create_entry(
                    title=user_input[CONF_USERNAME], data=user_input
                )
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
                    vol.Required(CONF_HOST, default="wp.knx.pattison.de"): str,
                    vol.Required(CONF_USERNAME, default="waterkotte"): str,
                    vol.Required(CONF_PASSWORD, default="waterkotte"): str,
                }
            ),
            errors=self._errors,
        )

    async def _test_credentials(self, username, password, host):
        """Return true if credentials is valid."""
        try:
            # # session = async_create_clientsession(self.hass)
            # client = Ecotouch(host)
            # await client.login(username, password)
            # ret = await client.read_value(EcotouchTag.DATE_DAY)
            # # print(ret)
            # return ret["status"] == "E_OK"
            # # await client.async_get_data()
            self._ip = gethostbyname(host)
            session = async_create_clientsession(self.hass)
            client = WaterkotteHeatpumpApiClient(host, username, password, session, None)
            await client.login()
            # await client.async_read_value(EcotouchTag.DATE_DAY)
            inittag = [
                EcotouchTag.VERSION_BIOS,
                EcotouchTag.VERSION_CONTROLLER,
                # EcotouchTag.VERSION_CONTROLLER_BUILD,
                EcotouchTag.INFO_ID,
                EcotouchTag.INFO_SERIAL,
                EcotouchTag.INFO_SERIES]
            ret = await client.async_read_values(inittag)
            self._bios = ret[EcotouchTag.VERSION_BIOS]['value']
            self._firmware = ret[EcotouchTag.VERSION_CONTROLLER]['value']
            self._ID = str(ret[EcotouchTag.INFO_ID]['value'])
            self._series = str(ret[EcotouchTag.INFO_SERIES]['value'])
            self._serial = str(ret[EcotouchTag.INFO_SERIAL]['value'])
            # print(ret)
            return True

        except Exception:  # pylint: disable=broad-except
            pass
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

        data_schema = vol.Schema(
            {
                vol.Required(BINARY_SENSOR, default=self.options.get(BINARY_SENSOR, True)): bool,
                vol.Required(SENSOR, default=self.options.get(SENSOR, True)): bool,
                vol.Required(SELECT, default=self.options.get(SELECT, True)): bool,
                vol.Required(CONF_POLLING_INTERVAL, default=self.options.get(CONF_POLLING_INTERVAL, 30)): int,  # pylint: disable=line-too-long
                vol.Required(CONF_USERNAME, default=self.options.get(CONF_USERNAME)): str,
                vol.Required(CONF_PASSWORD, default=self.options.get(CONF_USERNAME)): str,
            })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
        )

    async def _update_options(self):
        """Update config entry options."""
        return self.async_create_entry(
            title=TITLE, data=self.options
        )
