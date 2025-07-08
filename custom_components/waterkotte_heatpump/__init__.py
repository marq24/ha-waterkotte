import asyncio
import logging
from datetime import timedelta
from typing import List, Collection, Sequence, Any, Tuple

from custom_components.waterkotte_heatpump.pywaterkotte_ha import WaterkotteClient
from custom_components.waterkotte_heatpump.pywaterkotte_ha.const import ECOTOUCH
from custom_components.waterkotte_heatpump.pywaterkotte_ha.error import TooManyUsersException, InvalidPasswordException
from custom_components.waterkotte_heatpump.pywaterkotte_ha.tags import WKHPTag
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ID, CONF_HOST, CONF_USERNAME, CONF_PASSWORD
from homeassistant.core import HomeAssistant, Event, SupportsResponse
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import config_validation as config_val, entity_registry as entity_reg
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import Entity, EntityDescription
from homeassistant.helpers.typing import UNDEFINED, UndefinedType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from . import service as waterkotte_service
from .const import (
    CONF_IP,
    CONF_POLLING_INTERVAL,
    CONF_TAGS_PER_REQUEST,
    CONF_BIOS,
    CONF_FW,
    CONF_SERIAL,
    CONF_SERIES,
    CONF_SYSTEMTYPE,
    CONF_ADD_SCHEDULE_ENTITIES,
    CONF_ADD_SERIAL_AS_ID,
    CONF_USE_VENT,
    CONF_USE_HEATING_CURVE,
    CONF_USE_DISINFECTION,
    NAME,
    DOMAIN,
    PLATFORMS,
    STARTUP_MESSAGE,
    SERVICE_SET_HOLIDAY,
    SERVICE_SET_SCHEDULE_DATA,
    SERVICE_SET_DISINFECTION_START_TIME,
    SERVICE_GET_ENERGY_BALANCE,
    SERVICE_GET_ENERGY_BALANCE_MONTHLY,
    FEATURE_VENT,
    FEATURE_HEATING_CURVE,
    FEATURE_DISINFECTION,
    FEATURE_CODE_GEN
)

_LOGGER: logging.Logger = logging.getLogger(__package__)
SCAN_INTERVAL = timedelta(seconds=60)
CONFIG_SCHEMA = config_val.removed(DOMAIN, raise_if_present=False)


async def async_setup(hass: HomeAssistant, config: dict):  # pylint: disable=unused-argument
    """Set up this integration using YAML is not supported."""
    return True


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    if DOMAIN not in hass.data:
        value = "UNKOWN"
        _LOGGER.info(STARTUP_MESSAGE)
        hass.data.setdefault(DOMAIN, {"manifest_version": value})

    coordinator = WKHPDataUpdateCoordinator(hass, config_entry)
    await coordinator.async_refresh()
    if not coordinator.last_update_success:
        raise ConfigEntryNotReady
    else:
        # here we can do some init stuff (like read all data)...
        pass

    hass.data[DOMAIN][config_entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    service = waterkotte_service.WaterkotteHeatpumpService(hass, config_entry, coordinator)
    hass.services.async_register(DOMAIN, SERVICE_SET_HOLIDAY, service.set_holiday,
                                 supports_response=SupportsResponse.OPTIONAL)
    hass.services.async_register(DOMAIN, SERVICE_SET_SCHEDULE_DATA, service.set_schedule_data,
                                 supports_response=SupportsResponse.OPTIONAL)
    hass.services.async_register(DOMAIN, SERVICE_SET_DISINFECTION_START_TIME, service.set_disinfection_start_time,
                                 supports_response=SupportsResponse.OPTIONAL)
    hass.services.async_register(DOMAIN, SERVICE_GET_ENERGY_BALANCE, service.get_energy_balance,
                                 supports_response=SupportsResponse.ONLY)
    hass.services.async_register(DOMAIN, SERVICE_GET_ENERGY_BALANCE_MONTHLY, service.get_energy_balance_monthly,
                                 supports_response=SupportsResponse.ONLY)

    # we should check (in any CASE!) if the active tags might have...
    asyncio.create_task(coordinator.update_client_tag_list(hass, config_entry.data.get(CONF_ADD_SERIAL_AS_ID,False), config_entry.entry_id))

    # ok we are done...
    config_entry.async_on_unload(config_entry.add_update_listener(entry_update_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    _LOGGER.debug(f"async_unload_entry() called for entry: {config_entry.entry_id}")
    unload_ok = await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS)

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


async def entry_update_listener(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    _LOGGER.debug(f"entry_update_listener() called for entry: {config_entry.entry_id}")
    await hass.config_entries.async_reload(config_entry.entry_id)


@staticmethod
def generate_tag_list(hass: HomeAssistant, trim_unique_id:bool, config_entry_id: str) -> List[WKHPTag]:
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
                    if trim_unique_id:
                        a_temp_tag = a_temp_tag[0:a_temp_tag.rfind('_')]
                    _LOGGER.info(f"found active entity: {entity.entity_id} using Tag: {a_temp_tag.upper()}")
                    if a_temp_tag is not None and a_temp_tag.upper() in WKHPTag.__members__:
                        if WKHPTag[a_temp_tag.upper()]:
                            tags.append(WKHPTag[a_temp_tag.upper()])
                    else:
                        _LOGGER.warning(f"Tag: {a_temp_tag} not found in WKHPTag.__members__ !")
    return tags


class WKHPDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, config_entry):
        self.name = config_entry.title
        self.is_multi_instances = config_entry.data.get(CONF_ADD_SERIAL_AS_ID, False)
        if self.is_multi_instances:
            self.serial_id_addon = config_entry.data.get(CONF_SERIAL, "")

        self._config_entry = config_entry
        self.add_schedule_entities = config_entry.options.get(CONF_ADD_SCHEDULE_ENTITIES,
                                                              config_entry.data.get(CONF_ADD_SCHEDULE_ENTITIES, False))
        self.available_features = []
        if CONF_USE_VENT in config_entry.data and config_entry.data[CONF_USE_VENT]:
            self.available_features.append(FEATURE_VENT)
        if CONF_USE_HEATING_CURVE in config_entry.data and config_entry.data[CONF_USE_HEATING_CURVE]:
            self.available_features.append(FEATURE_HEATING_CURVE)
        if CONF_USE_DISINFECTION in config_entry.data and config_entry.data[CONF_USE_DISINFECTION]:
            self.available_features.append(FEATURE_DISINFECTION)
        _LOGGER.debug(f"available_features: {self.available_features}")

        _host = config_entry.options.get(CONF_HOST, config_entry.data.get(CONF_HOST))
        _user = config_entry.options.get(CONF_USERNAME, config_entry.data.get(CONF_USERNAME, "waterkotte"))
        _pwd = config_entry.options.get(CONF_PASSWORD, config_entry.data.get(CONF_PASSWORD, "waterkotte"))
        _system_type = config_entry.options.get(CONF_SYSTEMTYPE, config_entry.data.get(CONF_SYSTEMTYPE, ECOTOUCH))
        _tags_num = config_entry.options.get(CONF_TAGS_PER_REQUEST, config_entry.data.get(CONF_TAGS_PER_REQUEST, 10))
        _tags = generate_tag_list(hass=hass, trim_unique_id=self.is_multi_instances, config_entry_id=config_entry.entry_id)

        self.bridge = WaterkotteClient(host=_host, username=_user, pwd=_pwd, system_type=_system_type,
                                       web_session=async_get_clientsession(hass), tags=_tags,
                                       tags_per_request=_tags_num, lang=hass.config.language.lower())

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
            "name": NAME,
            "model": config_entry.options.get(CONF_SERIES, config_entry.data.get(CONF_SERIES)),
            "sw_version": f"{fw} BIOS: {bios}",
            "hw_version": config_entry.options.get(CONF_ID, config_entry.data.get(CONF_ID))
        }

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)

    async def update_client_tag_list(self, hass: HomeAssistant, trim_unique_id: bool, entry_id: str):
        _LOGGER.debug(f"rechecking active tags... in 15sec")
        await asyncio.sleep(15)

        _LOGGER.debug(f"rechecking active tags NOW!")
        self.bridge.tags = generate_tag_list(hass, trim_unique_id, entry_id)

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
        except InvalidPasswordException as invalid_pwd:
            _LOGGER.info(f"invalid password for waterkotte! {invalid_pwd}")
            raise UpdateFailed() from invalid_pwd
        except TooManyUsersException as too_many_users:
            _LOGGER.info(f"TooManyUsers response from waterkotte - waiting 30sec and then retry...")
            await asyncio.sleep(30)
            raise UpdateFailed() from too_many_users
        except Exception as other:
            _LOGGER.error(f"unexpected: {other}")
            raise UpdateFailed() from other

    async def async_read_values(self, tags: Sequence[WKHPTag]) -> dict:
        """Get data from the API."""
        ret = await self.bridge.async_read_values(tags)
        return ret

    async def async_write_tags(self, kv_pairs: Collection[Tuple[WKHPTag, Any]]) -> dict:
        """Get data from the API."""
        ret = await self.bridge.async_write_values(kv_pairs)
        return ret

    async def async_write_tag(self, tag: WKHPTag, value, entity: Entity = None):
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
        if description.feature is not None and FEATURE_CODE_GEN == description.feature:
            self.code_generated = True
        else:
            self.code_generated = False
        self._attr_translation_key = description.key.lower()
        self.coordinator = coordinator
        self.entity_description = description

        # check, if the feature should be enabled by default (if activated during setup)
        if not description.entity_registry_enabled_default and description.feature is not None:
            if description.feature in self.coordinator.available_features:
                self._attr_entity_registry_enabled_default = True

        if self.coordinator.is_multi_instances:
            self.entity_id = f"{DOMAIN}.wkh_{self.coordinator.serial_id_addon}_{self._attr_translation_key}"
        else:
            self.entity_id = f"{DOMAIN}.wkh_{self._attr_translation_key}"

    def _name_internal(self, device_class_name: str | None,
                       platform_translations: dict[str, Any], ) -> str | UndefinedType | None:
        if self.code_generated:
            return self._name_internal_code_generated(self._attr_translation_key, platform_translations)
        else:
            return super()._name_internal(device_class_name, platform_translations)

    def _name_internal_code_generated(self, key, platform_translations: dict[str, Any]):
        temp = key.lower().replace('_', ' ')
        temp = temp.replace(' enable', '')
        temp = temp.replace(' value', '')
        a_list = ["schedule", "heating", "cooling", "water", "pool", "solar", "pv",
                  "mix1", "mix2", "mix3", "buffer tank circulation pump", "adjust",
                  "1mo", "2tu", "3we", "4th", "5fr", "6sa", "7su",
                  "start time", "end time"]
        for a_key in a_list:
            f_key = f"component.{self.platform.platform_name}.entity.code_gen.{a_key.replace(' ', '_')}.name"
            if f_key in platform_translations:
                temp = temp.replace(a_key, platform_translations.get(f_key))
            else:
                _LOGGER.warning(f"{a_key} -> {f_key} not found in platform_translations")

        return temp  # .title()

    @property
    def wkhp_tag(self):
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
        if self.coordinator.is_multi_instances:
            return f"{self.entity_description.key}_{self.coordinator.serial_id_addon}"
        else:
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

    def _friendly_name_internal(self) -> str | None:
        """Return the friendly name.

        If has_entity_name is False, this returns self.name
        If has_entity_name is True, this returns device.name + self.name
        """
        name = self.name
        if name is UNDEFINED:
            name = None

        if not self.has_entity_name or not (device_entry := self.device_entry):
            return name

        device_name = device_entry.name_by_user or device_entry.name
        if name is None and self.use_device_name:
            return device_name

        # we overwrite the default impl here and just return our 'name'
        # return f"{device_name} {name}" if device_name else name
        if device_entry.name_by_user is not None:
            return f"{device_entry.name_by_user} {name}" if device_name else name
        else:
            return f"[WKHP] {name}"
