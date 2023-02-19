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
from homeassistant.helpers.entity_registry import async_entries_for_device
from homeassistant.helpers.entity_registry import async_get as getEntityRegistry
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers import device_registry as dr
from custom_components.waterkotte_heatpump.mypywaterkotte.ecotouch import EcotouchTag
from .api import WaterkotteHeatpumpApiClient
from .const import CONF_IP, CONF_BIOS, CONF_FW, CONF_SERIAL, CONF_SERIES, CONF_ID, CONF_TAGS_PER_REQUEST
from .const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_USERNAME,
    CONF_POLLING_INTERVAL,
    CONF_SYSTEMTYPE,
)
from .const import DOMAIN, NAME, TITLE
from .const import PLATFORMS
from .const import STARTUP_MESSAGE

from . import service as waterkotteservice

# from .const import SENSORS

SCAN_INTERVAL = timedelta(seconds=60)
COORDINATOR = None
_LOGGER: logging.Logger = logging.getLogger(__package__)

tags = []


async def async_setup(
    hass: HomeAssistant, config: Config
):  # pylint: disable=unused-argument
    """Set up this integration using YAML is not supported."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up this integration using UI."""
    global SCAN_INTERVAL  # pylint: disable=global-statement
    global COORDINATOR  # pylint: disable=global-statement
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.info(STARTUP_MESSAGE)

    # Setup Device
    fw = entry.options.get(
        CONF_IP, entry.data.get(CONF_IP)
    )  # pylint: disable=invalid-name
    bios = entry.options.get(CONF_BIOS, entry.data.get(CONF_BIOS))

    device_registry = dr.async_get(hass)

    device_registry.async_get_or_create(  # pylint: disable=invalid-name
        config_entry_id=entry.entry_id,
        identifiers={
            ("DOMAIN", DOMAIN),
            ("IP", entry.options.get(CONF_IP, entry.data.get(CONF_IP))),
        },
        manufacturer=NAME,
        suggested_area="Basement",
        name=NAME,
        model=entry.options.get(CONF_SERIES, entry.data.get(CONF_SERIES)),
        sw_version=f"{fw} BIOS: {bios}",
        hw_version=entry.options.get(CONF_ID, entry.data.get(CONF_ID)),
    )

    # device = DeviceInfo(
    #     id=deviceEntry.id,
    #     identifiers=deviceEntry.identifiers,
    #     name=deviceEntry.name,
    #     manufacturer=deviceEntry.manufacturer,
    #     model=deviceEntry.model,
    #     sw_version=deviceEntry.sw_version,
    #     suggested_area=deviceEntry.suggested_area,
    #     hw_version=deviceEntry.hw_version,
    # )

    ###
    username = entry.options.get(CONF_USERNAME, entry.data.get(CONF_USERNAME))
    password = entry.options.get(CONF_PASSWORD, entry.data.get(CONF_PASSWORD))
    host = entry.options.get(CONF_HOST, entry.data.get(CONF_HOST))
    SCAN_INTERVAL = timedelta(seconds=entry.options.get(CONF_POLLING_INTERVAL, 60))
    session = async_get_clientsession(hass)
    system_type = entry.options.get(CONF_SYSTEMTYPE, entry.data.get(CONF_SYSTEMTYPE))
    tags_per_request = entry.options.get(CONF_TAGS_PER_REQUEST, entry.data.get(CONF_TAGS_PER_REQUEST))
    client = WaterkotteHeatpumpApiClient(
        host, username, password, session, tags, systemType=system_type, tagsPerRequest=tags_per_request
    )
    if COORDINATOR is not None:
        coordinator = WaterkotteHeatpumpDataUpdateCoordinator(
            hass,
            client=client,
            data=COORDINATOR.data,
        )
    else:
        coordinator = WaterkotteHeatpumpDataUpdateCoordinator(hass, client=client)
    # await coordinator.async_refresh() ##Needed?

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    hass.data[DOMAIN][entry.entry_id] = coordinator
    for platform in PLATFORMS:
        if entry.options.get(platform, True):
            coordinator.platforms.append(platform)
            # hass.async_add_job(
            await hass.config_entries.async_forward_entry_setup(entry, platform)
            # )
    entry.add_update_listener(async_reload_entry)

    if len(tags) > 0:
        await coordinator.async_refresh()
    COORDINATOR = coordinator

    service = waterkotteservice.WaterkotteHeatpumpService(hass, entry, coordinator)

    hass.services.async_register(DOMAIN, "set_holiday", service.set_holiday)
    hass.services.async_register(DOMAIN, "set_time", service.set_time)
    return True


class WaterkotteHeatpumpDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(
        self, hass: HomeAssistant, client: WaterkotteHeatpumpApiClient, data=None
    ) -> None:
        """Initialize."""
        self.api = client
        if data is None:
            self.data = {}
        else:
            self.data = data
        self.platforms = []
        self.__hass = hass
        self.alltags = {}
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)

    async def _async_update_data(self):
        """Update data via library."""
        try:
            await self.api.login()
            if len(self.api.tags) == 0:
                tags = []
                for entity in self.__hass.data["entity_registry"].entities:
                    if (  # pylint: disable=line-too-long
                        self.__hass.data["entity_registry"].entities[entity].platform
                        == DOMAIN
                        and self.__hass.data["entity_registry"]
                        .entities[entity]
                        .disabled
                        is False
                    ):
                        # x += 1
                        # print(entity)
                        tag = (
                            self.__hass.data["entity_registry"]
                            .entities[entity]
                            .unique_id
                        )
                        print(f"Entity: {entity} Tag: {tag.upper()}")
                        # match = re.search(r"^.*\.(.*)_waterkotte_heatpump", entity)
                        # match = re.search(r"^.*\.(.*)", entity)

                        # I (marq24) do not really understand why we check here, if the
                        # tag is available in the 'EcotouchTag' - but what do I know...
                        if tag is not None and tag.upper() in EcotouchTag.__members__:
                            # print(match.groups()[0].upper())
                            if EcotouchTag[  # pylint: disable=unsubscriptable-object
                                tag.upper()
                            ]:
                                # print(EcotouchTag[match.groups()[0].upper()]) # pylint: disable=unsubscriptable-object
                                tags.append(
                                    EcotouchTag[tag.upper()]
                                )  # pylint: disable=unsubscriptable-object
                        # match = re.search(r"^.*\.(.*)", entity)
                        # if match:
                        #     print(match.groups()[0].upper())
                        #     if EcotouchTag[match.groups()[0].upper()]:  # pylint: disable=unsubscriptable-object
                        #         # print(EcotouchTag[match.groups()[0].upper()]) # pylint: disable=unsubscriptable-object
                        #         tags.append(EcotouchTag[match.groups()[0].upper()])  # pylint: disable=unsubscriptable-object
                        else:
                            _LOGGER.warning(_LOGGER.warning(f"Tag: {tag} not found in EcotouchTag.__members__ !"))
                self.api.tags = tags

            tagdatas = await self.api.async_get_data()
            if self.data is None:
                self.data = {}
            for key in tagdatas:
                # print(f"{key}:{tagdatas[key]}")
                if tagdatas[key]["status"] == "E_OK":
                    # self.data.update(tagdatas[key])
                    # self.data.update({key:tagdatas[key]})
                    self.data[key] = tagdatas[key]
                    # self.data =
            return self.data
        except UpdateFailed as exception:
            raise UpdateFailed() from exception

    async def async_write_tag(self, tag: EcotouchTag, value):
        """Update single data"""
        res = await self.api.async_write_value(tag, value)
        # print(res)
        self.data[tag]["value"] = res[tag.tags[0]]["value"]
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
