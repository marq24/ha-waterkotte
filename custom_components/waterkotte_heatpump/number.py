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


# Sensor types are defined as:
#   variable -> [0]title, [1] EcoTouchTag, [2]device_class, [3]min, [4]icon, [5]enabled_by_default, [6]max, [7]step #pylint: disable=line-too-long
SENSOR_TYPES = {
    "temperature_heating_set": [
        "Temperature Heating Set",
        EcotouchTag.TEMPERATURE_HEATING_SET,
        NumberDeviceClass.TEMPERATURE,
        0,
        "mdi:snowflake-thermometer",
        True,
        100,
        0.1,
    ],
    "temperature_heating_set2": [
        "Temperature Heating Set2",
        EcotouchTag.TEMPERATURE_HEATING_SET2,
        NumberDeviceClass.TEMPERATURE,
        0,
        "mdi:snowflake-thermometer",
        True,
        100,
        0.1,
    ],
    "temperature_cooling_set": [
        "Temperature Cooling Set",
        EcotouchTag.TEMPERATURE_COOLING_SET,
        NumberDeviceClass.TEMPERATURE,
        0,
        "mdi:snowflake-thermometer",
        True,
        100,
        0.1,
    ],
    "temperature_cooling_set2": [
        "Temperature Cooling Set2",
        EcotouchTag.TEMPERATURE_COOLING_SET2,
        NumberDeviceClass.TEMPERATURE,
        0,
        "mdi:snowflake-thermometer",
        True,
        100,
        0.1,
    ],
    "temperature_water_setpoint": [
        "Temperature Water Setpoint",
        EcotouchTag.TEMPERATURE_WATER_SETPOINT,
        NumberDeviceClass.TEMPERATURE,
        0,
        "mdi:snowflake-thermometer",
        True,
        100,
        0.1,
    ],
    "temperature_water_setpoint2": [
        "Temperature Water Setpoint2",
        EcotouchTag.TEMPERATURE_WATER_SETPOINT2,
        NumberDeviceClass.TEMPERATURE,
        0,
        "mdi:snowflake-thermometer",
        True,
        100,
        0.1,
    ],
    "temperature_pool_setpoint": [
        "Temperature Pool Setpoint",
        EcotouchTag.TEMPERATURE_POOL_SETPOINT,
        NumberDeviceClass.TEMPERATURE,
        0,
        "mdi:snowflake-thermometer",
        True,
        100,
        0.1,
    ],
    "temperature_pool_setpoint2": [
        "Temperature Pool Setpoint2",
        EcotouchTag.TEMPERATURE_POOL_SETPOINT2,
        DEVICE_CLASS_ENUM,
        0,
        "mdi:snowflake-thermometer",
        True,
        100,
        0.1,
    ],
}
"""

    TEMPERATURE_HEATING_SET = TagData(["A31"], "°C")
    TEMPERATURE_HEATING_SET2 = TagData(["A32"], "°C")
    TEMPERATURE_COOLING_SET = TagData(["A34"], "°C")
    TEMPERATURE_COOLING_SET2 = TagData(["A35"], "°C")
    TEMPERATURE_WATER_SETPOINT = TagData(["A37"], "°C", writeable=True)
    TEMPERATURE_WATER_SETPOINT2 = TagData(["A38"], "°C", writeable=True)
    TEMPERATURE_POOL_SETPOINT = TagData(["A40"], "°C", writeable=True)
    TEMPERATURE_POOL_SETPOINT2 = TagData(["A41"], "°C", writeable=True)
    COMPRESSOR_POWER = TagData(["A50"], "?°C")

    HYSTERESIS_HEATING = TagData(["A61"], "?")

    NVI_NORM_AUSSEN = TagData(["A91"], "?")
    NVI_HEIZKREIS_NORM = TagData(["A92"], "?")
    NVI_T_HEIZGRENZE = TagData(["A93"], "?°C")
    NVI_T_HEIZGRENZE_SOLL = TagData(["A94"], "?°C")
    MAX_VL_TEMP = TagData(["A95"], "°C")
    TEMP_SET_0_DEG = TagData(["A97"], "°C")
    COOL_ENABLE_TEMP = TagData(["A108"], "°C")
    NVI_SOLL_KUEHLEN = TagData(["A109"], "°C")
    TEMPCHANGE_HEATING_PV = TagData(["A682"], "°C")
    TEMPCHANGE_COOLING_PV = TagData(["A683"], "°C")
    TEMPCHANGE_WARMWATER_PV = TagData(["A684"], "°C")
    TEMPCHANGE_POOL_PV = TagData(["A685"], "°C")

    DATE_DAY = TagData(["I5"])
    DATE_MONTH = TagData(["I6"])
    DATE_YEAR = TagData(["I7"])
    TIME_HOUR = TagData(["I8"])
    TIME_MINUTE = TagData(["I9"])
    OPERATING_HOURS_COMPRESSOR_1 = TagData(["I10"])
    OPERATING_HOURS_COMPRESSOR_2 = TagData(["I14"])
    OPERATING_HOURS_CIRCULATION_PUMP = TagData(["I18"])
    OPERATING_HOURS_SOURCE_PUMP = TagData(["I20"])
    OPERATING_HOURS_SOLAR = TagData(["I22"])

    ALARM = TagData(["I52"])
    INTERRUPTIONS = TagData(["I53"])
    ADAPT_HEATING = TagData(["I263"], writeable=True)
    MANUAL_HEATINGPUMP = TagData(["I1270"])
    MANUAL_SOURCEPUMP = TagData(["I1281"])
    MANUAL_SOLARPUMP1 = TagData(["I1287"])
    MANUAL_SOLARPUMP2 = TagData(["I1289"])
    MANUAL_TANKPUMP = TagData(["I1291"])
    MANUAL_VALVE = TagData(["I1293"])
    MANUAL_POOLVALVE = TagData(["I1295"])
    MANUAL_COOLVALVE = TagData(["I1297"])
    MANUAL_4WAYVALVE = TagData(["I1299"])
    MANUAL_MULTIEXT = TagData(["I1319"]) """


async def async_setup_entry(
    hass: HomeAssistantType, entry: ConfigType, async_add_devices
) -> None:
    """Set up the Waterkotte sensor platform."""
    # hass_data = hass.data[DOMAIN][entry.entry_id]
    _LOGGER.debug("Sensor async_setup_entry")
    coordinator = hass.data[DOMAIN][entry.entry_id]
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
