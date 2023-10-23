"""WaterkotteHeatpumpEntity class"""
import logging

from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo, Entity, EntityDescription
from .const import DOMAIN, CONF_SERIAL

SENSOR_TYPES = []
_LOGGER = logging.getLogger(__name__)


class WaterkotteHeatpumpEntity(CoordinatorEntity):
    """ WaterkotteHeatpumpEntity Main common Class """

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator)
        self.config_entry = config_entry
        self._attr_device_info = DeviceInfo(identifiers={('DOMAIN', DOMAIN)})

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return self.config_entry.data[CONF_SERIAL]
        # return self.config_entry.entry_id

    @property
    def has_entity_name(self) -> bool:
        """Return true."""
        return True

    # 1. renamed from 'device_state_attributes' to 'extra_state_attributes'
    # 2. replaced self.coordinator.data.get("id") with config_entry source - since there is no 'id' in the data!
    # 3. completely removed (by marq24) - IMHO nobody needs additional attributes for the sensors that is static!
    # @property
    # def extra_state_attributes(self):
    #    return {
    #        # "attribution": ATTRIBUTION,
    #        "id": str(self.config_entry.data[CONF_ID]),
    #        "integration": DOMAIN,
    #    }


class WaterkotteHeatpumpEntity2(Entity):
    _attr_should_poll = False
    _attr_has_entity_name = True

    def __init__(self, coordinator, description: EntityDescription) -> None:
        self.coordinator = coordinator
        self.entity_description = description
        self._stitle = coordinator._config_entry.title
        self._state = None

        self._attr_device_info = DeviceInfo(identifiers={('DOMAIN', DOMAIN)})

    @property
    def available(self):
        """Return True if entity is available."""
        return self.coordinator.last_update_success

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        sensor = self.entity_description.key
        return f"{self._stitle}_{sensor}"

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
