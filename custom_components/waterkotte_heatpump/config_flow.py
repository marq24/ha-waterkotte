"""Adds config flow for Waterkotte Heatpump."""
import voluptuous as vol

from socket import gethostbyname
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from custom_components.waterkotte_heatpump.pywaterkotte.ecotouch import EcotouchTag


# from custom_components.pywaterkotte import pywaterkotte
# from .pywaterkotte.ecotouch import Ecotouch, EcotouchTag
from .api import WaterkotteHeatpumpApiClient

from .const import CONF_HOST, CONF_IP, CONF_PASSWORD, CONF_USERNAME, CONF_POLLING_INTERVAL, CONF_BIOS, CONF_FW
from .const import DOMAIN
from .const import PLATFORMS


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
                EcotouchTag.VERSION_CONTROLLER_BUILD]
            ret = await client.async_read_values(inittag)
            self._bios = f"{str(ret[EcotouchTag.VERSION_BIOS]['value'])[0]}.{str(ret[EcotouchTag.VERSION_BIOS]['value'])[1:3]}"
            self._firmware = f"0{str(ret[EcotouchTag.VERSION_CONTROLLER]['value'])[0]}.{str(ret[EcotouchTag.VERSION_CONTROLLER]['value'])[1:3]}.{str(ret[EcotouchTag.VERSION_CONTROLLER]['value'])[3:]}-{str(ret[EcotouchTag.VERSION_CONTROLLER_BUILD]['value'])}"
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
                vol.Required(x, default=self.options.get(x, True)): bool
                for x in sorted(PLATFORMS)
            })
        data_schema = data_schema.extend(
            {
                vol.Required(CONF_POLLING_INTERVAL, default=self.options.get(CONF_POLLING_INTERVAL, 30)): int,
                vol.Required(
                    CONF_USERNAME,
                    default=self.options.get(CONF_USERNAME),
                    msg="Username"): str,
                vol.Required(
                    CONF_PASSWORD,
                    default=self.options.get(CONF_USERNAME),
                    description="Password"): str,
            })
        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
        )

    async def _update_options(self):
        """Update config entry options."""
        return self.async_create_entry(
            title=self.config_entry.data.get(CONF_USERNAME), data=self.options
        )
