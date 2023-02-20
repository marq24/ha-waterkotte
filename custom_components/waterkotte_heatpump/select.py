"""Sensor platform for Waterkotte Heatpump."""
import logging
# from homeassistant.helpers.entity import Entity, EntityCategory  # , DeviceInfo
from homeassistant.components.select import SelectEntity
from homeassistant.helpers.typing import ConfigType, HomeAssistantType

from custom_components.waterkotte_heatpump.mypywaterkotte.ecotouch import EcotouchTag
from .entity import WaterkotteHeatpumpEntity

from .const import ENUM_OFFAUTOMANUAL, DEVICE_CLASS_ENUM, DOMAIN

_LOGGER = logging.getLogger(__name__)
_LANG = None

# Sensor types are defined as:
#   variable -> [0]title, [1] EcoTouchTag, [2]device_class, [3]units, [4]icon, [5]enabled_by_default, [6]options, [7]entity_category #pylint: disable=line-too-long
SENSOR_TYPES = {
    "enable_cooling": [
        "Enable Cooling",
        EcotouchTag.ENABLE_COOLING,
        DEVICE_CLASS_ENUM,
        None,
        "mdi:snowflake-thermometer",
        True,
        ENUM_OFFAUTOMANUAL,
        None,
    ],
    "enable_heating": [
        "Enable Heating",
        EcotouchTag.ENABLE_HEATING,
        DEVICE_CLASS_ENUM,
        None,
        "mdi:radiator",
        True,
        ENUM_OFFAUTOMANUAL,
        None,
    ],
    "enable_pv": [
        "Enable PV",
        EcotouchTag.ENABLE_PV,
        DEVICE_CLASS_ENUM,
        None,
        "mdi:solar-power",
        False,
        ENUM_OFFAUTOMANUAL,
        None,
    ],
    "enable_warmwater": [
        "Enable Warmwater",
        EcotouchTag.ENABLE_WARMWATER,
        DEVICE_CLASS_ENUM,
        None,
        "mdi:water-thermometer",
        True,
        ENUM_OFFAUTOMANUAL,
        None,
    ],
}

async def async_setup_entry(hass: HomeAssistantType, entry: ConfigType, async_add_devices) -> None:
    """Set up the Waterkotte Select platform."""
    _LOGGER.debug("Select async_setup_entry")
    coordinator = hass.data[DOMAIN][entry.entry_id]
    global _LANG
    _LANG = coordinator.lang
    async_add_devices([WaterkotteHeatpumpSelect(entry, coordinator, sensor_type)
                       for sensor_type in SENSOR_TYPES])


class WaterkotteHeatpumpSelect(SelectEntity, WaterkotteHeatpumpEntity):
    """waterkotte_heatpump Sensor class."""

    def __init__(self, entry, hass_data, sensor_type):  # pylint: disable=unused-argument
        """Initialize the sensor."""
        self._coordinator = hass_data

        self._type = sensor_type
        # self._name = f"{SENSOR_TYPES[self._type][0]} {DOMAIN}"
        self._name = f"{SENSOR_TYPES[self._type][0]}"
        # self._unique_id = f"{SENSOR_TYPES[self._type][0]}_{DOMAIN}"
        self._unique_id = self._type
        self._entry_data = entry.data
        self._device_id = entry.entry_id
        hass_data.alltags.update({self._unique_id: SENSOR_TYPES[self._type][1]})
        super().__init__(hass_data, entry)

    @ property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def current_option(self) -> str | None:
        try:
            sensor = SENSOR_TYPES[self._type]
            value = self._coordinator.data[sensor[1]]["value"]
            if value is None or value == "":
                value = 'unknown'
        except KeyError:
            value = "unknown"
        except TypeError:
            return None
        return value
        # return "auto"

    @property
    def options(self) -> list[str]:
        # return ["off", "auto", "manual"]
        return SENSOR_TYPES[self._type][6]

    async def async_select_option(self, option: str) -> None:  # pylint: disable=unused-argument
        """Turn on the switch."""
        try:
            # print(option)
            # await self._coordinator.api.async_write_value(SENSOR_TYPES[self._type][1], option)
            await self._coordinator.async_write_tag(SENSOR_TYPES[self._type][1], option)
        except ValueError:
            return "unavailable"

    @property
    def tag(self):
        """Return a unique ID to use for this entity."""
        return SENSOR_TYPES[self._type][1]

    @ property
    def device_class(self):
        """Return the device class of the sensor."""
        return SENSOR_TYPES[self._type][2]

    @ property
    def icon(self):
        """Return the icon of the sensor."""
        return SENSOR_TYPES[self._type][4]
        # return ICON

    @ property
    def entity_registry_enabled_default(self):
        """Return the entity_registry_enabled_default of the sensor."""
        return SENSOR_TYPES[self._type][5]

    @ property
    def entity_category(self):
        """Return the unit of measurement."""
        try:
            return SENSOR_TYPES[self._type][7]
        except IndexError:
            return None

    @ property
    def unique_id(self):
        """Return the unique of the sensor."""
        return self._unique_id

    @ property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return SENSOR_TYPES[self._type][3]

    async def async_update(self):
        """Schedule a custom update via the common entity update service."""
        await self._coordinator.async_request_refresh()

    @ property
    def should_poll(self) -> bool:
        """Entities do not individually poll."""
        return False
