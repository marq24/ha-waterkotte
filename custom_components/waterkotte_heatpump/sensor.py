"""Sensor platform for Waterkotte Heatpump."""
import logging

# from homeassistant.helpers.entity import Entity, EntityCategory  # , DeviceInfo
from homeassistant.helpers.typing import ConfigType, HomeAssistantType, StateType
from datetime import datetime, date, time
from decimal import Decimal

from homeassistant.const import (
    PERCENTAGE,
    ENERGY_KILO_WATT_HOUR,
    UnitOfTemperature,
    UnitOfPressure,
    UnitOfPower,
)

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
    SensorDeviceClass,
)

from custom_components.waterkotte_heatpump.pywaterkotte_ha.ecotouch import EcotouchTag
from .entity import WaterkotteHeatpumpEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
_LANG = None

# Sensor types are defined as:
#   variable -> [0]title, [1] EcoTouchTag, [2]device_class, [3]units, [4]icon, [5]enabled_by_default, [6]options, [7]entity_category #pylint: disable=line-too-long
SENSOR_TYPES = {
    # temperature sensors
    "TEMPERATURE_OUTSIDE": [
        "Temperature Outside",
        EcotouchTag.TEMPERATURE_OUTSIDE,
        SensorDeviceClass.TEMPERATURE,
        UnitOfTemperature.CELSIUS,
        "mdi:sun-snowflake-variant",
        True,
        None,
        None,
    ],
    "TEMPERATURE_OUTSIDE_1H": [
        "Temperature Outside 1h",
        EcotouchTag.TEMPERATURE_OUTSIDE_1H,
        SensorDeviceClass.TEMPERATURE,
        UnitOfTemperature.CELSIUS,
        "mdi:sun-snowflake-variant",
        True,
        None,
        None,
    ],
    "TEMPERATURE_OUTSIDE_24H": [
        "Temperature Outside 24h",
        EcotouchTag.TEMPERATURE_OUTSIDE_24H,
        SensorDeviceClass.TEMPERATURE,
        UnitOfTemperature.CELSIUS,
        "mdi:sun-snowflake-variant",
        True,
        None,
        None,
    ],
    "TEMPERATURE_SOURCE_ENTRY": [
        "Temperature Source Entry",
        EcotouchTag.TEMPERATURE_SOURCE_ENTRY,
        SensorDeviceClass.TEMPERATURE,
        UnitOfTemperature.CELSIUS,
        "mdi:thermometer",
        True,
        None,
        None,
    ],
    "TEMPERATURE_SOURCE_EXIT": [
        "Temperature Source Exit",
        EcotouchTag.TEMPERATURE_SOURCE_EXIT,
        SensorDeviceClass.TEMPERATURE,
        UnitOfTemperature.CELSIUS,
        "mdi:thermometer",
        True,
        None,
        None,
    ],
    "TEMPERATURE_EVAPORATION": [
        "Temperature Evaporation",
        EcotouchTag.TEMPERATURE_EVAPORATION,
        SensorDeviceClass.TEMPERATURE,
        UnitOfTemperature.CELSIUS,
        "mdi:thermometer",
        True,
        None,
        None,
    ],
    "TEMPERATURE_SUCTION_LINE": [
        "Temperature Suction Line",
        EcotouchTag.TEMPERATURE_SUCTION_LINE,
        SensorDeviceClass.TEMPERATURE,
        UnitOfTemperature.CELSIUS,
        "mdi:thermometer",
        True,
        None,
        None,
    ],
    "TEMPERATURE_RETURN": [
        "Temperature Return",
        EcotouchTag.TEMPERATURE_RETURN,
        SensorDeviceClass.TEMPERATURE,
        UnitOfTemperature.CELSIUS,
        "mdi:thermometer",
        True,
        None,
        None,
    ],
    "TEMPERATURE_FLOW": [
        "Temperature Flow",
        EcotouchTag.TEMPERATURE_FLOW,
        SensorDeviceClass.TEMPERATURE,
        UnitOfTemperature.CELSIUS,
        "mdi:thermometer",
        True,
        None,
        None,
    ],
    "TEMPERATURE_CONDENSATION": [
        "Temperature Condensation",
        EcotouchTag.TEMPERATURE_CONDENSATION,
        SensorDeviceClass.TEMPERATURE,
        UnitOfTemperature.CELSIUS,
        "mdi:thermometer",
        True,
        None,
        None,
    ],
    "TEMPERATURE_BUFFERTANK": [
        "Temperature Buffer Tank",
        EcotouchTag.TEMPERATURE_BUFFERTANK,
        SensorDeviceClass.TEMPERATURE,
        UnitOfTemperature.CELSIUS,
        "mdi:storage-tank",
        True,
        None,
        None,
    ],
    "TEMPERATURE_ROOM": [
        "Temperature Room",
        EcotouchTag.TEMPERATURE_ROOM,
        SensorDeviceClass.TEMPERATURE,
        UnitOfTemperature.CELSIUS,
        "mdi:thermostat-box",
        False,
        None,
        None,
    ],
    "TEMPERATURE_ROOM_1H": [
        "Temperature Room 1h",
        EcotouchTag.TEMPERATURE_ROOM_1H,
        SensorDeviceClass.TEMPERATURE,
        UnitOfTemperature.CELSIUS,
        "mdi:thermostat-box",
        False,
        None,
        None,
    ],
    "TEMPERATURE_HEATING": [
        "Temperature Heating",
        EcotouchTag.TEMPERATURE_HEATING,
        SensorDeviceClass.TEMPERATURE,
        UnitOfTemperature.CELSIUS,
        "mdi:radiator",
        True,
        None,
        None,
    ],
    "TEMPERATURE_HEATING_DEMAND": [
        "Demanded Temperature Heating",
        EcotouchTag.TEMPERATURE_HEATING_DEMAND,
        SensorDeviceClass.TEMPERATURE,
        UnitOfTemperature.CELSIUS,
        "mdi:radiator",
        True,
        None,
        None,
    ],
    "TEMPERATURE_COOLING": [
        "Temperature Cooling",
        EcotouchTag.TEMPERATURE_COOLING,
        SensorDeviceClass.TEMPERATURE,
        UnitOfTemperature.CELSIUS,
        "mdi:snowflake-thermometer",
        False,
        None,
        None,
    ],
    "TEMPERATURE_COOLING_DEMAND": [
        "Demanded Temperature Cooling",
        EcotouchTag.TEMPERATURE_COOLING_DEMAND,
        SensorDeviceClass.TEMPERATURE,
        UnitOfTemperature.CELSIUS,
        "mdi:snowflake-thermometer",
        False,
        None,
        None,
    ],
    "TEMPERATURE_WATER": [
        "Temperature Hot Water",
        EcotouchTag.TEMPERATURE_WATER,
        SensorDeviceClass.TEMPERATURE,
        UnitOfTemperature.CELSIUS,
        "mdi:water-thermometer",
        True,
        None,
        None,
    ],
    "TEMPERATURE_WATER_DEMAND": [
        "Demanded Temperature Hot Water",
        EcotouchTag.TEMPERATURE_WATER_DEMAND,
        SensorDeviceClass.TEMPERATURE,
        UnitOfTemperature.CELSIUS,
        "mdi:water-thermometer",
        True,
        None,
        None,
    ],
    "TEMPERATURE_MIX1": [
        "Temperature mixing circle 1",
        EcotouchTag.TEMPERATURE_MIX1,
        SensorDeviceClass.TEMPERATURE,
        UnitOfTemperature.CELSIUS,
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
    "TEMPERATURE_MIX1_DEMAND": [
        "Demanded Temperature mixing circle 1",
        EcotouchTag.TEMPERATURE_MIX1_DEMAND,
        SensorDeviceClass.TEMPERATURE,
        UnitOfTemperature.CELSIUS,
        "mdi:numeric-1-circle",
        True,
        None,
        None,
    ],
    "TEMPERATURE_MIX2": [
        "Temperature mixing circle 2",
        EcotouchTag.TEMPERATURE_MIX2,
        SensorDeviceClass.TEMPERATURE,
        UnitOfTemperature.CELSIUS,
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
    "TEMPERATURE_MIX2_DEMAND": [
        "Demanded Temperature mixing circle 2",
        EcotouchTag.TEMPERATURE_MIX2_DEMAND,
        SensorDeviceClass.TEMPERATURE,
        UnitOfTemperature.CELSIUS,
        "mdi:numeric-2-circle",
        False,
        None,
        None,
    ],
    "TEMPERATURE_MIX3": [
        "Temperature mixing circle 3",
        EcotouchTag.TEMPERATURE_MIX3,
        SensorDeviceClass.TEMPERATURE,
        UnitOfTemperature.CELSIUS,
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
    "TEMPERATURE_MIX3_DEMAND": [
        "Demanded Temperature mixing circle 3",
        EcotouchTag.TEMPERATURE_MIX3_DEMAND,
        SensorDeviceClass.TEMPERATURE,
        UnitOfTemperature.CELSIUS,
        "mdi:numeric-3-circle",
        False,
        None,
        None,
    ],
    "TEMPERATURE_POOL": [
        "Temperature Pool",
        EcotouchTag.TEMPERATURE_POOL,
        SensorDeviceClass.TEMPERATURE,
        UnitOfTemperature.CELSIUS,
        "mdi:pool-thermometer",
        False,
        None,
        None,
    ],
    "TEMPERATURE_POOL_DEMAND": [
        "Demanded Temperature Pool",
        EcotouchTag.TEMPERATURE_POOL_DEMAND,
        SensorDeviceClass.TEMPERATURE,
        UnitOfTemperature.CELSIUS,
        "mdi:pool-thermometer",
        False,
        None,
        None,
    ],
    "TEMPERATURE_SOLAR": [
        "Temperature Solar",
        EcotouchTag.TEMPERATURE_SOLAR,
        SensorDeviceClass.TEMPERATURE,
        UnitOfTemperature.CELSIUS,
        "mdi:solar-power-variant",
        False,
        None,
        None,
    ],
    "TEMPERATURE_SOLAR_EXIT": [
        "Temperature Solar Collector Exit",
        EcotouchTag.TEMPERATURE_SOLAR_EXIT,
        SensorDeviceClass.TEMPERATURE,
        UnitOfTemperature.CELSIUS,
        "mdi:solar-power-variant",
        False,
        None,
        None,
    ],
    "TEMPERATURE_DISCHARGE": [
        "Temperature Discharge",
        EcotouchTag.TEMPERATURE_DISCHARGE,
        SensorDeviceClass.TEMPERATURE,
        UnitOfTemperature.CELSIUS,
        "mdi:thermometer",
        False,
        None,
        None,
    ],
    # other (none temperature) values...
    "PRESSURE_EVAPORATION": [
        "Pressure Evaporation",
        EcotouchTag.PRESSURE_EVAPORATION,
        SensorDeviceClass.PRESSURE,
        UnitOfPressure.BAR,
        "mdi:gauge",
        True,
        None,
        None,
    ],
    "PRESSURE_CONDENSATION": [
        "Pressure Condensation",
        EcotouchTag.PRESSURE_CONDENSATION,
        SensorDeviceClass.PRESSURE,
        UnitOfPressure.BAR,
        "mdi:gauge",
        True,
        None,
        None,
    ],
    "PRESSURE_WATER": [
        "Pressure Water",
        EcotouchTag.PRESSURE_WATER,
        SensorDeviceClass.PRESSURE,
        UnitOfPressure.BAR,
        "mdi:gauge",
        False,
        None,
        None,
    ],
    # other data...
    "POSITION_EXPANSION_VALVE": [
        "Position Expansion Valve",
        EcotouchTag.POSITION_EXPANSION_VALVE,
        None,
        None,
        "mdi:gauge",
        True,
        None,
        None,
    ],
    "SUCTION_GAS_OVERHEATING": [
        "Suction Gas Overheating",
        EcotouchTag.SUCTION_GAS_OVERHEATING,
        None,
        None,
        "mdi:gauge",
        True,
        None,
        None,
    ],
    "POWER_ELECTRIC": [
        "Power Electrical",
        EcotouchTag.POWER_ELECTRIC,
        SensorDeviceClass.POWER,
        UnitOfPower.KILO_WATT,
        "mdi:meter-electric",
        True,
        None,
        None,
    ],
    "POWER_HEATING": [
        "Power Thermal",
        EcotouchTag.POWER_HEATING,
        SensorDeviceClass.POWER,
        UnitOfPower.KILO_WATT,
        "mdi:radiator",
        True,
        None,
        None,
    ],
    "POWER_COOLING": [
        "Power Cooling",
        EcotouchTag.POWER_COOLING,
        SensorDeviceClass.POWER,
        UnitOfPower.KILO_WATT,
        "mdi:snowflake-thermometer",
        True,
        None,
        None,
    ],
    "COP_HEATING": [
        "COP Heating",
        EcotouchTag.COP_HEATING,
        None,
        None,
        "mdi:gauge",
        True,
        None,
        None,
    ],
    "COP_COOLING": [
        "COP Cooling",
        EcotouchTag.COP_COOLING,
        None,
        None,
        "mdi:gauge",
        True,
        None,
        None,
    ],
    "ENERGY_CONSUMPTION_TOTAL_YEAR":[
        "ENERGY_CONSUMPTION_TOTAL_YEAR",
        EcotouchTag.ENERGY_CONSUMPTION_TOTAL_YEAR,
        SensorDeviceClass.ENERGY,
        ENERGY_KILO_WATT_HOUR,
        "mdi:lightning-bolt-outline",
        True,
        None,
        None,
        SensorStateClass.TOTAL_INCREASING
    ],
    "COMPRESSOR_ELECTRIC_CONSUMPTION_YEAR":[
        "COMPRESSOR_ELECTRIC_CONSUMPTION_YEAR",
        EcotouchTag.COMPRESSOR_ELECTRIC_CONSUMPTION_YEAR,
        SensorDeviceClass.ENERGY,
        ENERGY_KILO_WATT_HOUR,
        "mdi:gauge",
        True,
        None,
        None,
        SensorStateClass.TOTAL_INCREASING
    ],
    "SOURCEPUMP_ELECTRIC_CONSUMPTION_YEAR":[
        "SOURCEPUMP_ELECTRIC_CONSUMPTION_YEAR",
        EcotouchTag.SOURCEPUMP_ELECTRIC_CONSUMPTION_YEAR,
        SensorDeviceClass.ENERGY,
        ENERGY_KILO_WATT_HOUR,
        "mdi:water-pump",
        False,
        None,
        None,
        SensorStateClass.TOTAL_INCREASING
    ],
    "ELECTRICAL_HEATER_ELECTRIC_CONSUMPTION_YEAR":[
        "ELECTRICAL_HEATER_ELECTRIC_CONSUMPTION_YEAR",
        EcotouchTag.ELECTRICAL_HEATER_ELECTRIC_CONSUMPTION_YEAR,
        SensorDeviceClass.ENERGY,
        ENERGY_KILO_WATT_HOUR,
        "mdi:heating-coil",
        True,
        None,
        None,
        SensorStateClass.TOTAL_INCREASING
    ],
    "ENERGY_PRODUCTION_TOTAL_YEAR":[
        "ENERGY_PRODUCTION_TOTAL_YEAR",
        EcotouchTag.ENERGY_PRODUCTION_TOTAL_YEAR,
        SensorDeviceClass.ENERGY,
        ENERGY_KILO_WATT_HOUR,
        "mdi:home-thermometer-outline",
        True,
        None,
        None,
        SensorStateClass.TOTAL_INCREASING
    ],
    "HEATING_ENERGY_PRODUCTION_YEAR":[
        "HEATING_ENERGY_PRODUCTION_YEAR",
        EcotouchTag.HEATING_ENERGY_PRODUCTION_YEAR,
        SensorDeviceClass.ENERGY,
        ENERGY_KILO_WATT_HOUR,
        "mdi:radiator",
        True,
        None,
        None,
        SensorStateClass.TOTAL_INCREASING
    ],
    "HOT_WATER_ENERGY_PRODUCTION_YEAR":[
        "HOT_WATER_ENERGY_PRODUCTION_YEAR",
        EcotouchTag.HOT_WATER_ENERGY_PRODUCTION_YEAR,
        SensorDeviceClass.ENERGY,
        ENERGY_KILO_WATT_HOUR,
        "mdi:water-thermometer",
        True,
        None,
        None,
        SensorStateClass.TOTAL_INCREASING
    ],
    "COOLING_ENERGY_YEAR":[
        "COOLING_ENERGY_YEAR",
        EcotouchTag.COOLING_ENERGY_YEAR,
        SensorDeviceClass.ENERGY,
        ENERGY_KILO_WATT_HOUR,
        "mdi:snowflake-thermometer",
        True,
        None,
        None,
        SensorStateClass.TOTAL_INCREASING
    ],
    "PERCENT_HEAT_CIRC_PUMP": [
        "Percent Heat Circ Pump",
        EcotouchTag.PERCENT_HEAT_CIRC_PUMP,
        SensorDeviceClass.POWER_FACTOR,
        PERCENTAGE,
        "mdi:gauge",
        False,
        None,
        None,
    ],
    "PERCENT_SOURCE_PUMP": [
        "Percent Source Pump",
        EcotouchTag.PERCENT_SOURCE_PUMP,
        SensorDeviceClass.POWER_FACTOR,
        PERCENTAGE,
        "mdi:gauge",
        False,
        None,
        None,
    ],
    "PERCENT_COMPRESSOR": [
        "Percent Compressor",
        EcotouchTag.PERCENT_COMPRESSOR,
        SensorDeviceClass.POWER_FACTOR,
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
        SensorDeviceClass.DATE,
        None,
        "mdi:calendar-arrow-right",
        True,
        None,
        None,
    ],
    "HOLIDAY_END_TIME": [
        "Holiday end",
        EcotouchTag.HOLIDAY_END_TIME,
        SensorDeviceClass.DATE,
        None,
        "mdi:calendar-arrow-left",
        True,
        None,
        None,
    ],
    "SCHEDULE_WATER_DISINFECTION_START_TIME": [
        "Water disinfection start time",
        EcotouchTag.SCHEDULE_WATER_DISINFECTION_START_TIME,
        SensorDeviceClass.DATE,
        None,
        "mdi:clock-digital",
        False,
        None,
        time,
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
    global _LANG
    _LANG = coordinator.lang
    async_add_devices([WaterkotteHeatpumpSensor(entry, coordinator, sensor_type)
                       for sensor_type in SENSOR_TYPES])


class WaterkotteHeatpumpSensor(SensorEntity, WaterkotteHeatpumpEntity):
    """waterkotte_heatpump Sensor class."""

    def __init__(self, entry, hass_data, sensor_type):  # pylint: disable=unused-argument
        """Initialize the sensor."""
        self.entity_id = f"{DOMAIN}.wkh_{sensor_type}"
        self._coordinator = hass_data
        self._type = sensor_type
        self._attr_unique_id = sensor_type
        self._entry_data = entry.data
        self._device_id = entry.entry_id

        # if the 'name' of the Sensor is matching the TAG, we use the NEW translation code!
        if self._type == SENSOR_TYPES[self._type][0]:
            self._attr_translation_key = f"{sensor_type.lower()}"
        else:
            if SENSOR_TYPES[self._type][1].tags[0] in _LANG:
                self._attr_name = _LANG[SENSOR_TYPES[self._type][1].tags[0]]
            else:
                _LOGGER.warning(str(SENSOR_TYPES[self._type][1].tags[0])+" Sensor not found in translation")
                self._attr_name = f"{SENSOR_TYPES[self._type][0]}"

        # this are the NEW-Sensors, where the translation comes from the "translations" json files...
        if len(SENSOR_TYPES[self._type]) > 8:
            self._attr_state_class = SENSOR_TYPES[self._type][8]
            #self._attr_suggested_display_precision = 3
            self._attr_selfimplemented_display_precision = 3
        else:
            self._attr_selfimplemented_display_precision = None
            self._attr_state_class = SensorStateClass.MEASUREMENT

        super().__init__(hass_data, entry)

    #SENSOR_TYPES['x'][0] => DisplayName (if not translated)
    #SENSOR_TYPES['x'][1] => EcotouchTag
    #SENSOR_TYPES['x'][2] => SensorDeviceClass
    #SENSOR_TYPES['x'][3] => Native Unit_of_measurement
    #SENSOR_TYPES['x'][4] => Icon
    #SENSOR_TYPES['x'][5] => enabled_by_default
    #SENSOR_TYPES['x'][6] => Options
    #SENSOR_TYPES['x'][7] => entity_category
    #SENSOR_TYPES['x'][8] => SensorState_class -> default is MEASUREMENT

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

            if self._attr_selfimplemented_display_precision is not None:
                value = round(float(value), self._attr_selfimplemented_display_precision)
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
        # UNKNONW ?!
        return None


    @property
    def unique_id(self):
        """Return the unique of the sensor."""
        return self._attr_unique_id

    async def async_update(self):
        """Schedule a custom update via the common entity update service."""
        await self._coordinator.async_request_refresh()

    @property
    def should_poll(self) -> bool:
        """Entities do not individually poll."""
        return False
