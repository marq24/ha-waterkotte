import logging
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import HomeAssistantType

from . import WKHPDataUpdateCoordinator, WKHPBaseEntity
from .const import DOMAIN, BINARY_SENSORS, ExtBinarySensorEntityDescription

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistantType, config_entry: ConfigEntry, add_entity_cb: AddEntitiesCallback):
    _LOGGER.debug("BINARY_SENSOR async_setup_entry")
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    entities = []
    for description in BINARY_SENSORS:
        entity = WKHPBinarySensor(coordinator, description)
        entities.append(entity)
    add_entity_cb(entities)


class WKHPBinarySensor(WKHPBaseEntity, BinarySensorEntity):
    def __init__(self, coordinator: WKHPDataUpdateCoordinator, description: ExtBinarySensorEntityDescription):
        super().__init__(coordinator=coordinator, description=description)

    @property
    def is_on(self) -> bool | None:
        try:
            value = None
            if self.eco_tag in self.coordinator.data:
                value_and_state = self.coordinator.data[self.eco_tag]
                if "value" in value_and_state:
                    value = value_and_state["value"]
                else:
                    _LOGGER.debug(
                        f"is_on: for {self.entity_description.key} could not read value from data: {value_and_state}")
            else:
                if len(self.coordinator.data) > 0:
                    _LOGGER.debug(
                        f"is_on: for {self.entity_description.key} not found in data: {len(self.coordinator.data)}")
            if value is None or value == "":
                value = None

        except KeyError:
            _LOGGER.warning(f"is_on caused KeyError for: {self._type}")
            value = None
        except TypeError:
            return None

        if not isinstance(value, bool):
            if isinstance(value, str):
                # parse anything else then 'on' to False!
                if value.lower() == 'on':
                    value = True
                else:
                    value = False
            else:
                value = False

        return value

    @property
    def icon(self):
        ret = super().icon;

        if ret is not None:
            return ret
        else:
            if self.is_on:
                match self.entity_description.key:
                    case "STATE_HEATING_CIRCULATION_PUMP_D425" | \
                         "STATE_BUFFERTANK_CIRCULATION_PUMP_D377" | \
                         "STATE_POOL_CIRCULATION_PUMP_D549" | \
                         "STATE_MIX1_CIRCULATION_PUMP_D248" | \
                         "STATE_MIX2_CIRCULATION_PUMP_D291" | \
                         "STATE_MIX3_CIRCULATION_PUMP_D334" | \
                         "STATUS_HEATING_CIRCULATION_PUMP" | \
                         "STATUS_SOLAR_CIRCULATION_PUMP" | \
                         "STATUS_BUFFER_TANK_CIRCULATION_PUMP":
                        return "mdi:pump"
                    case _:
                        return None
            else:
                match self.entity_description.key:
                    case "STATE_HEATING_CIRCULATION_PUMP_D425" | \
                         "STATE_BUFFERTANK_CIRCULATION_PUMP_D377" | \
                         "STATE_POOL_CIRCULATION_PUMP_D549" | \
                         "STATE_MIX1_CIRCULATION_PUMP_D248" | \
                         "STATE_MIX2_CIRCULATION_PUMP_D291" | \
                         "STATE_MIX3_CIRCULATION_PUMP_D334" | \
                         "STATUS_HEATING_CIRCULATION_PUMP" | \
                         "STATUS_SOLAR_CIRCULATION_PUMP" | \
                         "STATUS_BUFFER_TANK_CIRCULATION_PUMP":
                        return "mdi:pump-off"
                    case _:
                        return None
