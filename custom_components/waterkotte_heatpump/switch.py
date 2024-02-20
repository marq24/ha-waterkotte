import logging
from typing import Literal

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_ON, STATE_OFF
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import HomeAssistantType

from . import WKHPDataUpdateCoordinator, WKHPBaseEntity
from .const import DOMAIN, SWITCH_SENSORS, ExtSwitchEntityDescription

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistantType, config_entry: ConfigEntry, add_entity_cb: AddEntitiesCallback):
    _LOGGER.debug("SWITCH async_setup_entry")
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    entities = []
    for description in SWITCH_SENSORS:
        entity = WKHPSwitch(coordinator, description)
        entities.append(entity)
    add_entity_cb(entities)


class WKHPSwitch(WKHPBaseEntity, SwitchEntity):
    def __init__(self, coordinator: WKHPDataUpdateCoordinator, description: ExtSwitchEntityDescription):
        super().__init__(coordinator=coordinator, description=description)
        self._attr_icon_off = self.entity_description.icon_off

    async def async_turn_on(self, **kwargs):
        """Turn on the switch."""
        try:
            await self.coordinator.async_write_tag(self.eco_tag, True, self)
            return self.coordinator.data[self.eco_tag]["value"]
        except ValueError:
            return "unavailable"

    async def async_turn_off(self, **kwargs):
        """Turn off the switch."""
        try:
            await self.coordinator.async_write_tag(self.eco_tag, False, self)
            return self.coordinator.data[self.eco_tag]["value"]
        except ValueError:
            return "unavailable"

    @property
    def is_on(self) -> bool | None:
        try:
            value = None
            if self.eco_tag in self.coordinator.data:
                value_and_state = self.coordinator.data[self.eco_tag]
                # _LOGGER.error(f"{self.entity_description.key} -> {value_and_state}")
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
            _LOGGER.warning(f"is_on caused KeyError for: {self.entity_description.key}")
            value = None
        except TypeError:
            return None
        return value

    @property
    def state(self) -> Literal["on", "off"] | None:
        """Return the state."""
        if (is_on := self.is_on) is None:
            return None
        return STATE_ON if is_on else STATE_OFF

    @property
    def icon(self):
        """Return the icon of the sensor."""
        if self._attr_icon_off is not None and self.state == STATE_OFF:
            return self._attr_icon_off
        else:
            return super().icon
