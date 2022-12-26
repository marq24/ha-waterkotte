"""Sensor platform for Waterkotte Heatpump."""
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import ConfigType, HomeAssistantType

from .const import DEFAULT_NAME
from .const import DOMAIN
from .const import ICON
from .const import SENSOR
from .entity import WaterkotteHeatpumpEntity
import logging
from .pywaterkotte.ecotouch import EcotouchTag
from homeassistant.const import (
    ATTR_ATTRIBUTION,
    DEGREE,
    DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_PRESSURE,
    DEVICE_CLASS_TEMPERATURE,
    LENGTH_KILOMETERS,
    PRESSURE_HPA,
    SPEED_KILOMETERS_PER_HOUR,
    TEMP_CELSIUS,
    TIME_SECONDS,
)

_LOGGER = logging.getLogger(__name__)


# Sensor types are defined as:
#   variable -> [0]title, [1]device_class, [2]units, [3]icon, [4]enabled_by_default
SENSOR_TYPES = {
    "enable_cooling": [
        "enable_cooling",
        None,
        None,
        "mdi:weather-partly-cloudy",
        False,
    ],
    "enable_heating": [
        "Enable Heating",
        None,
        None,
        "mdi:weather-partly-cloudy",
        False,
    ],
    "enable_pv": [
        "Enable PV",
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:temperature-celsius",
        False,
    ],
    "enable_warmwater": [
        "Enable Warmwater",
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:temperature-celsius",
        False,
    ],
    "state_water": ["State Water", DEVICE_CLASS_PRESSURE, PRESSURE_HPA, None, False],
    "state_cooling": [
        "State Cooling",
        None,
        SPEED_KILOMETERS_PER_HOUR,
        "mdi:weather-windy",
        False,
    ],
    "state_sourcepumpe": [
        "State Source Pump",
        None,
        DEGREE,
        "mdi:compass-outline",
        False,
    ],
    "status_heating": [
        "Status Heating",
        None,
        SPEED_KILOMETERS_PER_HOUR,
        "mdi:weather-windy",
        False,
    ],
    "status_water": ["Status Water", None, "kg/m^2", "mdi:weather-rainy", False],
    "status_cooling": [
        "Status Cooling",
        None,
        "%",
        "mdi:weather-rainy",
        False,
    ],
}


# async def async_setup_entry(hass, entry, async_add_devices):
#    """Setup sensor platform."""
#    coordinator = hass.data[DOMAIN][entry.entry_id]
#    async_add_devices([WaterkotteHeatpumpSensor(coordinator, entry)])


async def async_setup_entry(
    hass: HomeAssistantType, entry: ConfigType, async_add_entities
) -> None:
    """Set up the Waterkotte sensor platform."""
    hass_data = hass.data[DOMAIN][entry.entry_id]
    _LOGGER.debug("Sensor async_setup_entry")
    # coordinator = hass.data[DOMAIN][entry.entry_id]
    # async_add_devices([WaterkotteHeatpumpSensor(coordinator, entry)])

    async_add_entities(
        [
            WaterkotteHeatpumpSensor(entry.data, hass_data, sensor_type)
            for sensor_type in SENSOR_TYPES
        ],
        False,
    )


# class WaterkotteHeatpumpSensor(WaterkotteHeatpumpEntity):
class WaterkotteHeatpumpSensor(Entity):
    """waterkotte_heatpump Sensor class."""

    def __init__(self, entry_data, hass_data, sensor_type):
        """Initialize the sensor."""
        # self._connector = hass_data[DWDWEATHER_DATA]
        self._coordinator = hass_data

        self._type = sensor_type
        self._name = f"{SENSOR_TYPES[self._type][0]} {DOMAIN}"
        self._unique_id = f"{SENSOR_TYPES[self._type][0]}_{DOMAIN}"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        result = ""
        print(self._coordinator.data)
        if self._type == "enable_heating":
            result = self._coordinator.data[EcotouchTag.ENABLE_HEATING]["value"]
        elif self._type == "enable_cooling":
            result = self._coordinator.data[EcotouchTag.ENABLE_COOLING]["value"]
        elif self._type == "enable_warmwater":
            result = self._coordinator.data[EcotouchTag.ENABLE_WARMWATER]["value"]
        elif self._type == "enable_pv":
            result = self._coordinator.data[EcotouchTag.ENABLE_PV]["value"]
        elif self._type == "state_cooling":
            result = self._coordinator.data[EcotouchTag.STATE_COOLING]["value"]
        elif self._type == "state_sourcepump":
            result = self._coordinator.data[EcotouchTag.STATE_SOURCEPUMP]["value"]
        elif self._type == "state_water":
            result = self._coordinator.data[EcotouchTag.STATE_WATER]["value"]
        elif self._type == "status_cooling":
            result = self._coordinator.data[EcotouchTag.STATUS_COOLING]["value"]
        elif self._type == "status_heating":
            result = self._coordinator.data[EcotouchTag.STATUS_HEATING]["value"]
        elif self._type == "status_water":
            result = self._coordinator.data[EcotouchTag.STATUS_WATER]["value"]
        else:
            result = "missing"
        return result

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return ICON

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return SENSOR_TYPES[self._type][1]

    @property
    def unique_id(self):
        """Return the unique of the sensor."""
        return self._unique_id

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return SENSOR_TYPES[self._type][2]

    async def async_update(self):
        """Schedule a custom update via the common entity update service."""
        await self._coordinator.async_request_refresh()

    @property
    def should_poll(self) -> bool:
        """Entities do not individually poll."""
        return False
