"""
Custom integration to integrate Waterkotte Heatpump with Home Assistant.

For more details about this integration, please refer to
https://github.com/pattisonmichael/waterkotte-heatpump
"""
import asyncio
import logging
import re
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Config
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.update_coordinator import UpdateFailed

from .api import WaterkotteHeatpumpApiClient
from .const import CONF_HOST, CONF_PASSWORD
from .const import CONF_USERNAME, CONF_POLLING_INTERVAL
from .const import DOMAIN
from .const import PLATFORMS
from .const import STARTUP_MESSAGE
from .pywaterkotte.ecotouch import EcotouchTag
# from .const import SENSORS

SCAN_INTERVAL = timedelta(seconds=60)
COORDINATOR = None
_LOGGER: logging.Logger = logging.getLogger(__package__)

tags = []


async def async_setup(hass: HomeAssistant, config: Config):  # pylint: disable=unused-argument
    """Set up this integration using YAML is not supported."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up this integration using UI."""
    global SCAN_INTERVAL  # pylint: disable=global-statement
    global COORDINATOR  # pylint: disable=global-statement
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.info(STARTUP_MESSAGE)

    username = entry.options.get(CONF_USERNAME, entry.data.get(CONF_USERNAME))
    password = entry.options.get(CONF_PASSWORD, entry.data.get(CONF_PASSWORD))
    host = entry.options.get(CONF_HOST, entry.data.get(CONF_HOST))
    SCAN_INTERVAL = entry.options.get(CONF_POLLING_INTERVAL, timedelta(seconds=60))
    session = async_get_clientsession(hass)
    client = WaterkotteHeatpumpApiClient(host, username, password, session, tags)
    if COORDINATOR is not None:
        coordinator = WaterkotteHeatpumpDataUpdateCoordinator(hass, client=client, data=COORDINATOR.data)
    else:
        coordinator = WaterkotteHeatpumpDataUpdateCoordinator(hass, client=client)
    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    hass.data[DOMAIN][entry.entry_id] = coordinator
    for platform in PLATFORMS:
        if entry.options.get(platform, True):
            coordinator.platforms.append(platform)
            hass.async_add_job(
                hass.config_entries.async_forward_entry_setup(entry, platform)
            )
    entry.add_update_listener(async_reload_entry)

    tags.clear()
    for entity in hass.data["entity_registry"].entities:
        if (
           hass.data["entity_registry"].entities[entity].platform == "waterkotte_heatpump"
           and hass.data["entity_registry"].entities[entity].disabled is False):
            # x += 1

            # r"#%s\t(?P<status>[A-Z_]+)\n\d+\t(?P<value>\-?\d+)" % tag,
            # match = re.search(r"^.*\.(.*)_waterkotte_heatpump", entity)
            # if match:
            #     print(match.groups()[0].upper())
            #     if EcotouchTag[match.groups()[0].upper()]:  # pylint: disable=unsubscriptable-object
            #         # print(EcotouchTag[match.groups()[0].upper()]) # pylint: disable=unsubscriptable-object
            #         tags.append(EcotouchTag[match.groups()[0].upper()])  # pylint: disable=unsubscriptable-object
            tag = hass.data["entity_registry"].entities[entity].unique_id
            print(f"__init__.async_setup_entry Entity: {entity} Tag: {tag}")
            tags.append(EcotouchTag[tag.upper()])
    # print(x)
    # print(tags)

    client = WaterkotteHeatpumpApiClient(host, username, password, session, tags)
    if len(tags) > 0:
        await coordinator.async_refresh()
    COORDINATOR = coordinator
    return True


class WaterkotteHeatpumpDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: WaterkotteHeatpumpApiClient,
        data=[]
    ) -> None:
        """Initialize."""
        self.api = client
        self.data = data
        self.platforms = []
        self.__hass = hass

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)

    async def _async_update_data(self):
        """Update data via library."""
        try:
            await self.api.login()
            if len(self.api.tags) == 0:
                tags = []
                for entity in self.__hass.data["entity_registry"].entities:
                    if (
                            self.__hass.data["entity_registry"].entities[entity].platform == "waterkotte_heatpump"
                            and self.__hass.data["entity_registry"].entities[entity].disabled is False):
                        # x += 1
                        # print(entity)
                        tag = self.__hass.data["entity_registry"].entities[entity].unique_id
                        print(f"Entity: {entity} Tag: {tag.upper()}")
                        # match = re.search(r"^.*\.(.*)_waterkotte_heatpump", entity)
                        # match = re.search(r"^.*\.(.*)", entity)
                        if tag is not None and tag.upper() in EcotouchTag.__members__:
                            # print(match.groups()[0].upper())
                            if EcotouchTag[tag.upper()]:  # pylint: disable=unsubscriptable-object
                                # print(EcotouchTag[match.groups()[0].upper()]) # pylint: disable=unsubscriptable-object
                                tags.append(EcotouchTag[tag.upper()])  # pylint: disable=unsubscriptable-object
                        # match = re.search(r"^.*\.(.*)", entity)
                        # if match:
                        #     print(match.groups()[0].upper())
                        #     if EcotouchTag[match.groups()[0].upper()]:  # pylint: disable=unsubscriptable-object
                        #         # print(EcotouchTag[match.groups()[0].upper()]) # pylint: disable=unsubscriptable-object
                        #         tags.append(EcotouchTag[match.groups()[0].upper()])  # pylint: disable=unsubscriptable-object
                self.api.tags = tags

            tagdatas = await self.api.async_get_data()
            if self.data is None:
                self.data = {}
            for key in tagdatas:
                # print(f"{key}:{tagdatas[key]}")
                if tagdatas[key]['status'] == "E_OK":
                    # self.data.update(tagdatas[key])
                    # self.data.update({key:tagdatas[key]})
                    self.data[key] = tagdatas[key]
                    # self.data =
            return self.data
        except UpdateFailed as exception:
            raise UpdateFailed() from exception

    async def async_write_tag(self, tag: EcotouchTag, value):
        """ Update single data """
        res = await self.api.async_write_value(tag, value)
        # print(res)
        self.data[tag]['value'] = res[tag.tags[0]]['value']
        # self.data[result[0]]


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    unloaded = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
                if platform in coordinator.platforms
            ]
        )
    )
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)

    await coordinator.api._client.logout()
    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
