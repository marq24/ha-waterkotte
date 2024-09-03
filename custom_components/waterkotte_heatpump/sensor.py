import logging
from datetime import datetime, time

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity
from . import WKHPDataUpdateCoordinator, WKHPBaseEntity
from .const import DOMAIN, SENSOR_SENSORS, ExtSensorEntityDescription
from .const_gen import SENSOR_SENSORS_GENERATED

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, add_entity_cb: AddEntitiesCallback):
    _LOGGER.debug("SENSOR async_setup_entry")
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    entities = []
    for description in SENSOR_SENSORS:
        entity = WKHPSensor(coordinator, description)
        entities.append(entity)
    if coordinator.add_schedule_entities:
        for description in SENSOR_SENSORS_GENERATED:
            entity = WKHPSensor(coordinator, description)
            entities.append(entity)
    add_entity_cb(entities)


class WKHPSensor(WKHPBaseEntity, SensorEntity, RestoreEntity):
    def __init__(self, coordinator: WKHPDataUpdateCoordinator, description: ExtSensorEntityDescription):
        super().__init__(coordinator=coordinator, description=description)

        # if description.device_class is not None and description.device_class.SensorDeviceClass.DATE:
        #     if description.tag == WKHPTag.SCHEDULE_WATER_DISINFECTION_START_TIME:
        #         self._attr_native_value = time
        #     else:
        #         self._attr_native_value = datetime

    #        self._previous_float_value: float | None = None
    #        self._is_total_increasing: bool = description is not None and isinstance(description,
    #                                                                                 ExtSensorEntityDescription) and hasattr(
    #            description, "controls") and description.controls is not None and "only_increasing" in description.controls

    @property
    def _is_bit_field(self) -> bool:
        return self.entity_description.key == "ALARM_BITS" or self.entity_description.key == "INTERRUPTION_BITS"

    @property
    def state(self):
        # for SensorDeviceClass.DATE we will use out OWN 'state' render impl!!!
        if self.entity_description.device_class == SensorDeviceClass.DATE:
            value = self.native_value
            if value is None:
                value = "unknown"
            return  value
        else:
            return SensorEntity.state.fget(self)

    @property
    def native_value(self):
        """Return the state of the sensor."""
        try:
            value = self.coordinator.data[self.wkhp_tag]["value"]
            if value is None or len(str(value)) == 0:
                if self._is_bit_field:
                    value = "none"
                else:
                    value = None
            else:
                if isinstance(value, datetime):
                    return value.isoformat(sep=' ', timespec="minutes")
                elif isinstance(value, time):
                    return value.isoformat(timespec="minutes")
                elif isinstance(value, bool):
                    if value is True:
                        value = "on"
                    elif value is False:
                        value = "off"

        except (KeyError, TypeError):
            value = None

        # final return statement...
        return value

    @property
    def entity_category(self):
        if self._is_bit_field:
            return EntityCategory.DIAGNOSTIC
        elif self.entity_description.entity_category is not None:
            return self.entity_description.entity_category
        return None
