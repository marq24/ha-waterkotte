"""Sensor platform for Waterkotte Heatpump."""
import logging

# from homeassistant.helpers.entity import Entity, EntityCategory  # , DeviceInfo
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.typing import ConfigType, HomeAssistantType

from homeassistant.const import (
    DEVICE_CLASS_DATE,
    DEVICE_CLASS_POWER_FACTOR,
    PERCENTAGE,
    DEVICE_CLASS_PRESSURE,
    PRESSURE_BAR,
    DEVICE_CLASS_POWER,
    POWER_KILO_WATT,
)

from homeassistant.components.sensor import (
    SensorStateClass,
)

from custom_components.waterkotte_heatpump.mypywaterkotte.xecotouch import Ecotouch2Tag
from .entity import WaterkotteHeatpumpEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Sensor types are defined as:
#   variable -> [0]title, [1] EcoTouchTag, [2]device_class, [3]units, [4]icon, [5]enabled_by_default, [6]options, [7]entity_category #pylint: disable=line-too-long
SENSOR_TYPES = {
    # status sensors
    "STATUS_HEATING": [
        "Status Heating",
        Ecotouch2Tag.STATUS_HEATING,
        None,
        None,
        "mdi:sun-thermometer",
        True,
        None,
        None,
    ],
    "STATUS_WATER": [
        "Status Water",
        Ecotouch2Tag.STATUS_WATER,
        None,
        None,
        "mdi:thermometer-water",
        True,
        None,
        None,
    ],
    "STATUS_COOLING": [
        "Status Cooling",
        Ecotouch2Tag.STATUS_COOLING,
        None,
        None,
        "mdi:coolant-temperature",
        True,
        None,
        None,
    ],
    "TEMPERATURE_MIX1_PERCENT": [
        "Temperature mixing circle 1 percent",
        Ecotouch2Tag.TEMPERATURE_MIX1_PERCENT,
        None,
        PERCENTAGE,
        "mdi:gauge",
        False,
        None,
        None,
    ],
    "TEMPERATURE_MIX2_PERCENT": [
        "Temperature mixing circle 2 percent",
        Ecotouch2Tag.TEMPERATURE_MIX2_PERCENT,
        None,
        PERCENTAGE,
        "mdi:gauge",
        False,
        None,
        None,
    ],
    "TEMPERATURE_MIX3_PERCENT": [
        "Temperature mixing circle 3 percent",
        Ecotouch2Tag.TEMPERATURE_MIX3_PERCENT,
        None,
        PERCENTAGE,
        "mdi:gauge",
        False,
        None,
        None,
    ],
    # other (none temperature) values...
    "PRESSURE_EVAPORATION": [
        "Pressure Evaporation",
        Ecotouch2Tag.PRESSURE_EVAPORATION,
        DEVICE_CLASS_PRESSURE,
        PRESSURE_BAR,
        "mdi:gauge",
        False,
        None,
        None,
    ],
    "PRESSURE_CONDENSATION": [
        "Pressure Condensation",
        Ecotouch2Tag.PRESSURE_CONDENSATION,
        DEVICE_CLASS_PRESSURE,
        PRESSURE_BAR,
        "mdi:gauge",
        False,
        None,
        None,
    ],
    # other data...
    "POSITION_EXPANSION_VALVE": [
        "Position Expansion Valve",
        Ecotouch2Tag.POSITION_EXPANSION_VALVE,
        None,
        SensorStateClass.MEASUREMENT,
        "mdi:gauge",
        False,
        None,
        None,
    ],
    "SUCTION_GAS_OVERHEATING": [
        "Suction Gas Overheating",
        Ecotouch2Tag.SUCTION_GAS_OVERHEATING,
        None,
        SensorStateClass.MEASUREMENT,
        "mdi:gauge",
        False,
        None,
        None,
    ],
    "POWER_ELECTRIC": [
        "Power Electrical",
        Ecotouch2Tag.POWER_ELECTRIC,
        DEVICE_CLASS_POWER,
        POWER_KILO_WATT,
        "mdi:lightning-bolt",
        True,
        None,
        None,
    ],
    "POWER_HEATING": [
        "Power Thermal",
        Ecotouch2Tag.POWER_HEATING,
        DEVICE_CLASS_POWER,
        POWER_KILO_WATT,
        "mdi:lightning-bolt",
        True,
        None,
        None,
    ],
    "POWER_COOLING": [
        "Power Cooling",
        Ecotouch2Tag.POWER_COOLING,
        DEVICE_CLASS_POWER,
        POWER_KILO_WATT,
        "mdi:lightning-bolt",
        True,
        None,
        None,
    ],
    "COP_HEATING": [
        "COP Heating",
        Ecotouch2Tag.COP_HEATING,
        None,
        SensorStateClass.MEASUREMENT,
        "mdi:gauge",
        True,
        None,
        None,
    ],
    "COP_COOLING": [
        "COP Cooling",
        Ecotouch2Tag.COP_COOLING,
        None,
        SensorStateClass.MEASUREMENT,
        "mdi:gauge",
        True,
        None,
        None,
    ],
    "PERCENT_HEAT_CIRC_PUMP": [
        "Percent Heat Circ Pump",
        Ecotouch2Tag.PERCENT_HEAT_CIRC_PUMP,
        DEVICE_CLASS_POWER_FACTOR,
        PERCENTAGE,
        "mdi:gauge",
        False,
        None,
        None,
    ],
    "PERCENT_SOURCE_PUMP": [
        "Percent Source Pump",
        Ecotouch2Tag.PERCENT_SOURCE_PUMP,
        DEVICE_CLASS_POWER_FACTOR,
        PERCENTAGE,
        "mdi:gauge",
        False,
        None,
        None,
    ],
    "PERCENT_COMPRESSOR": [
        "Percent Compressor",
        Ecotouch2Tag.PERCENT_COMPRESSOR,
        DEVICE_CLASS_POWER_FACTOR,
        PERCENTAGE,
        "mdi:gauge",
        False,
        None,
        None,
    ],
    # writeable sensors from here...
    "HOLIDAY_START_TIME": [
        "Holiday start",
        Ecotouch2Tag.HOLIDAY_START_TIME,
        DEVICE_CLASS_DATE,
        None,
        "mdi:calendar-arrow-right",
        True,
        None,
        None,
    ],
    "HOLIDAY_END_TIME": [
        "Holiday end",
        Ecotouch2Tag.HOLIDAY_END_TIME,
        DEVICE_CLASS_DATE,
        None,
        "mdi:calendar-arrow-left",
        True,
        None,
        None,
    ],
    "STATE_SERVICE": [
        "State Service",
        Ecotouch2Tag.STATE_SERVICE,
        None,
        None,
        None,
        True,
        None,
        None,
    ],
}

# async def async_setup_entry(hass: HomeAssistantType, entry: ConfigType, async_add_entities) -> None:
async def async_setup_entry(
    hass: HomeAssistantType, entry: ConfigType, async_add_devices
) -> None:
    """Set up the Waterkotte sensor platform."""
    _LOGGER.debug("Sensor async_setup_entry")
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices(
        [
            WaterkotteHeatpumpSensor(entry, coordinator, sensor_type)
            for sensor_type in SENSOR_TYPES
        ]
    )


class WaterkotteHeatpumpSensor(SensorEntity, WaterkotteHeatpumpEntity):
    """waterkotte_heatpump Sensor class."""

    def __init__(
        self, entry, hass_data, sensor_type
    ):  # pylint: disable=unused-argument
        """Initialize the sensor."""
        self._coordinator = hass_data

        self._type = sensor_type
        self._name = f"{SENSOR_TYPES[self._type][0]}"
        self._unique_id = self._type
        self._entry_data = entry.data
        self._device_id = entry.entry_id
        hass_data.alltags.update({self._unique_id: SENSOR_TYPES[self._type][1]})
        super().__init__(hass_data, entry)

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def tag(self):
        """Return a unique ID to use for this entity."""
        return SENSOR_TYPES[self._type][1]

    @property
    def state(self):
        """Return the state of the sensor."""
        # result = ""
        # print(self._coordinator.data)
        try:
            sensor = SENSOR_TYPES[self._type]
            value = self._coordinator.data[sensor[1]]["value"]
            if value is None or value == "":
                value = "unknown"
        except KeyError:
            value = "unknown"
        except TypeError:
            return "unknown"
        if value is True:
            value = "on"
        elif value is False:
            value = "off"
        return value

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return SENSOR_TYPES[self._type][4]
        # return ICON

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return SENSOR_TYPES[self._type][2]

    @property
    def entity_registry_enabled_default(self):
        """Return the entity_registry_enabled_default of the sensor."""
        return SENSOR_TYPES[self._type][5]

    @property
    def entity_category(self):
        """Return the unit of measurement."""
        return SENSOR_TYPES[self._type][7]

    @property
    def unique_id(self):
        """Return the unique of the sensor."""
        return self._unique_id

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return SENSOR_TYPES[self._type][3]

    async def async_update(self):
        """Schedule a custom update via the common entity update service."""
        await self._coordinator.async_request_refresh()

    @property
    def should_poll(self) -> bool:
        """Entities do not individually poll."""
        return False
