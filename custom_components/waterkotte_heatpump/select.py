import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import HomeAssistantType

from . import WKHPDataUpdateCoordinator, WKHPBaseEntity
from .const import DOMAIN, SELECT_SENSORS, ExtSelectEntityDescription

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistantType, config_entry: ConfigEntry, add_entity_cb: AddEntitiesCallback):
    _LOGGER.debug("SELECT async_setup_entry")
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    entities = []
    for description in SELECT_SENSORS:
        entity = WKHPSelect(coordinator, description)
        entities.append(entity)
    add_entity_cb(entities)


class WKHPSelect(WKHPBaseEntity, SelectEntity):
    def __init__(self, coordinator: WKHPDataUpdateCoordinator, description: ExtSelectEntityDescription):
        super().__init__(coordinator=coordinator, description=description)

    @property
    def current_option(self) -> str | None:
        try:
            value = self.coordinator.data[self.eco_tag]["value"]
            if value is None or value == "":
                value = 'unknown'
        except KeyError:
            value = "unknown"
        except TypeError:
            return None
        return value

    async def async_select_option(self, option: str) -> None:
        try:
            await self.coordinator.async_write_tag(self.eco_tag, option, self)
        except ValueError:
            return "unavailable"
