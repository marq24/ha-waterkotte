"""WaterkotteHeatpumpEntity class"""
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
# from homeassistant.config_entries import ConfigEntry
# from .const import ATTRIBUTION
from .const import DOMAIN
# from .const import NAME
# from .const import VERSION

SENSOR_TYPES = []


class WaterkotteHeatpumpEntity(CoordinatorEntity):
    """ WaterkotteHeatpumpEntity Main common Class """

    def __init__(self, coordinator, config_entry):
        self.config_entry = config_entry
        self._attr_device_info = DeviceInfo(identifiers={('DOMAIN', DOMAIN)})
        super().__init__(coordinator)

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
