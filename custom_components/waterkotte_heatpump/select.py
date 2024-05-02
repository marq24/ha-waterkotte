import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.core import HomeAssistant

from . import WKHPDataUpdateCoordinator, WKHPBaseEntity
from .const import DOMAIN, SELECT_SENSORS, ExtSelectEntityDescription
from .const_gen import SELECT_SENSORS_GENERATED

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, add_entity_cb: AddEntitiesCallback):
    _LOGGER.debug("SELECT async_setup_entry")
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    entities = []
    for description in SELECT_SENSORS:
        entity = WKHPSelect(coordinator, description)
        entities.append(entity)
    if coordinator.add_schedule_entities:
        for description in SELECT_SENSORS_GENERATED:
            entity = WKHPSelect(coordinator, description)
            entities.append(entity)
    add_entity_cb(entities)


class WKHPSelect(WKHPBaseEntity, SelectEntity):
    def __init__(self, coordinator: WKHPDataUpdateCoordinator, description: ExtSelectEntityDescription):
        super().__init__(coordinator=coordinator, description=description)

    @property
    def current_option(self) -> str | None:
        try:
            value = self.coordinator.data[self.wkhp_tag]["value"]
            if value is None or value == "":
                value = 'unknown'
        except KeyError:
            value = "unknown"
        except TypeError:
            return None
        return value

    async def async_select_option(self, option: str) -> None:
        try:
            await self.coordinator.async_write_tag(self.wkhp_tag, option, self)
        except ValueError:
            return "unavailable"
