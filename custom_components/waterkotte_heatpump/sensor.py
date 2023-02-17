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
    DEVICE_CLASS_TEMPERATURE,
    PRESSURE_BAR,
    TEMP_CELSIUS, DEVICE_CLASS_POWER,
    POWER_KILO_WATT,
)

from homeassistant.components.sensor import (
    SensorStateClass,
)

from custom_components.waterkotte_heatpump.mypywaterkotte.ecotouch import EcotouchTag
from .entity import WaterkotteHeatpumpEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Sensor types are defined as:
#   variable -> [0]title, [1] EcoTouchTag, [2]device_class, [3]units, [4]icon, [5]enabled_by_default, [6]options, [7]entity_category #pylint: disable=line-too-long
SENSOR_TYPES = {
    # status sensors
    "STATUS_HEATING": [
        "Status Heating",
        EcotouchTag.STATUS_HEATING,
        None,
        None,
        "mdi:radiator",
        True,
        None,
        None,
    ],
    "STATUS_WATER": [
        "Status Water",
        EcotouchTag.STATUS_WATER,
        None,
        None,
        "mdi:water-thermometer",
        True,
        None,
        None,
    ],
    "STATUS_COOLING": [
        "Status Cooling",
        EcotouchTag.STATUS_COOLING,
        None,
        None,
        "mdi:snowflake-thermometer",
        True,
        None,
        None,
    ],
    # temperature sensors
    "TEMPERATURE_OUTSIDE": [
        "Temperature Outside",
        EcotouchTag.TEMPERATURE_OUTSIDE,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:sun-snowflake-variant",
        True,
        None,
        None,
    ],
    "TEMPERATURE_OUTSIDE_1H": [
        "Temperature Outside 1h",
        EcotouchTag.TEMPERATURE_OUTSIDE_1H,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:sun-snowflake-variant",
        True,
        None,
        None,
    ],
    "TEMPERATURE_OUTSIDE_24H": [
        "Temperature Outside 24h",
        EcotouchTag.TEMPERATURE_OUTSIDE_24H,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:sun-snowflake-variant",
        True,
        None,
        None,
    ],
    "TEMPERATURE_SOURCE_ENTRY": [
        "Temperature Source Entry",
        EcotouchTag.TEMPERATURE_SOURCE_ENTRY,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        True,
        None,
        None,
    ],
    "TEMPERATURE_SOURCE_EXIT": [
        "Temperature Source Exit",
        EcotouchTag.TEMPERATURE_SOURCE_EXIT,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        True,
        None,
        None,
    ],
    "TEMPERATURE_EVAPORATION": [
        "Temperature Evaporation",
        EcotouchTag.TEMPERATURE_EVAPORATION,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        True,
        None,
        None,
    ],
    "TEMPERATURE_SUCTION_LINE": [
        "Temperature Suction Line",
        EcotouchTag.TEMPERATURE_SUCTION_LINE,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        True,
        None,
        None,
    ],
    "TEMPERATURE_RETURN": [
        "Temperature Return",
        EcotouchTag.TEMPERATURE_RETURN,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        True,
        None,
        None,
    ],
    "TEMPERATURE_FLOW": [
        "Temperature Flow",
        EcotouchTag.TEMPERATURE_FLOW,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        True,
        None,
        None,
    ],
    "TEMPERATURE_CONDENSATION": [
        "Temperature Condensation",
        EcotouchTag.TEMPERATURE_CONDENSATION,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        True,
        None,
        None,
    ],
    "TEMPERATURE_BUFFERTANK": [
        "Temperature Buffer Tank",
        EcotouchTag.TEMPERATURE_BUFFERTANK,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:storage-tank",
        True,
        None,
        None,
    ],
    "TEMPERATURE_ROOM": [
        "Temperature Room",
        EcotouchTag.TEMPERATURE_ROOM,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermostat-box",
        False,
        None,
        None,
    ],
    "TEMPERATURE_ROOM_1H": [
        "Temperature Room 1h",
        EcotouchTag.TEMPERATURE_ROOM_1H,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermostat-box",
        False,
        None,
        None,
    ],
    "TEMPERATURE_HEATING": [
        "Temperature Heating",
        EcotouchTag.TEMPERATURE_HEATING,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:radiator",
        True,
        None,
        None,
    ],
    "TEMPERATURE_HEATING_SET": [
        "Demanded Temperature Heating",
        EcotouchTag.TEMPERATURE_HEATING_SET,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:radiator",
        True,
        None,
        None,
    ],
    "TEMPERATURE_COOLING": [
        "Temperature Cooling",
        EcotouchTag.TEMPERATURE_COOLING,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:snowflake-thermometer",
        False,
        None,
        None,
    ],
    "TEMPERATURE_COOLING_SET": [
        "Demanded Temperature Cooling",
        EcotouchTag.TEMPERATURE_COOLING_SET,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:snowflake-thermometer",
        False,
        None,
        None,
    ],
    "TEMPERATURE_WATER": [
        "Temperature Hot Water",
        EcotouchTag.TEMPERATURE_WATER,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:water-thermometer",
        True,
        None,
        None,
    ],
    "TEMPERATURE_WATER_SET": [
        "Demanded Temperature Hot Water",
        EcotouchTag.TEMPERATURE_WATER_SET,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:water-thermometer",
        True,
        None,
        None,
    ],
    "TEMPERATURE_MIX1": [
        "Temperature mixing circle 1",
        EcotouchTag.TEMPERATURE_MIX1,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:numeric-1-circle",
        True,
        None,
        None,
    ],
    "TEMPERATURE_MIX1_PERCENT": [
        "Temperature mixing circle 1 percent",
        EcotouchTag.TEMPERATURE_MIX1_PERCENT,
        None,
        PERCENTAGE,
        "mdi:gauge",
        False,
        None,
        None,
    ],
    "TEMPERATURE_MIX1_SET": [
        "Demanded Temperature mixing circle 1",
        EcotouchTag.TEMPERATURE_MIX1_SET,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:numeric-1-circle",
        True,
        None,
        None,
    ],
    "TEMPERATURE_MIX2": [
        "Temperature mixing circle 2",
        EcotouchTag.TEMPERATURE_MIX2,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:numeric-2-circle",
        False,
        None,
        None,
    ],
    "TEMPERATURE_MIX2_PERCENT": [
        "Temperature mixing circle 2 percent",
        EcotouchTag.TEMPERATURE_MIX2_PERCENT,
        None,
        PERCENTAGE,
        "mdi:gauge",
        False,
        None,
        None,
    ],
    "TEMPERATURE_MIX2_SET": [
        "Demanded Temperature mixing circle 2",
        EcotouchTag.TEMPERATURE_MIX2_SET,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:numeric-2-circle",
        False,
        None,
        None,
    ],
    "TEMPERATURE_MIX3": [
        "Temperature mixing circle 3",
        EcotouchTag.TEMPERATURE_MIX3,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:numeric-3-circle",
        False,
        None,
        None,
    ],
    "TEMPERATURE_MIX3_PERCENT": [
        "Temperature mixing circle 3 percent",
        EcotouchTag.TEMPERATURE_MIX3_PERCENT,
        None,
        PERCENTAGE,
        "mdi:gauge",
        False,
        None,
        None,
    ],
    "TEMPERATURE_MIX3_SET": [
        "Demanded Temperature mixing circle 3",
        EcotouchTag.TEMPERATURE_MIX3_SET,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:numeric-3-circle",
        False,
        None,
        None,
    ],
    "TEMPERATURE_POOL": [
        "Temperature Pool",
        EcotouchTag.TEMPERATURE_POOL,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:pool-thermometer",
        False,
        None,
        None,
    ],
    "TEMPERATURE_POOL_SET": [
        "Demanded Temperature Pool",
        EcotouchTag.TEMPERATURE_POOL_SET,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:pool-thermometer",
        False,
        None,
        None,
    ],
    "TEMPERATURE_SOLAR": [
        "Temperature Solar",
        EcotouchTag.TEMPERATURE_SOLAR,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:solar-power-variant",
        False,
        None,
        None,
    ],
    "TEMPERATURE_SOLAR_EXIT": [
        "Temperature Solar Collector Exit",
        EcotouchTag.TEMPERATURE_SOLAR_EXIT,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:solar-power-variant",
        False,
        None,
        None,
    ],
    # other (none temperature) values...
    "PRESSURE_EVAPORATION": [
        "Pressure Evaporation",
        EcotouchTag.PRESSURE_EVAPORATION,
        DEVICE_CLASS_PRESSURE,
        PRESSURE_BAR,
        "mdi:gauge",
        True,
        None,
        None,
    ],
    "PRESSURE_CONDENSATION": [
        "Pressure Condensation",
        EcotouchTag.PRESSURE_CONDENSATION,
        DEVICE_CLASS_PRESSURE,
        PRESSURE_BAR,
        "mdi:gauge",
        True,
        None,
        None,
    ],
    # other data...
    "POSITION_EXPANSION_VALVE": [
        "Position Expansion Valve",
        EcotouchTag.POSITION_EXPANSION_VALVE,
        None,
        SensorStateClass.MEASUREMENT,
        "mdi:gauge",
        True,
        None,
        None,
    ],
    "SUCTION_GAS_OVERHEATING": [
        "Suction Gas Overheating",
        EcotouchTag.SUCTION_GAS_OVERHEATING,
        None,
        SensorStateClass.MEASUREMENT,
        "mdi:gauge",
        True,
        None,
        None,
    ],
    "POWER_ELECTRIC": [
        "Power Electrical",
        EcotouchTag.POWER_ELECTRIC,
        DEVICE_CLASS_POWER,
        POWER_KILO_WATT,
        "mdi:meter-electric",
        True,
        None,
        None,
    ],
    "POWER_HEATING": [
        "Power Thermal",
        EcotouchTag.POWER_HEATING,
        DEVICE_CLASS_POWER,
        POWER_KILO_WATT,
        "mdi:radiator",
        True,
        None,
        None,
    ],
    "POWER_COOLING": [
        "Power Cooling",
        EcotouchTag.POWER_COOLING,
        DEVICE_CLASS_POWER,
        POWER_KILO_WATT,
        "mdi:snowflake-thermometer",
        True,
        None,
        None,
    ],
    "COP_HEATING": [
        "COP Heating",
        EcotouchTag.COP_HEATING,
        None,
        SensorStateClass.MEASUREMENT,
        "mdi:gauge",
        True,
        None,
        None,
    ],
    "COP_COOLING": [
        "COP Cooling",
        EcotouchTag.COP_COOLING,
        None,
        SensorStateClass.MEASUREMENT,
        "mdi:gauge",
        True,
        None,
        None,
    ],
    "PERCENT_HEAT_CIRC_PUMP": [
        "Percent Heat Circ Pump",
        EcotouchTag.PERCENT_HEAT_CIRC_PUMP,
        DEVICE_CLASS_POWER_FACTOR,
        PERCENTAGE,
        "mdi:gauge",
        False,
        None,
        None,
    ],
    "PERCENT_SOURCE_PUMP": [
        "Percent Source Pump",
        EcotouchTag.PERCENT_SOURCE_PUMP,
        DEVICE_CLASS_POWER_FACTOR,
        PERCENTAGE,
        "mdi:gauge",
        False,
        None,
        None,
    ],
    "PERCENT_COMPRESSOR": [
        "Percent Compressor",
        EcotouchTag.PERCENT_COMPRESSOR,
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
        EcotouchTag.HOLIDAY_START_TIME,
        DEVICE_CLASS_DATE,
        None,
        "mdi:calendar-arrow-right",
        True,
        None,
        None,
    ],
    "HOLIDAY_END_TIME": [
        "Holiday end",
        EcotouchTag.HOLIDAY_END_TIME,
        DEVICE_CLASS_DATE,
        None,
        "mdi:calendar-arrow-left",
        True,
        None,
        None,
    ],
    "SCHEDULE_WATER_DISINFECTION_START": [
        "Water disinfection start time",
        EcotouchTag.SCHEDULE_WATER_DISINFECTION_START,
        None, # time hh:mm
        None,
        "mdi:clock-start",
        False,
        None,
        None,
    ],
    "SCHEDULE_WATER_DISINFECTION_DURATION": [
        "Water disinfection end time",
        EcotouchTag.SCHEDULE_WATER_DISINFECTION_DURATION,
        None, # duration in hh:00
        None,
        "mdi:clock-end",
        False,
        None,
        None,
    ],

    "STATE_SERVICE": [
        "State Service",
        EcotouchTag.STATE_SERVICE,
        None,
        None,
        "mdi:wrench-clock",
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
        # super().__init__(self, hass_data)
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
    def device_class(self):
        """Return the device class of the sensor."""
        return SENSOR_TYPES[self._type][2]

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return SENSOR_TYPES[self._type][3]

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return SENSOR_TYPES[self._type][4]
        # return ICON

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

    async def async_update(self):
        """Schedule a custom update via the common entity update service."""
        await self._coordinator.async_request_refresh()

    @property
    def should_poll(self) -> bool:
        """Entities do not individually poll."""
        return False
