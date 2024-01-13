"""Sensor platform for Waterkotte Heatpump."""
import logging

from homeassistant.components.number import NumberEntity, NumberDeviceClass, DEFAULT_STEP, NumberMode
from homeassistant.const import UnitOfTemperature, UnitOfTime
from homeassistant.helpers.typing import ConfigType, HomeAssistantType

from custom_components.waterkotte_heatpump.pywaterkotte_ha.ecotouch import EcotouchTag
from .entity import WaterkotteHeatpumpEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

TENTH_STEP = 0.1
FIFTH_STEP = 0.5

# Sensor types are defined as:
#   variable -> [0]title, [1] EcotouchTag, [2]device_class, [3]min, [4]icon, [5]enabled_by_default, [6]max, [7]step #pylint: disable=line-too-long
SENSOR_TYPES = {
    # temperature sensors

    # not sure if this RETURN temperature should be set able at all?!
    "TEMPERATURE_RETURN_SETPOINT": [
        "Temperature Return Setpoint",
        EcotouchTag.TEMPERATURE_RETURN_SETPOINT,
        NumberDeviceClass.TEMPERATURE,
        "mdi:thermometer",
        False,
        0,
        100,
        DEFAULT_STEP,
        NumberMode.BOX,
        UnitOfTemperature.CELSIUS,
    ],

    # Cooling/Kuehlung...
    # A109
    "TEMPERATURE_COOLING_SETPOINT": [
        "Temperature Cooling Demand",
        EcotouchTag.TEMPERATURE_COOLING_SETPOINT,
        NumberDeviceClass.TEMPERATURE,
        "mdi:snowflake-thermometer",
        False,
        5,
        26,
        TENTH_STEP,
        NumberMode.BOX,
        UnitOfTemperature.CELSIUS,
    ],
    # A108
    "TEMPERATURE_COOLING_OUTDOOR_LIMIT": [
        "Temperature Cooling Outdoor Limit",
        EcotouchTag.TEMPERATURE_COOLING_OUTDOOR_LIMIT,
        NumberDeviceClass.TEMPERATURE,
        "mdi:snowflake-thermometer",
        False,
        0,
        100,
        DEFAULT_STEP,
        NumberMode.BOX,
        UnitOfTemperature.CELSIUS,
    ],

    # Heizung
    # A32 manual heat-setpoint (when heat_mode = 1)
    "TEMPERATURE_HEATING_SETPOINT": [
        "Temperature Heating Demand",
        EcotouchTag.TEMPERATURE_HEATING_SETPOINT,
        NumberDeviceClass.TEMPERATURE,
        "mdi:radiator",
        True,
        15,
        60,
        TENTH_STEP,
        NumberMode.BOX,
        UnitOfTemperature.CELSIUS,
    ],
    "TEMPERATURE_HEATING_ADJUST": [
        "Temperature heating Adjustment",
        EcotouchTag.TEMPERATURE_HEATING_ADJUST,
        NumberDeviceClass.TEMPERATURE,
        "mdi:radiator",
        True,
        -2,
        2,
        FIFTH_STEP,
        NumberMode.SLIDER,
        UnitOfTemperature.KELVIN,
    ],
    "TEMPERATURE_HEATING_HYSTERESIS": [
        "Temperature heating Hysteresis",
        EcotouchTag.TEMPERATURE_HEATING_HYSTERESIS,
        NumberDeviceClass.TEMPERATURE,
        "mdi:radiator",
        True,
        0,
        10,
        TENTH_STEP,
        NumberMode.BOX,
        UnitOfTemperature.KELVIN,
    ],
    "TEMPERATURE_MIX1_ADJUST": [
        "Temperature mixing circle 1 Adjustment",
        EcotouchTag.TEMPERATURE_MIX1_ADJUST,
        NumberDeviceClass.TEMPERATURE,
        "mdi:numeric-1-circle",
        True,
        -2,
        2,
        FIFTH_STEP,
        NumberMode.SLIDER,
        UnitOfTemperature.KELVIN,
    ],
    "TEMPERATURE_MIX2_ADJUST": [
        "Temperature mixing circle 2 Adjustment",
        EcotouchTag.TEMPERATURE_MIX2_ADJUST,
        NumberDeviceClass.TEMPERATURE,
        "mdi:numeric-2-circle",
        False,
        -2,
        2,
        FIFTH_STEP,
        NumberMode.SLIDER,
        UnitOfTemperature.KELVIN,
    ],
    "TEMPERATURE_MIX3_ADJUST": [
        "Temperature mixing circle 3 Adjustment",
        EcotouchTag.TEMPERATURE_MIX3_ADJUST,
        NumberDeviceClass.TEMPERATURE,
        "mdi:numeric-3-circle",
        False,
        -2,
        2,
        FIFTH_STEP,
        NumberMode.SLIDER,
        UnitOfTemperature.KELVIN,
    ],

    # Heizung - Heizkennlinie
    # A93
    "TEMPERATURE_HEATING_HC_LIMIT": [
        "Temperature heating curve heating limit",
        EcotouchTag.TEMPERATURE_HEATING_HC_LIMIT,
        NumberDeviceClass.TEMPERATURE,
        "mdi:radiator",
        False,
        5,
        35,
        TENTH_STEP,
        NumberMode.BOX,
        UnitOfTemperature.CELSIUS,
    ],
    # A94
    "TEMPERATURE_HEATING_HC_TARGET": [
        "Temperature heating curve heating limit target",
        EcotouchTag.TEMPERATURE_HEATING_HC_TARGET,
        NumberDeviceClass.TEMPERATURE,
        "mdi:radiator",
        False,
        15,
        65,
        TENTH_STEP,
        NumberMode.BOX,
        UnitOfTemperature.CELSIUS,
    ],
    # A91
    "TEMPERATURE_HEATING_HC_OUTDOOR_NORM": [
        "Temperature heating curve norm outdoor",
        EcotouchTag.TEMPERATURE_HEATING_HC_OUTDOOR_NORM,
        NumberDeviceClass.TEMPERATURE,
        "mdi:radiator",
        False,
        -99,
        99,
        TENTH_STEP,
        NumberMode.BOX,
        UnitOfTemperature.CELSIUS,
    ],
    # A92
    "TEMPERATURE_HEATING_HC_NORM": [
        "Temperature heating curve norm heating circle",
        EcotouchTag.TEMPERATURE_HEATING_HC_NORM,
        NumberDeviceClass.TEMPERATURE,
        "mdi:radiator",
        False,
        0,
        99,
        TENTH_STEP,
        NumberMode.BOX,
        UnitOfTemperature.CELSIUS,
    ],
    # A95
    "TEMPERATURE_HEATING_SETPOINTLIMIT_MAX": [
        "Temperature heating curve Limit for setpoint (Max.)",
        EcotouchTag.TEMPERATURE_HEATING_SETPOINTLIMIT_MAX,
        NumberDeviceClass.TEMPERATURE,
        "mdi:radiator",
        False,
        0,
        99,
        TENTH_STEP,
        NumberMode.BOX,
        UnitOfTemperature.CELSIUS,
    ],
    # A104
    "TEMPERATURE_HEATING_SETPOINTLIMIT_MIN": [
        "Temperature heating curve Limit for setpoint (Min.)",
        EcotouchTag.TEMPERATURE_HEATING_SETPOINTLIMIT_MIN,
        NumberDeviceClass.TEMPERATURE,
        "mdi:radiator",
        False,
        0,
        99,
        TENTH_STEP,
        NumberMode.BOX,
        UnitOfTemperature.CELSIUS,
    ],

    # A38 - Warmwasser
    "TEMPERATURE_WATER_SETPOINT": [
        "Temperature Hot Water setpoint",
        EcotouchTag.TEMPERATURE_WATER_SETPOINT,
        NumberDeviceClass.TEMPERATURE,
        "mdi:water-thermometer",
        True,
        10,
        70,
        TENTH_STEP,
        NumberMode.BOX,
        UnitOfTemperature.CELSIUS,
    ],
    "TEMPERATURE_WATER_HYSTERESIS": [
        "Temperature Hot Water Hysteresis",
        EcotouchTag.TEMPERATURE_WATER_HYSTERESIS,
        NumberDeviceClass.TEMPERATURE,
        "mdi:water-thermometer",
        True,
        0,
        10,
        TENTH_STEP,
        NumberMode.BOX,
        UnitOfTemperature.KELVIN,
    ],

    # Mischerkreis 1 Heizkennlinie
    # A276
    "TEMPERATURE_MIX1_HC_LIMIT": [
        "Temperature mixing circle 1 heating limit",
        EcotouchTag.TEMPERATURE_MIX1_HC_LIMIT,
        NumberDeviceClass.TEMPERATURE,
        "mdi:numeric-1-circle",
        False,
        5,
        35,
        TENTH_STEP,
        NumberMode.BOX,
        UnitOfTemperature.CELSIUS,
    ],
    # A277
    "TEMPERATURE_MIX1_HC_TARGET": [
        "Temperature mixing circle 1 heating limit target",
        EcotouchTag.TEMPERATURE_MIX1_HC_TARGET,
        NumberDeviceClass.TEMPERATURE,
        "mdi:numeric-1-circle",
        False,
        15,
        65,
        TENTH_STEP,
        NumberMode.BOX,
        UnitOfTemperature.CELSIUS,
    ],
    # A274
    "TEMPERATURE_MIX1_HC_OUTDOOR_NORM": [
        "Temperature mixing circle 1 norm outdoor",
        EcotouchTag.TEMPERATURE_MIX1_HC_OUTDOOR_NORM,
        NumberDeviceClass.TEMPERATURE,
        "mdi:numeric-1-circle",
        False,
        -99,
        99,
        TENTH_STEP,
        NumberMode.BOX,
        UnitOfTemperature.CELSIUS,
    ],
    # A275
    "TEMPERATURE_MIX1_HC_HEATING_NORM": [
        "Temperature mixing circle 1 norm heating circle",
        EcotouchTag.TEMPERATURE_MIX1_HC_HEATING_NORM,
        NumberDeviceClass.TEMPERATURE,
        "mdi:numeric-1-circle",
        False,
        0,
        99,
        TENTH_STEP,
        NumberMode.BOX,
        UnitOfTemperature.CELSIUS,
    ],
    # A278
    "TEMPERATURE_MIX1_HC_MAX": [
        "Temperature mixing circle 1 Limit for setpoint (Max.)",
        EcotouchTag.TEMPERATURE_MIX1_HC_MAX,
        NumberDeviceClass.TEMPERATURE,
        "mdi:numeric-1-circle",
        False,
        15,
        72,
        TENTH_STEP,
        NumberMode.BOX,
        UnitOfTemperature.CELSIUS,
    ],

    # Mischerkreis 2 Heizkennlinie
    "TEMPERATURE_MIX2_HC_LIMIT": [
        "Temperature mixing circle 2 heating limit",
        EcotouchTag.TEMPERATURE_MIX2_HC_LIMIT,
        NumberDeviceClass.TEMPERATURE,
        "mdi:numeric-2-circle",
        False,
        5,
        35,
        TENTH_STEP,
        NumberMode.BOX,
        UnitOfTemperature.CELSIUS,
    ],
    "TEMPERATURE_MIX2_HC_TARGET": [
        "Temperature mixing circle 2 heating limit target",
        EcotouchTag.TEMPERATURE_MIX2_HC_TARGET,
        NumberDeviceClass.TEMPERATURE,
        "mdi:numeric-2-circle",
        False,
        15,
        65,
        TENTH_STEP,
        NumberMode.BOX,
        UnitOfTemperature.CELSIUS,
    ],
    "TEMPERATURE_MIX2_HC_OUTDOOR_NORM": [
        "Temperature mixing circle 2 norm outdoor",
        EcotouchTag.TEMPERATURE_MIX2_HC_OUTDOOR_NORM,
        NumberDeviceClass.TEMPERATURE,
        "mdi:numeric-2-circle",
        False,
        -99,
        99,
        TENTH_STEP,
        NumberMode.BOX,
        UnitOfTemperature.CELSIUS,
    ],
    "TEMPERATURE_MIX2_HC_HEATING_NORM": [
        "Temperature mixing circle 2 norm heating circle",
        EcotouchTag.TEMPERATURE_MIX2_HC_HEATING_NORM,
        NumberDeviceClass.TEMPERATURE,
        "mdi:numeric-2-circle",
        False,
        0,
        99,
        TENTH_STEP,
        NumberMode.BOX,
        UnitOfTemperature.CELSIUS,
    ],
    "TEMPERATURE_MIX2_HC_MAX": [
        "Temperature mixing circle 2 Limit for setpoint (Max.)",
        EcotouchTag.TEMPERATURE_MIX2_HC_MAX,
        NumberDeviceClass.TEMPERATURE,
        "mdi:numeric-2-circle",
        False,
        15,
        72,
        TENTH_STEP,
        NumberMode.BOX,
        UnitOfTemperature.CELSIUS,
    ],

    # Mischerkreis 3 Heizkennlinie
    "TEMPERATURE_MIX3_HC_LIMIT": [
        "Temperature mixing circle 3 heating limit",
        EcotouchTag.TEMPERATURE_MIX3_HC_LIMIT,
        NumberDeviceClass.TEMPERATURE,
        "mdi:numeric-3-circle",
        False,
        5,
        35,
        TENTH_STEP,
        NumberMode.BOX,
        UnitOfTemperature.CELSIUS,
    ],
    "TEMPERATURE_MIX3_HC_TARGET": [
        "Temperature mixing circle 3 heating limit target",
        EcotouchTag.TEMPERATURE_MIX3_HC_TARGET,
        NumberDeviceClass.TEMPERATURE,
        "mdi:numeric-3-circle",
        False,
        15,
        65,
        TENTH_STEP,
        NumberMode.BOX,
        UnitOfTemperature.CELSIUS,
    ],
    "TEMPERATURE_MIX3_HC_OUTDOOR_NORM": [
        "Temperature mixing circle 3 norm outdoor",
        EcotouchTag.TEMPERATURE_MIX3_HC_OUTDOOR_NORM,
        NumberDeviceClass.TEMPERATURE,
        "mdi:numeric-3-circle",
        False,
        -99,
        99,
        TENTH_STEP,
        NumberMode.BOX,
        UnitOfTemperature.CELSIUS,
    ],
    "TEMPERATURE_MIX3_HC_HEATING_NORM": [
        "Temperature mixing circle 3 norm heating circle",
        EcotouchTag.TEMPERATURE_MIX3_HC_HEATING_NORM,
        NumberDeviceClass.TEMPERATURE,
        "mdi:numeric-3-circle",
        False,
        0,
        99,
        TENTH_STEP,
        NumberMode.BOX,
        UnitOfTemperature.CELSIUS,
    ],
    "TEMPERATURE_MIX3_HC_MAX": [
        "Temperature mixing circle 3 Limit for setpoint (Max.)",
        EcotouchTag.TEMPERATURE_MIX3_HC_MAX,
        NumberDeviceClass.TEMPERATURE,
        "mdi:numeric-3-circle",
        False,
        15,
        72,
        TENTH_STEP,
        NumberMode.BOX,
        UnitOfTemperature.CELSIUS,
    ],

    # Pool-Temperature Setpoint's
    "TEMPERATURE_POOL_SETPOINT": [
        "Temperature Pool setpoint",
        EcotouchTag.TEMPERATURE_POOL_SETPOINT,
        NumberDeviceClass.TEMPERATURE,
        "mdi:pool-thermometer",
        False,
        15,
        75,
        TENTH_STEP,
        NumberMode.BOX,
        UnitOfTemperature.CELSIUS,
    ],
    "TEMPERATURE_POOL_HYSTERESIS": [
        "Temperature Pool Hysteresis",
        EcotouchTag.TEMPERATURE_POOL_HYSTERESIS,
        NumberDeviceClass.TEMPERATURE,
        "mdi:pool-thermometer",
        False,
        0,
        10,
        TENTH_STEP,
        NumberMode.BOX,
        UnitOfTemperature.KELVIN,
    ],
    "TEMPERATURE_POOL_HC_LIMIT": [
        "Temperature Pool heating curve heating limit",
        EcotouchTag.TEMPERATURE_POOL_HC_LIMIT,
        NumberDeviceClass.TEMPERATURE,
        "mdi:pool",
        False,
        5,
        35,
        TENTH_STEP,
        NumberMode.BOX,
        UnitOfTemperature.CELSIUS,
    ],
    "TEMPERATURE_POOL_HC_TARGET": [
        "Temperature Pool heating curve heating limit target",
        EcotouchTag.TEMPERATURE_POOL_HC_TARGET,
        NumberDeviceClass.TEMPERATURE,
        "mdi:pool",
        False,
        15,
        65,
        TENTH_STEP,
        NumberMode.BOX,
        UnitOfTemperature.CELSIUS,
    ],
    "TEMPERATURE_POOL_HC_OUTDOOR_NORM": [
        "Temperature Pool heating curve norm outdoor",
        EcotouchTag.TEMPERATURE_POOL_HC_OUTDOOR_NORM,
        NumberDeviceClass.TEMPERATURE,
        "mdi:pool",
        False,
        -99,
        99,
        TENTH_STEP,
        NumberMode.BOX,
        UnitOfTemperature.CELSIUS,
    ],
    "TEMPERATURE_POOL_HC_NORM": [
        "Temperature Pool heating curve norm",
        EcotouchTag.TEMPERATURE_POOL_HC_NORM,
        NumberDeviceClass.TEMPERATURE,
        "mdi:pool",
        False,
        0,
        99,
        TENTH_STEP,
        NumberMode.BOX,
        UnitOfTemperature.CELSIUS,
    ],

    # Water disinfection start time & duration -> weekdays will be set in
    # switch.py
    "TEMPERATURE_WATER_DISINFECTION": [
        "Temperature Water disinfection",
        EcotouchTag.TEMPERATURE_WATER_DISINFECTION,
        NumberDeviceClass.TEMPERATURE,
        "mdi:shield-bug",
        False,
        60,
        70,
        TENTH_STEP,
        NumberMode.BOX,
        UnitOfTemperature.CELSIUS,
    ],
    # "SCHEDULE_WATER_DISINFECTION_START_HOUR": [
    #     "Water disinfection start time (hour)",
    #     EcotouchTag.SCHEDULE_WATER_DISINFECTION_START_HOUR,
    #     None, # time hh:mm (24h format)
    #     "mdi:clock-digital",
    #     False,
    #     0,
    #     23,
    #     DEFAULT_STEP,
    #     NumberMode.BOX,
    # ],
    # "SCHEDULE_WATER_DISINFECTION_START_MINUTE": [
    #     "Water disinfection start time (minute)",
    #     EcotouchTag.SCHEDULE_WATER_DISINFECTION_START_MINUTE,
    #     None, # time mm (24h format)
    #     "mdi:clock-digital",
    #     False,
    #     0,
    #     59,
    #     DEFAULT_STEP,
    #     NumberMode.BOX,
    # ],
    "SCHEDULE_WATER_DISINFECTION_DURATION": [
        "Water disinfection duration (in hours)",
        EcotouchTag.SCHEDULE_WATER_DISINFECTION_DURATION,
        None,  # duration in h
        "mdi:progress-clock",
        False,
        0,
        23,
        DEFAULT_STEP,
        NumberMode.SLIDER,
        UnitOfTime.HOURS,
    ],

    "SOURCE_PUMP_CAPTURE_TEMPERATURE_A479": [
        "Heat source pump - ΔT heat source",
        EcotouchTag.SOURCE_PUMP_CAPTURE_TEMPERATURE_A479,
        NumberDeviceClass.TEMPERATURE,
        "mdi:thermometer",
        False,
        0,
        40,
        TENTH_STEP,
        NumberMode.BOX,
        UnitOfTemperature.KELVIN,
    ],
}

TEMP_ADJUST_LOOKUP = [-2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2]


async def async_setup_entry(
        hass: HomeAssistantType, entry: ConfigType, async_add_devices
) -> None:
    """Set up the Waterkotte Number platform."""
    _LOGGER.debug("Number async_setup_entry")
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices([WaterkotteHeatpumpNumber(entry, coordinator, sensor_type)
                       for sensor_type in SENSOR_TYPES])


class WaterkotteHeatpumpNumber(NumberEntity, WaterkotteHeatpumpEntity):
    """waterkotte_heatpump Number class."""

    def __init__(self, entry, hass_data, sensor_type):  # pylint: disable=unused-argument
        """Initialize the sensor."""
        self.entity_id = f"{DOMAIN}.wkh_{sensor_type}"
        self._coordinator = hass_data
        self._type = sensor_type
        self._attr_unique_id = sensor_type
        self._entry_data = entry.data
        self._device_id = entry.entry_id
        self._attr_translation_key = self._type.lower()
        if len(SENSOR_TYPES[self._type]) > 9:
            self._attr_native_unit_of_measurement = SENSOR_TYPES[self._type][9]
        super().__init__(hass_data, entry)

    @property
    def native_value(self) -> float | None:
        # this will be called, if the value is READ -> and so the
        # data will be converted to the display value
        try:
            value = self._coordinator.data[self.eco_tag]["value"]
            if value is None or value == "":
                return "unknown"
            if str(self.eco_tag.name).upper().endswith("_ADJUST"):
                value = TEMP_ADJUST_LOOKUP[value]
            # if(self.tag[0][0][0] == 'I'):
            #    _LOGGER.warning("native_value "+str(value))
        except KeyError:
            return "unknown"
        except TypeError:
            return None
        return float(value)
        # return "auto"

    async def async_set_native_value(self, value: float) -> None:
        """Turn on the switch."""
        try:
            if str(self.eco_tag.name).upper().endswith("_ADJUST"):
                value = TEMP_ADJUST_LOOKUP.index(value)
            if self.eco_tag[0][0][0] == 'I':
                value = int(value)
            await self._coordinator.async_write_tag(self.eco_tag, value)
        except ValueError:
            return "unavailable"

    @property
    def eco_tag(self):
        """Return a unique ID to use for this entity."""
        return SENSOR_TYPES[self._type][1]

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return SENSOR_TYPES[self._type][2]

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return SENSOR_TYPES[self._type][3]

    @property
    def entity_registry_enabled_default(self):
        """Return the entity_registry_enabled_default of the sensor."""
        return SENSOR_TYPES[self._type][4]

    @property
    def native_min_value(self):
        """Return the minimum value."""
        return SENSOR_TYPES[self._type][5]

    @property
    def native_max_value(self):
        """Return the maximum value."""
        return SENSOR_TYPES[self._type][6]

    @property
    def native_step(self):
        """Return the native Step."""
        try:
            return SENSOR_TYPES[self._type][7]
        except IndexError:
            return None

    @property
    def mode(self):
        """Return the native Mode."""
        try:
            return SENSOR_TYPES[self._type][8]
        except IndexError:
            return NumberMode.AUTO

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
