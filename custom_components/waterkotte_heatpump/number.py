import logging

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.core import HomeAssistant

from . import WKHPDataUpdateCoordinator, WKHPBaseEntity
from .const import DOMAIN, NUMBER_SENSORS, ExtNumberEntityDescription
from .const_gen import NUMBER_SENSORS_GENERATED

_LOGGER = logging.getLogger(__name__)

TEMP_ADJUST_LOOKUP = [-2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2]


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, add_entity_cb: AddEntitiesCallback):
    _LOGGER.debug("NUMBER async_setup_entry")
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    entities = []
    for description in NUMBER_SENSORS:
        entity = WKHPNumber(coordinator, description)
        entities.append(entity)
    if coordinator.add_schedule_entities:
        for description in NUMBER_SENSORS_GENERATED:
            entity = WKHPNumber(coordinator, description)
            entities.append(entity)
    add_entity_cb(entities)


class WKHPNumber(WKHPBaseEntity, NumberEntity):
    def __init__(self, coordinator: WKHPDataUpdateCoordinator, description: ExtNumberEntityDescription):
        super().__init__(coordinator=coordinator, description=description)

    @property
    def native_value(self) -> float | None:
        try:
            value = self.coordinator.data[self.wkhp_tag]["value"]
            if value is None or value == "":
                return "unknown"
            if str(self.wkhp_tag.name).upper().endswith("_ADJUST"):
                value = TEMP_ADJUST_LOOKUP[value]
        except KeyError:
            return "unknown"
        except TypeError:
            return None
        return float(value)

    async def async_set_native_value(self, value: float) -> None:
        try:
            if str(self.wkhp_tag.name).upper().endswith("_ADJUST"):
                value = TEMP_ADJUST_LOOKUP.index(value)
            if self.wkhp_tag[0][0][0] == 'I':
                value = int(value)
            await self.coordinator.async_write_tag(self.wkhp_tag, value, self)
        except ValueError:
            return "unavailable"
