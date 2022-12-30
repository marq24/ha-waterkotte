"""Sensor platform for Waterkotte Heatpump."""
import logging
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import ConfigType, HomeAssistantType

# from .const import DEFAULT_NAME


# from .const import ICON
# from .const import SENSOR

#  from .const import UnitOfTemperature
# from .entity import WaterkotteHeatpumpEntity

from homeassistant.const import (
    #    ATTR_ATTRIBUTION,
    DEGREE,
    #    DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_PRESSURE,
    DEVICE_CLASS_TEMPERATURE,
    #    LENGTH_KILOMETERS,
    PRESSURE_HPA,
    SPEED_KILOMETERS_PER_HOUR,
    TEMP_CELSIUS,
    #    TIME_SECONDS,
)

from .pywaterkotte.ecotouch import EcotouchTag
from .const import ENUM_ONOFFAUTO, DEVICE_CLASS_ENUM, DOMAIN

_LOGGER = logging.getLogger(__name__)


# Sensor types are defined as:
#   variable -> [0]title, [1]device_class, [2]units, [3]icon, [4]disabled_by_default, [5]options
SENSOR_TYPES = {
    "enable_cooling": [
        "enable_cooling",
        DEVICE_CLASS_ENUM,
        None,
        "mdi:snowflake-thermometer",
        True,
        ENUM_ONOFFAUTO,
    ],
    "enable_heating": [
        "Enable Heating",
        DEVICE_CLASS_ENUM,
        None,
        "mdi:weather-partly-cloudy",
        True,
        ENUM_ONOFFAUTO,
    ],
    "enable_pv": [
        "Enable PV",
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:solar-power",
        True,
    ],
    "enable_warmwater": [
        "Enable Warmwater",
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:water-thermometer",
        True,
    ],
    "state_water": ["State Water", DEVICE_CLASS_PRESSURE, PRESSURE_HPA, None, False],
    "state_cooling": [
        "State Cooling",
        None,
        SPEED_KILOMETERS_PER_HOUR,
        "mdi:snowflake-thermometer",
        True,
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
        True,
    ],
    "status_water": ["Status Water", None, "kg/m^2", "mdi:weather-rainy", True],
    "status_cooling": [
        "Status Cooling",
        None,
        "%",
        "mdi:weather-rainy",
        True,
    ],
    "temperature_outside": [
        "Temperature Outside",
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        True,
    ],
    "temperature_outside_1h": [
        "Temperature Outside 1h",
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        True,
    ],
    "temperature_outside_24h": [
        "Temperature Outside 24h",
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        True,
    ],
    "temperature_source_in": [
        "Temperature Source In",
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        True,
    ],
    "temperature_source_out": [
        "Temperature Source Out",
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        True,
    ],
    "temperature_evaporation": [
        "Temperature Evaporation",
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        True,
    ],
    "temperature_suction": [
        "Temperature Suction",
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        True,
    ],
    "temperature_return_set": [
        "Temperature Return Set",
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        True,
    ],
    "temperature_return": [
        "Temperature Return",
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        True,
    ],
    "temperature_flow": [
        "Temperature Flow",
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        True,
    ],
    "temperature_condensation": [
        "Temperature Condensation",
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        True,
    ],
    "temperature_storage": [
        "Temperature Storage",
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        True,
    ],
    "temperature_room": [
        "Temperature Room",
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        False,
    ],
    "temperature_room_1h": [
        "Temperature Room 1h",
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        False,
    ],
    "temperature_water": [
        "Temperature Water",
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        True,
    ],
    "temperature_pool": [
        "Temperature Pool",
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        False,
    ],
    "temperature_solar": [
        "Temperature Solar",
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        False,
    ],
    "temperature_solar_flow": [
        "Temperature Solar Flow",
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        False,
    ],
}


"""
    PRESSURE_EVAPORATION = TagData(["A8"], "bar")
    PRESSURE_CONDENSATION = TagData(["A15"], "bar")
    POSITION_EXPANSION_VALVE = TagData(["A23"], "?°C") """

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

    def __init__(self, entry_data, hass_data, sensor_type):  # pylint: disable=unused-argument
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
        # print(self._coordinator.data)
        try:
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
            elif self._type == "temperature_outside":
                result = self._coordinator.data[EcotouchTag.TEMPERATURE_OUTSIDE]["value"]
            elif self._type == "temperature_outside_1h":
                result = self._coordinator.data[EcotouchTag.TEMPERATURE_OUTSIDE_1H]["value"]
            elif self._type == "temperature_outside_24h":
                result = self._coordinator.data[EcotouchTag.TEMPERATURE_OUTSIDE_24H][
                    "value"
                ]
            elif self._type == "temperature_source_in":
                result = self._coordinator.data[EcotouchTag.TEMPERATURE_SOURCE_IN]["value"]
            elif self._type == "temperature_source_out":
                result = self._coordinator.data[EcotouchTag.TEMPERATURE_SOURCE_OUT]["value"]
            elif self._type == "temperature_evaporation":
                result = self._coordinator.data[EcotouchTag.TEMPERATURE_EVAPORATION][
                    "value"
                ]
            elif self._type == "temperature_suction":
                result = self._coordinator.data[EcotouchTag.TEMPERATURE_SUCTION]["value"]
            elif self._type == "temperature_return_set":
                result = self._coordinator.data[EcotouchTag.TEMPERATURE_RETURN_SET]["value"]
            elif self._type == "temperature_return":
                result = self._coordinator.data[EcotouchTag.TEMPERATURE_RETURN]["value"]
            elif self._type == "temperature_flow":
                result = self._coordinator.data[EcotouchTag.TEMPERATURE_FLOW]["value"]
            elif self._type == "temperature_condenstation":
                result = self._coordinator.data[EcotouchTag.TEMPERATURE_CONDENSATION][
                    "value"
                ]
            elif self._type == "temperature_storage":
                result = self._coordinator.data[EcotouchTag.TEMPERATURE_STORAGE]["value"]
            elif self._type == "temperature_room":
                result = self._coordinator.data[EcotouchTag.TEMPERATURE_ROOM]["value"]
            elif self._type == "temperature_room_1h":
                result = self._coordinator.data[EcotouchTag.TEMPERATURE_ROOM_1H]["value"]
            elif self._type == "temperature_water":
                result = self._coordinator.data[EcotouchTag.TEMPERATURE_WATER]["value"]
            elif self._type == "temperature_solar":
                result = self._coordinator.data[EcotouchTag.TEMPERATURE_SOLAR]["value"]
            elif self._type == "temperature_sloar_flow":
                result = self._coordinator.data[EcotouchTag.TEMPERATURE_SOLAR_FLOW]["value"]
            else:
                result = "unavailable"
            if result is True:
                result = "on"
            elif result is False:
                result = "off"
        except KeyError:
            return "unavailable"
        return result

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return SENSOR_TYPES[self._type][3]
        # return ICON

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return SENSOR_TYPES[self._type][1]

    @property
    def entity_registry_enabled_default(self):
        """Return the entity_registry_enabled_default of the sensor."""
        return SENSOR_TYPES[self._type][4]

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
