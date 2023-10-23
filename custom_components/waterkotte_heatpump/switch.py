"""Switch platform for Waterkotte Heatpump."""
import logging
from homeassistant.components.switch import SwitchEntity

from custom_components.waterkotte_heatpump.pywaterkotte_ha.ecotouch import EcotouchTag
from .const import DOMAIN

from .entity import WaterkotteHeatpumpEntity

_LOGGER = logging.getLogger(__name__)

# Sensor types are defined as:
#   variable -> [0]title, [1] EcoTouchTag, [2]device_class, [3]units, [4]icon, [5]enabled_by_default, [6]options, [7]entity_category  #pylint: disable=line-too-long
SENSOR_TYPES = {
    "HOLIDAY_ENABLED": [
        "Holiday Mode",
        EcotouchTag.HOLIDAY_ENABLED,
        None,
        None,
        None,
        True,
        None,
        None,
    ],
    "SCHEDULE_WATER_DISINFECTION_1MO": [
        "Water disinfection day 1 - Monday",
        EcotouchTag.SCHEDULE_WATER_DISINFECTION_1MO,
        None,
        None,
        "mdi:calendar-today",
        False,
        None,
        None,
    ],
    "SCHEDULE_WATER_DISINFECTION_2TU": [
        "Water disinfection day 2 - Tuesday",
        EcotouchTag.SCHEDULE_WATER_DISINFECTION_2TU,
        None,
        None,
        "mdi:calendar-today",
        False,
        None,
        None,
    ],
    "SCHEDULE_WATER_DISINFECTION_3WE": [
        "Water disinfection day 3 - Wednesday",
        EcotouchTag.SCHEDULE_WATER_DISINFECTION_3WE,
        None,
        None,
        "mdi:calendar-today",
        False,
        None,
        None,
    ],
    "SCHEDULE_WATER_DISINFECTION_4TH": [
        "Water disinfection day 4 - Thursday",
        EcotouchTag.SCHEDULE_WATER_DISINFECTION_4TH,
        None,
        None,
        "mdi:calendar-today",
        False,
        None,
        None,
    ],
    "SCHEDULE_WATER_DISINFECTION_5FR": [
        "Water disinfection day 5 - Friday",
        EcotouchTag.SCHEDULE_WATER_DISINFECTION_5FR,
        None,
        None,
        "mdi:calendar-today",
        False,
        None,
        None,
    ],
    "SCHEDULE_WATER_DISINFECTION_6SA": [
        "Water disinfection day 6 - Saturday",
        EcotouchTag.SCHEDULE_WATER_DISINFECTION_6SA,
        None,
        None,
        "mdi:calendar-today",
        False,
        None,
        None,
    ],
    "SCHEDULE_WATER_DISINFECTION_7SU": [
        "Water disinfection day 7 - Sunday",
        EcotouchTag.SCHEDULE_WATER_DISINFECTION_7SU,
        None,
        None,
        "mdi:calendar-today",
        False,
        None,
        None,
    ],
}


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup the Waterkotte Switch platform."""
    _LOGGER.debug("Switch async_setup_entry")
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices([WaterkotteHeatpumpSwitch(entry, coordinator, sensor_type)
                       for sensor_type in SENSOR_TYPES])


class WaterkotteHeatpumpSwitch(WaterkotteHeatpumpEntity, SwitchEntity):
    """waterkotte_heatpump switch class."""

    def __init__(self, entry, hass_data, sensor_type):  # pylint: disable=unused-argument
        """Initialize the sensor."""
        self.entity_id = f"{DOMAIN}.wkh_{sensor_type}"
        self._coordinator = hass_data
        self._type = sensor_type
        self._attr_unique_id = sensor_type
        self._entry_data = entry.data
        self._device_id = entry.entry_id
        self._attr_translation_key = self._type.lower()
        super().__init__(hass_data, entry)

    def __del__(self):
        try:
            del self._coordinator[self._attr_unique_id]
        except Exception:  # pylint: disable=broad-except
            pass

    async def async_turn_on(self, **kwargs):  # pylint: disable=unused-argument
        """Turn on the switch."""
        try:
            await self._coordinator.async_write_tag(self.eco_tag, True)
            return self._coordinator.data[self.eco_tag]["value"]
        except ValueError:
            return "unavailable"

    async def async_turn_off(self, **kwargs):  # pylint: disable=unused-argument
        """Turn off the switch."""
        try:
            await self._coordinator.async_write_tag(self.eco_tag, False)
            return self._coordinator.data[self.eco_tag]["value"]
        except ValueError:
            return "unavailable"

    @property
    def is_on(self) -> bool | None:
        try:
            value = None
            if self.eco_tag in self._coordinator.data:
                value_and_state = self._coordinator.data[self.eco_tag]
                if "value" in value_and_state:
                    value = value_and_state["value"]
                else:
                    _LOGGER.info(f"is_on: for {self._type} could not read value from data: {value_and_state}")
            else:
                _LOGGER.info(f"is_on: for {self._type} could not be found in available data: {self._coordinator.data}")
            if value is None or value == "":
                value = None
        except KeyError:
            _LOGGER.warning(f"is_on caused KeyError for: {self._type}")
            value = None
        except TypeError:
            return None
        return value

    @property
    def eco_tag(self):
        """Return a unique ID to use for this entity."""
        return SENSOR_TYPES[self._type][1]

    @property
    def icon(self):
        """Return the icon of the sensor."""
        if SENSOR_TYPES[self._type][4] is None:
            try:
                if (self._type == "holiday_enabled" and self.eco_tag in self._coordinator.data):
                    if self._coordinator.data[self.eco_tag]["value"] is True:
                        return "mdi:calendar-check"
                    else:
                        return "mdi:calendar-blank"
                else:
                    return None
            except KeyError:
                _LOGGER.warning(
                    f"KeyError in switch.icon: should have value? data:{self._coordinator.data[self.eco_tag]}")
            except TypeError:
                return None
        return SENSOR_TYPES[self._type][4]
        # return ICON

    # @property
    # def is_on(self):
    #     """Return true if the switch is on."""
    #     return self.coordinator.data.get("title", "") == "foo"

    @property
    def entity_registry_enabled_default(self):
        """Return the entity_registry_enabled_default of the sensor."""
        return SENSOR_TYPES[self._type][5]

    @property
    def unique_id(self):
        """Return the unique of the sensor."""
        return self._attr_unique_id
