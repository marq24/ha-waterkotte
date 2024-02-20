import asyncio
import logging
import json

from datetime import timedelta
from typing import List, Sequence
from homeassistant.config_entries import ConfigEntry, ConfigEntryState
from homeassistant.core import Config, SupportsResponse, Event
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import Entity, EntityDescription
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.update_coordinator import UpdateFailed
from homeassistant.helpers import config_validation as config_val, entity_registry as entity_reg

from .const import (
    CONF_HOST, CONF_IP, CONF_BIOS, CONF_FW, CONF_SERIAL, CONF_SERIES, CONF_ID,
    CONF_POLLING_INTERVAL,
    CONF_TAGS_PER_REQUEST,
    CONF_SYSTEMTYPE,
    NAME,
    DOMAIN,
    PLATFORMS,
    STARTUP_MESSAGE,
    SERVICE_SET_HOLIDAY,
    SERVICE_SET_DISINFECTION_START_TIME,
    SERVICE_GET_ENERGY_BALANCE,
    SERVICE_GET_ENERGY_BALANCE_MONTHLY
)

from . import service as waterkotteservice
from custom_components.waterkotte_heatpump.pywaterkotte_ha.ecotouch import EcotouchTag
from custom_components.waterkotte_heatpump.pywaterkotte_ha import WaterkotteClient, TooManyUsersException

_LOGGER: logging.Logger = logging.getLogger(__package__)
SCAN_INTERVAL = timedelta(seconds=60)
CONFIG_SCHEMA = config_val.removed(DOMAIN, raise_if_present=False)


async def async_setup(hass: HomeAssistant, config: Config):  # pylint: disable=unused-argument
    """Set up this integration using YAML is not supported."""
    return True


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    if DOMAIN not in hass.data:
        value = "UNKOWN"
        try:
            basepath = __file__[:-11]
            with open(f"{basepath}manifest.json") as f:
                manifest = json.load(f)
                value = manifest["version"]
        except:
            pass
        _LOGGER.info(STARTUP_MESSAGE)
        hass.data.setdefault(DOMAIN, {"manifest_version": value})

    coordinator = WKHPDataUpdateCoordinator(hass, config_entry)
    await coordinator.async_refresh()
    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    hass.data[DOMAIN][config_entry.entry_id] = coordinator

    for platform in PLATFORMS:
        hass.async_create_task(hass.config_entries.async_forward_entry_setup(config_entry, platform))

    if config_entry.state != ConfigEntryState.LOADED:
        config_entry.add_update_listener(async_reload_entry)

    service = waterkotteservice.WaterkotteHeatpumpService(hass, config_entry, coordinator)
    hass.services.async_register(DOMAIN, SERVICE_SET_HOLIDAY, service.set_holiday,
                                 supports_response=SupportsResponse.OPTIONAL)
    hass.services.async_register(DOMAIN, SERVICE_SET_DISINFECTION_START_TIME, service.set_disinfection_start_time,
                                 supports_response=SupportsResponse.OPTIONAL)
    hass.services.async_register(DOMAIN, SERVICE_GET_ENERGY_BALANCE, service.get_energy_balance,
                                 supports_response=SupportsResponse.ONLY)
    hass.services.async_register(DOMAIN, SERVICE_GET_ENERGY_BALANCE_MONTHLY, service.get_energy_balance_monthly,
                                 supports_response=SupportsResponse.ONLY)

    # we should check (in any CASE!) if the active tags might have...
    asyncio.create_task(coordinator.update_client_tag_list(hass, config_entry.entry_id))

    # ok we are done...
    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    unload_ok = all(await asyncio.gather(*[
        hass.config_entries.async_forward_entry_unload(config_entry, platform)
        for platform in PLATFORMS
    ]))

    if unload_ok:
        if DOMAIN in hass.data and config_entry.entry_id in hass.data[DOMAIN]:
            # even if waterkotte does not support logout... I code it here...
            coordinator = hass.data[DOMAIN][config_entry.entry_id]
            await coordinator.bridge._internal_client.logout()

            hass.data[DOMAIN].pop(config_entry.entry_id)

        hass.services.async_remove(DOMAIN, SERVICE_SET_HOLIDAY)
        hass.services.async_remove(DOMAIN, SERVICE_SET_DISINFECTION_START_TIME)
        hass.services.async_remove(DOMAIN, SERVICE_GET_ENERGY_BALANCE)
        hass.services.async_remove(DOMAIN, SERVICE_GET_ENERGY_BALANCE_MONTHLY)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """Reload config entry."""
    if await async_unload_entry(hass, config_entry):
        await asyncio.sleep(2)
        await async_setup_entry(hass, config_entry)


@staticmethod
def generate_tag_list(hass: HomeAssistant, config_entry_id: str) -> List[EcotouchTag]:
    _LOGGER.info(f"(re)build tag list...")
    tags = []
    if hass is not None:
        a_entity_reg = entity_reg.async_get(hass)
        if a_entity_reg is not None:
            # we query from the HA entity registry all entities that are created by this
            # 'config_entry' -> we use here just default api calls [no more hacks!]
            for entity in entity_reg.async_entries_for_config_entry(registry=a_entity_reg,
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


class WKHPDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, config_entry):
        self.name = config_entry.title
        self._config_entry = config_entry
        self._host = config_entry.options.get(CONF_HOST, config_entry.data[CONF_HOST])
        loc_system_type = config_entry.options.get(CONF_SYSTEMTYPE, config_entry.data.get(CONF_SYSTEMTYPE))
        loc_tags_per_request = config_entry.options.get(CONF_TAGS_PER_REQUEST,
                                                        config_entry.data.get(CONF_TAGS_PER_REQUEST, 10))

        loc_tags = generate_tag_list(hass=hass, config_entry_id=config_entry.entry_id)

        self.bridge = WaterkotteClient(host=self._host, system_type=loc_system_type,
                                       web_session=async_get_clientsession(hass), tags=loc_tags,
                                       tags_per_request=loc_tags_per_request, lang=hass.config.language.lower())

        global SCAN_INTERVAL
        # update_interval can be adjusted in the options (not for WebAPI)
        SCAN_INTERVAL = timedelta(seconds=config_entry.options.get(CONF_POLLING_INTERVAL,
                                                                   config_entry.data.get(CONF_POLLING_INTERVAL, 60)))

        fw = config_entry.options.get(CONF_IP, config_entry.data.get(CONF_IP))
        bios = config_entry.options.get(CONF_BIOS, config_entry.data.get(CONF_BIOS))
        self._device_info_dict = {
            "identifiers": {
                ("DOMAIN", DOMAIN),
                ("IP", config_entry.options.get(CONF_IP, config_entry.data.get(CONF_IP))),
            },
            "manufacturer": NAME,
            "suggested_area": "Basement",
            "name": NAME,
            "model": config_entry.options.get(CONF_SERIES, config_entry.data.get(CONF_SERIES)),
            "sw_version": f"{fw} BIOS: {bios}",
            "hw_version": config_entry.options.get(CONF_ID, config_entry.data.get(CONF_ID))
        }

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)

    async def update_client_tag_list(self, hass, entry_id):
        _LOGGER.debug(f"rechecking active tags... in 15sec")
        await asyncio.sleep(15)

        _LOGGER.debug(f"rechecking active tags NOW!")
        self.bridge.tags = generate_tag_list(hass, entry_id)

        _LOGGER.debug(f"active tags checked... now refresh sensor data")
        await self.async_refresh()

    # Callable[[Event], Any]
    def __call__(self, evt: Event) -> bool:
        _LOGGER.debug(f"Event arrived: {evt}")
        return True

    async def _async_update_data(self):
        """Update data via library."""
        try:
            await self.bridge.login()
            _LOGGER.info(f"number of entities to query: {len(self.bridge.tags)} (1 entity can consist of n-tags)")
            result = await self.bridge.async_get_data()
            _LOGGER.info(f"number of entity values read: {len(result)}")

            if self.data is None:
                self.data = {}

            for a_tag_in_result in result:
                if result[a_tag_in_result]["status"] == "S_OK":
                    self.data[a_tag_in_result] = result[a_tag_in_result]

            return self.data

        except UpdateFailed as exception:
            raise UpdateFailed() from exception
        except TooManyUsersException as too_many_users:
            _LOGGER.info(f"TooManyUsers response from waterkotte - waiting 30sec and then retry...")
            await asyncio.sleep(30)
            raise UpdateFailed() from too_many_users

    async def async_read_values(self, tags: Sequence[EcotouchTag]) -> dict:
        """Get data from the API."""
        ret = await self.bridge.async_read_values(tags)
        return ret

    async def async_write_tag(self, tag: EcotouchTag, value, entity: Entity = None):
        """Update single data"""
        result = await self.bridge.async_write_value(tag, value)
        _LOGGER.debug(f"write result: {result}")

        if tag in result:
            self.data[tag] = result[tag]
        else:
            _LOGGER.error(f"could not write value: '{value}' to: {tag} result was: {result}")

        # after we have written something to the Waterkotte we should force an update of the data...
        if entity is not None:
            entity.async_schedule_update_ha_state(force_refresh=True)


class WKHPBaseEntity(Entity):
    _attr_should_poll = False
    _attr_has_entity_name = True

    def __init__(self, coordinator: WKHPDataUpdateCoordinator, description: EntityDescription) -> None:
        self._attr_translation_key = description.key.lower()

        self.coordinator = coordinator
        self.entity_description = description
        self.entity_id = f"{DOMAIN}.wkh_{self._attr_translation_key}"

    @property
    def eco_tag(self):
        """Return a unique ID to use for this entity."""
        return self.entity_description.tag

    @property
    def device_info(self) -> dict:
        return self.coordinator._device_info_dict

    @property
    def available(self):
        """Return True if entity is available."""
        return self.coordinator.last_update_success

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        # sensor_key = self.entity_description.key
        # device_key = self.coordinator.config_entry.data[CONF_SERIAL]
        # return f"{device_key}_{sensor}"

        return self.entity_description.key

    async def async_added_to_hass(self):
        """Connect to dispatcher listening for entity data notifications."""
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))

    async def async_update(self):
        """Update entity."""
        await self.coordinator.async_request_refresh()

    @property
    def should_poll(self) -> bool:
        """Entities do not individually poll."""
        return False
