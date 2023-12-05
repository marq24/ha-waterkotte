"""Sensor platform for Waterkotte Heatpump."""
import logging

# from homeassistant.helpers.entity import Entity, EntityCategory  # , DeviceInfo
from homeassistant.components.number import NumberEntity, NumberDeviceClass
from homeassistant.helpers.typing import ConfigType, HomeAssistantType

# from .const import DEFAULT_NAME


# from .const import ICON
# from .const import SENSOR

#  from .const import UnitOfTemperature


# from homeassistant.const import (
#    ATTR_ATTRIBUTION,
# DEGREE,
#    DEVICE_CLASS_HUMIDITY,
# DEVICE_CLASS_PRESSURE,
# DEVICE_CLASS_TEMPERATURE,
#    LENGTH_KILOMETERS,
# PRESSURE_HPA,
# PRESSURE_BAR,
# SPEED_KILOMETERS_PER_HOUR,
# TEMP_CELSIUS,
#    TIME_SECONDS,
# )
from pywaterkotte.ecotouch import EcotouchTag
from .entity import WaterkotteHeatpumpEntity

from .const import ENUM_OFFAUTOMANUAL, DEVICE_CLASS_ENUM, DOMAIN

_LOGGER = logging.getLogger(__name__)
_LANG = None

# Sensor types are defined as:
#   variable -> [0]title, [1] EcoTouchTag, [2]device_class, [3]min, [4]icon, [5]enabled_by_default, [6]max, [7]step #pylint: disable=line-too-long
SENSOR_TYPES = {
    "adapt_heating": [
        "Temperature Heating Adapt",
        EcotouchTag.ADAPT_HEATING,
        NumberDeviceClass.TEMPERATURE,
        -2,
        "mdi:snowflake-thermometer",
        True,
        2,
        0.5,
    ],
    # "temperature_heating_set2": [
    #     "Temperature Heating Set2",
    #     EcotouchTag.TEMPERATURE_HEATING_SET2,
    #     NumberDeviceClass.TEMPERATURE,
    #     0,
    #     "mdi:snowflake-thermometer",
    #     True,
    #     100,
    #     0.1,
    # ],
    "nvi_soll_kuehlen": [
        "Temperature Cooling Set",
        EcotouchTag.NVI_SOLL_KUEHLEN,
        NumberDeviceClass.TEMPERATURE,
        5,
        "mdi:snowflake-thermometer",
        True,
        26,
        0.5,
    ],
    # "temperature_cooling_set2": [
    #     "Temperature Cooling Set2",
    #     EcotouchTag.TEMPERATURE_COOLING_SET2,
    #     NumberDeviceClass.TEMPERATURE,
    #     0,
    #     "mdi:snowflake-thermometer",
    #     True,
    #     100,
    #     0.1,
    # ],
    # "temperature_water_setpoint": [
    #     "Temperature Water Setpoint",
    #     EcotouchTag.TEMPERATURE_WATER_SETPOINT,
    #     NumberDeviceClass.TEMPERATURE,
    #     0,
    #     "mdi:snowflake-thermometer",
    #     True,
    #     100,
    #     0.1,
    # ],
    "temperature_water_setpoint2": [
        "Temperature Water Setpoint2",
        EcotouchTag.TEMPERATURE_WATER_SETPOINT2,
        NumberDeviceClass.TEMPERATURE,
        28,
        "mdi:snowflake-thermometer",
        True,
        70,
        0.5,
    ],
    "temperature_pool_setpoint": [
        "Temperature Pool Setpoint",
        EcotouchTag.TEMPERATURE_POOL_SETPOINT,
        NumberDeviceClass.TEMPERATURE,
        0,
        "mdi:snowflake-thermometer",
        False,
        100,
        0.1,
    ],
    "temperature_pool_setpoint2": [
        "Temperature Pool Setpoint2",
        EcotouchTag.TEMPERATURE_POOL_SETPOINT2,
        DEVICE_CLASS_ENUM,
        0,
        "mdi:snowflake-thermometer",
        False,
        100,
        0.1,
    ],
    "temperature_mixing1_set": [
        "Temperature Mixing1 Set",
        EcotouchTag.TEMPERATURE_MIXING1_SET,
        NumberDeviceClass.TEMPERATURE,
        0,
        "mdi:snowflake-thermometer",
        False,
        100,
        0.1,
    ],
    "temperature_mixing2_set": [
        "Temperature Mixing2 Set",
        EcotouchTag.TEMPERATURE_MIXING2_SET,
        NumberDeviceClass.TEMPERATURE,
        0,
        "mdi:snowflake-thermometer",
        False,
        100,
        0.1,
    ],
    "temperature_mixing3_set": [
        "Temperature Mixing3 Set",
        EcotouchTag.TEMPERATURE_MIXING3_SET,
        NumberDeviceClass.TEMPERATURE,
        0,
        "mdi:snowflake-thermometer",
        False,
        100,
        0.1,
    ],
    "adapt_mixing1": [
        "Adapt Mixing1",
        EcotouchTag.ADAPT_MIXING1,
        NumberDeviceClass.TEMPERATURE,
        -2,
        "mdi:snowflake-thermometer",
        False,
        2,
        0.5,
    ],
    "adapt_mixing2": [
        "Adapt Mixing2",
        EcotouchTag.ADAPT_MIXING2,
        NumberDeviceClass.TEMPERATURE,
        -2,
        "mdi:snowflake-thermometer",
        False,
        2,
        0.5,
    ],
    "adapt_mixing3": [
        "Adapt Mixing3",
        EcotouchTag.ADAPT_MIXING3,
        NumberDeviceClass.TEMPERATURE,
        -2,
        "mdi:snowflake-thermometer",
        False,
        2,
        0.5,
    ],

    "t_heating_limit_mixing1": [
        "T Heating limit Mixing 1",
        EcotouchTag.T_HEATING_LIMIT_MIXING1,
        NumberDeviceClass.TEMPERATURE,
        0,
        None,
        False,
        100,
        0.1,
    ],
    "t_heating_limit_target_mixing1": [
        "T Heating limit target Mixing 1",
        EcotouchTag.T_HEATING_LIMIT_TARGET_MIXING1,
        NumberDeviceClass.TEMPERATURE,
        0,
        None,
        False,
        100,
        0.1,
    ],
    "t_norm_outdoor_mixing1": [
        "T norm outdoor Mixing 1",
        EcotouchTag.T_NORM_OUTDOOR_MIXING1,
        NumberDeviceClass.TEMPERATURE,
        -15,
        None,
        False,
        50,
        0.1,
    ],
    "t_norm_heating_circle_mixing1": [
        "T norm heating circle Mixing 1",
        EcotouchTag.T_HEATING_LIMIT_MIXING1,
        NumberDeviceClass.TEMPERATURE,
        0,
        None,
        False,
        100,
        0.1,
    ],
    "max_temp_mixing1": [
        "Max temperature in Mixing 1",
        EcotouchTag.MAX_TEMP_MIXING1,
        NumberDeviceClass.TEMPERATURE,
        0,
        None,
        False,
        100,
        0.1,
    ],

    "t_heating_limit_mixing2": [
        "T Heating limit Mixing 2",
        EcotouchTag.T_HEATING_LIMIT_MIXING2,
        NumberDeviceClass.TEMPERATURE,
        0,
        None,
        False,
        100,
        0.1,
    ],
    "t_heating_limit_target_mixing2": [
        "T Heating limit target Mixing 2",
        EcotouchTag.T_HEATING_LIMIT_TARGET_MIXING2,
        NumberDeviceClass.TEMPERATURE,
        0,
        None,
        False,
        100,
        0.1,
    ],
    "t_norm_outdoor_mixing2": [
        "T norm outdoor Mixing 2",
        EcotouchTag.T_NORM_OUTDOOR_MIXING2,
        NumberDeviceClass.TEMPERATURE,
        -15,
        None,
        False,
        50,
        0.1,
    ],
    "t_norm_heating_circle_mixing2": [
        "T norm heating circle Mixing 2",
        EcotouchTag.T_HEATING_LIMIT_MIXING2,
        NumberDeviceClass.TEMPERATURE,
        0,
        None,
        False,
        100,
        0.1,
    ],
    "max_temp_mixing2": [
        "Max temperature in Mixing 2",
        EcotouchTag.MAX_TEMP_MIXING2,
        NumberDeviceClass.TEMPERATURE,
        0,
        None,
        False,
        100,
        0.1,
    ],

    "t_heating_limit_mixing3": [
        "T Heating limit Mixing 3",
        EcotouchTag.T_HEATING_LIMIT_MIXING3,
        NumberDeviceClass.TEMPERATURE,
        0,
        None,
        False,
        100,
        0.1,
    ],
    "t_heating_limit_target_mixing3": [
        "T Heating limit target Mixing 3",
        EcotouchTag.T_HEATING_LIMIT_TARGET_MIXING3,
        NumberDeviceClass.TEMPERATURE,
        0,
        None,
        False,
        100,
        0.1,
    ],
    "t_norm_outdoor_mixing3": [
        "T norm outdoor Mixing 3",
        EcotouchTag.T_NORM_OUTDOOR_MIXING3,
        NumberDeviceClass.TEMPERATURE,
        -15,
        None,
        False,
        50,
        0.1,
    ],
    "t_norm_heating_circle_mixing3": [
        "T norm heating circle Mixing 3",
        EcotouchTag.T_HEATING_LIMIT_MIXING3,
        NumberDeviceClass.TEMPERATURE,
        0,
        None,
        False,
        100,
        0.1,
    ],
    "max_temp_mixing3": [
        "Max temperature in Mixing 3",
        EcotouchTag.MAX_TEMP_MIXING3,
        NumberDeviceClass.TEMPERATURE,
        0,
        None,
        False,
        100,
        0.1,
    ],
}

ADAPT_LOOKUP = [-2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2]


async def async_setup_entry(
    hass: HomeAssistantType, entry: ConfigType, async_add_devices
) -> None:
    """Set up the Waterkotte sensor platform."""
    # hass_data = hass.data[DOMAIN][entry.entry_id]
    _LOGGER.debug("Sensor async_setup_entry")
    coordinator = hass.data[DOMAIN][entry.entry_id]
    global _LANG
    _LANG = coordinator.lang
    # async_add_devices([WaterkotteHeatpumpSensor(entry, coordinator, "temperature_condensation")])
    # async_add_devices([WaterkotteHeatpumpSensor(entry, coordinator, "temperature_evaporation")])
    async_add_devices(
        [
            WaterkotteHeatpumpSelect(entry, coordinator, sensor_type)
            for sensor_type in SENSOR_TYPES
        ]
    )


class WaterkotteHeatpumpSelect(NumberEntity, WaterkotteHeatpumpEntity):
    """waterkotte_heatpump Sensor class."""

    def __init__(
        self, entry, hass_data, sensor_type
    ):  # pylint: disable=unused-argument
        """Initialize the sensor."""
        self._coordinator = hass_data

        self._type = sensor_type
        # self._name = f"{SENSOR_TYPES[self._type][0]} {DOMAIN}"
        self._name = f"{SENSOR_TYPES[self._type][0]}"
        self._name = _LANG[SENSOR_TYPES[self._type][1].tags[0]]
        # self._unique_id = f"{SENSOR_TYPES[self._type][0]}_{DOMAIN}"
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
    def native_value(self) -> float | None:
        try:
            sensor = SENSOR_TYPES[self._type]
            value = self._coordinator.data[sensor[1]]["value"]
            if value is None or value == "":
                return "unknown"
            if self._type == "adapt_heating":
                value = ADAPT_LOOKUP[value]
        except KeyError:
            return "unknown"
        except TypeError:
            return None
        return float(value)
        # return "auto"

    # @property
    # def native_uni(self) -> str:
    #     # return ["off", "auto", "manual"]
    #     return SENSOR_TYPES[self._type][6]

    async def async_set_native_value(self, value: float) -> None:
        """Turn on the switch."""
        try:
            # print(option)
            # await self._coordinator.api.async_write_value(SENSOR_TYPES[self._type][1], option)
            if self._type == "adapt_heating":
                value = ADAPT_LOOKUP.index(value)
            await self._coordinator.async_write_tag(SENSOR_TYPES[self._type][1], value)
        except ValueError:
            return "unavailable"

    @property
    def tag(self):
        """Return a unique ID to use for this entity."""
        return SENSOR_TYPES[self._type][1]

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
    def native_step(self):
        """Return the native Step."""
        try:
            return SENSOR_TYPES[self._type][7]
        except IndexError:
            return None

    @property
    def unique_id(self):
        """Return the unique of the sensor."""
        return self._unique_id

    @property
    def native_min_value(self):
        """Return the minimum value."""
        return SENSOR_TYPES[self._type][3]

    @property
    def native_max_value(self):
        """Return the maximum value."""
        return SENSOR_TYPES[self._type][6]

    async def async_update(self):
        """Schedule a custom update via the common entity update service."""
        await self._coordinator.async_request_refresh()

    @property
    def should_poll(self) -> bool:
        """Entities do not individually poll."""
        return False
