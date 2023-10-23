"""
Custom integration to integrate Waterkotte Heatpump with Home Assistant.
"""
import asyncio
import logging

from datetime import timedelta
from typing import List

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Config
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.update_coordinator import UpdateFailed
from homeassistant.helpers import device_registry as DeviceReg
from homeassistant.helpers import entity_registry as EntityReg
from custom_components.waterkotte_heatpump.pywaterkotte_ha.ecotouch import EcotouchTag
from .api import WaterkotteHeatpumpApiClient

from .const import (
    CONF_IP, CONF_BIOS, CONF_FW, CONF_SERIAL, CONF_SERIES, CONF_ID,
    CONF_HOST,
    CONF_PASSWORD,
    CONF_USERNAME,
    CONF_POLLING_INTERVAL,
    CONF_TAGS_PER_REQUEST,
    CONF_SYSTEMTYPE,
    DOMAIN,
    PLATFORMS,
    NAME,
    STARTUP_MESSAGE,
)

from . import service as waterkotteservice

_LOGGER: logging.Logger = logging.getLogger(__package__)
SCAN_INTERVAL = timedelta(seconds=60)
COORDINATOR = None
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
    fw = entry.options.get(CONF_IP, entry.data.get(CONF_IP))
    bios = entry.options.get(CONF_BIOS, entry.data.get(CONF_BIOS))

    device_registry = DeviceReg.async_get(hass)

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

    username = entry.options.get(CONF_USERNAME, entry.data.get(CONF_USERNAME))
    password = entry.options.get(CONF_PASSWORD, entry.data.get(CONF_PASSWORD))
    host = entry.options.get(CONF_HOST, entry.data.get(CONF_HOST))
    system_type = entry.options.get(CONF_SYSTEMTYPE, entry.data.get(CONF_SYSTEMTYPE))
    SCAN_INTERVAL = timedelta(seconds=entry.options.get(CONF_POLLING_INTERVAL, 60))
    tags_per_request = entry.options.get(CONF_TAGS_PER_REQUEST, entry.data.get(CONF_TAGS_PER_REQUEST))
    if tags_per_request is None:
        tags_per_request = 10

    session = async_get_clientsession(hass)
    client = WaterkotteHeatpumpApiClient(
        host=host,
        username=username,
        password=password,
        session=session,
        tags=tags,
        systemType=system_type,
        tagsPerRequest=tags_per_request
    )
    if COORDINATOR is not None:
        coordinator = WaterkotteHeatpumpDataUpdateCoordinator(
            hass,
            client=client,
            config_entry=entry,
            data=COORDINATOR.data
        )
    else:
        coordinator = WaterkotteHeatpumpDataUpdateCoordinator(
            hass,
            config_entry=entry,
            client=client
        )

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    hass.data[DOMAIN][entry.entry_id] = coordinator
    for platform in PLATFORMS:
        await hass.config_entries.async_forward_entry_setup(entry, platform)

    entry.add_update_listener(async_reload_entry)

    # after all sensors for the different platforms have been registered we can create the list
    # of all active tags - so that we only query the information from the heatpump that is currently
    # active in HA
    client.tags = generate_tag_list(hass, entry.entry_id)

    await coordinator.async_refresh()
    COORDINATOR = coordinator

    service = waterkotteservice.WaterkotteHeatpumpService(hass, entry, coordinator)
    hass.services.async_register(DOMAIN, "set_holiday", service.set_holiday)
    hass.services.async_register(DOMAIN, "set_disinfection_start_time", service.set_disinfection_start_time)
    return True


@staticmethod
def generate_tag_list(hass: HomeAssistant, config_entry_id: str) -> List[EcotouchTag]:
    _LOGGER.info(f"(re)build tag list...")
    tags = []
    if hass is not None:
        a_entity_reg = EntityReg.async_get(hass)
        if a_entity_reg is not None:
            # we query from the HA entity registry all entities that are created by this
            # 'config_entry' -> we use here just default api calls [no more hacks!]
            for entity in EntityReg.async_entries_for_config_entry(registry=a_entity_reg,
                                                                   config_entry_id=config_entry_id):
                if entity.disabled is False:
                    a_temp_tag = (entity.unique_id)
                    _LOGGER.info(f"found active entity: {entity.entity_id} using Tag: {a_temp_tag.upper()}")
                    if a_temp_tag is not None and a_temp_tag.upper() in EcotouchTag.__members__:
                        if EcotouchTag[a_temp_tag.upper()]:
                            tags.append(EcotouchTag[a_temp_tag.upper()])
                    else:
                        _LOGGER.warning(f"Tag: {a_temp_tag} not found in EcotouchTag.__members__ !")
    return tags


class WaterkotteHeatpumpDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(
            self,
            hass: HomeAssistant,
            client: WaterkotteHeatpumpApiClient,
            config_entry: ConfigEntry = None,
            data=None
    ) -> None:
        """Initialize."""
        self.api = client
        if config_entry is not None:
            self._config_entry = config_entry

        if data is None:
            self.data = {}
        else:
            self.data = data

        self.__hass = hass
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)

    async def _async_update_data(self):
        """Update data via library."""
        try:
            await self.api.login()
            _LOGGER.info(f"number of tags to query: {len(self.api.tags)}")
            # if len(self.api.tags) == 0:
            #    tags = self.generateTagList(self.__hass, self._config_entry.entry_id)
            #    self.api.tags = tags

            result = await self.api.async_get_data()
            _LOGGER.info(f"number of tag-values read: {len(result)}")

            if self.data is None:
                self.data = {}
            for a_tag_in_result in result:
                # print(f"{key}:{tagdatas[key]}")
                if result[a_tag_in_result]["status"] == "E_OK":
                    # self.data.update(tagdatas[key])
                    # self.data.update({key:tagdatas[key]})
                    self.data[a_tag_in_result] = result[a_tag_in_result]
                    # self.data =
            return self.data
        except UpdateFailed as exception:
            raise UpdateFailed() from exception

    async def async_write_tag(self, tag: EcotouchTag, value):
        """Update single data"""
        result = await self.api.async_write_value(tag, value)
        # print(res)
        if tag in result:
            self.data[tag] = result[tag]
        else:
            _LOGGER.error(f"could not write value: '{value}' to: {tag} result was: {result}")
        # self.data[result[0]]


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    unloaded = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
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
