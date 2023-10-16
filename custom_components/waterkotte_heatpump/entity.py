"""WaterkotteHeatpumpEntity class"""
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo, Entity, EntityDescription
# from homeassistant.config_entries import ConfigEntry
# from .const import ATTRIBUTION
from .const import DOMAIN
# from .const import NAME
# from .const import VERSION

SENSOR_TYPES = []


class WaterkotteHeatpumpEntity(CoordinatorEntity):
    """ WaterkotteHeatpumpEntity Main common Class """

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator)
        self.config_entry = config_entry
        self._attr_device_info = DeviceInfo(identifiers={('DOMAIN', DOMAIN)})

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return self.config_entry.data['serial']
        # return self.config_entry.entry_id

    @property
    def has_entity_name(self) -> bool:
        """Return true."""
        return True

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return {
            # "attribution": ATTRIBUTION,
            "id": str(self.coordinator.data.get("id")),
            "integration": DOMAIN,
        }

class WaterkotteHeatpumpEntity2(Entity):
    _attr_should_poll = False

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
