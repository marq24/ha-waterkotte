"""Sensor platform for Waterkotte Heatpump."""
import logging
# from homeassistant.helpers.entity import Entity, EntityCategory  # , DeviceInfo
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.typing import ConfigType, HomeAssistantType

# from .const import DEFAULT_NAME


# from .const import ICON
# from .const import SENSOR

#  from .const import UnitOfTemperature


from homeassistant.const import (
    #    ATTR_ATTRIBUTION,
    DEVICE_CLASS_DATE,
    #    DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_PRESSURE,
    DEVICE_CLASS_TEMPERATURE,
    #    LENGTH_KILOMETERS,
    # PRESSURE_HPA,
    PRESSURE_BAR,
    SPEED_KILOMETERS_PER_HOUR,
    TEMP_CELSIUS,
    #    TIME_SECONDS,
)
from .entity import WaterkotteHeatpumpEntity
from .pywaterkotte.ecotouch import EcotouchTag
from .const import DOMAIN  # ENUM_ONOFFAUTO, DEVICE_CLASS_ENUM,  # , NAME, CONF_FW, CONF_BIOS, CONF_IP

_LOGGER = logging.getLogger(__name__)


# Sensor types are defined as:
#   variable -> [0]title, [1]device_class, [2]units, [3]icon, [4]enabled_by_default, [5]options, [6]entity_category
#   variable -> [0]title, [1] EcoTouchTag, [2]device_class, [3]units, [4]icon, [5]enabled_by_default, [6]options, [7]entity_category
SENSOR_TYPES = {
    "status_heating": [
        "Status Heating",
        EcotouchTag.STATUS_HEATING,
        None,
        None,
        "mdi:weather-windy",
        True,
        None,
        None,
    ],
    "status_water": [
        "Status Water",
        EcotouchTag.STATUS_WATER,
        None,
        None,
        "mdi:weather-rainy",
        True,
        None,
        None,
    ],
    "status_cooling": [
        "Status Cooling",
        EcotouchTag.STATUS_COOLING,
        None,
        None,
        "mdi:weather-rainy",
        True,
        None,
        None,
    ],
    "temperature_outside": [
        "Temperature Outside",
        EcotouchTag.TEMPERATURE_OUTSIDE,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        True,
        None,
        None,
    ],
    "temperature_outside_1h": [
        "Temperature Outside 1h",
        EcotouchTag.TEMPERATURE_OUTSIDE_1H,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        True,
        None,
        None,
    ],
    "temperature_outside_24h": [
        "Temperature Outside 24h",
        EcotouchTag.TEMPERATURE_OUTSIDE_24H,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        True,
        None,
        None,
    ],
    "temperature_source_in": [
        "Temperature Source In",
        EcotouchTag.TEMPERATURE_SOURCE_IN,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        True,
        None,
        None,
    ],
    "temperature_source_out": [
        "Temperature Source Out",
        EcotouchTag.TEMPERATURE_SOURCE_OUT,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        True,
        None,
        None,
    ],
    "temperature_evaporation": [
        "Temperature Evaporation",
        EcotouchTag.TEMPERATURE_EVAPORATION,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        True,
        None,
        None,
    ],
    "temperature_suction": [
        "Temperature Suction",
        EcotouchTag.TEMPERATURE_SUCTION,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        True,
        None,
        None,
    ],
    "temperature_return_set": [
        "Temperature Return Set",
        EcotouchTag.TEMPERATURE_RETURN_SET,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        True,
        None,
        None,
    ],
    "temperature_return": [
        "Temperature Return",
        EcotouchTag.TEMPERATURE_RETURN,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        True,
        None,
        None,
    ],
    "temperature_flow": [
        "Temperature Flow",
        EcotouchTag.TEMPERATURE_FLOW,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        True,
        None,
        None,
    ],
    "temperature_condensation": [
        "Temperature Condensation",
        EcotouchTag.TEMPERATURE_CONDENSATION,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        True,
        None,
        None,
    ],
    "temperature_storage": [
        "Temperature Storage",
        EcotouchTag.TEMPERATURE_STORAGE,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        True,
        None,
        None,
    ],
    "temperature_room": [
        "Temperature Room",
        EcotouchTag.TEMPERATURE_ROOM,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        False,
        None,
        None,
    ],
    "temperature_room_1h": [
        "Temperature Room 1h",
        EcotouchTag.TEMPERATURE_ROOM_1H,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        False,
        None,
        None,
    ],
    "temperature_water": [
        "Temperature Water",
        EcotouchTag.TEMPERATURE_WATER,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        True,
        None,
        None,
    ],
    "temperature_pool": [
        "Temperature Pool",
        EcotouchTag.TEMPERATURE_POOL,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        False,
        None,
        None,
    ],
    "temperature_solar": [
        "Temperature Solar",
        EcotouchTag.TEMPERATURE_SOLAR,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        False,
        None,
        None,
    ],
    "temperature_solar_flow": [
        "Temperature Solar Flow",
        EcotouchTag.TEMPERATURE_SOLAR_FLOW,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        False,
        None,
        None,
    ],
    "temperature_heating_return": [
        "Temperature Heating Return",
        EcotouchTag.TEMPERATURE_HEATING_RETURN,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        False,
        None,
        None,
    ],
    "temperature_cooling_return": [
        "Temperature Cooling Return",
        EcotouchTag.TEMPERATURE_COOLING_RETURN,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        False,
        None,
        None,
    ],
    "temperature2_outside_1h": [  # TEMPERATURE2_OUTSIDE_1H = TagData(["A90"], "°C")
        "Temperature2 Outside 1h",
        EcotouchTag.TEMPERATURE2_OUTSIDE_1H,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        False,
        None,
        None,
    ],
    "pressure_evaporation": [
        "Pressure Evaporation",
        EcotouchTag.PRESSURE_EVAPORATION,
        DEVICE_CLASS_PRESSURE,
        PRESSURE_BAR,
        "mdi:gauge",
        False,
        None,
        None,
    ],
    "pressure_condensation": [
        "Pressure Condensation",
        EcotouchTag.PRESSURE_CONDENSATION,
        DEVICE_CLASS_PRESSURE,
        PRESSURE_BAR,
        "mdi:gauge",
        False,
        None,
        None,
    ],
    "position_expansion_valve": [
        "Position Expansion Valve",
        EcotouchTag.POSITION_EXPANSION_VALVE,
        DEVICE_CLASS_PRESSURE,
        PRESSURE_BAR,
        "mdi:gauge",
        False,
        None,
        None,
    ],
    "power_compressor": [
        "Power Compressor",
        EcotouchTag.POWER_COMPRESSOR,
        DEVICE_CLASS_PRESSURE,
        PRESSURE_BAR,
        "mdi:gauge",
        False,
        None,
        None,
    ],
    "power_heating": [
        "Power Heating",
        EcotouchTag.POWER_HEATING,
        DEVICE_CLASS_PRESSURE,
        PRESSURE_BAR,
        "mdi:gauge",
        False,
        None,
        None,
    ],
    "power_cooling": [
        "Power Cooling",
        EcotouchTag.POWER_COOLING,
        DEVICE_CLASS_PRESSURE,
        PRESSURE_BAR,
        "mdi:gauge",
        False,
        None,
        None,
    ],
    "cop_heating": [
        "COP Heating",
        EcotouchTag.COP_HEATING,
        DEVICE_CLASS_PRESSURE,
        PRESSURE_BAR,
        "mdi:gauge",
        False,
        None,
        None,
    ],
    "cop_cooling": [
        "COP Cooling",
        EcotouchTag.COP_COOLING,
        DEVICE_CLASS_PRESSURE,
        PRESSURE_BAR,
        "mdi:gauge",
        False,
        None,
        None,
    ],
    "percent_heat_circ_pump": [
        "Percent Heat Circ Pump",
        EcotouchTag.PERCENT_HEAT_CIRC_PUMP,
        DEVICE_CLASS_PRESSURE,
        PRESSURE_BAR,
        "mdi:gauge",
        False,
        None,
        None,
    ],
    "percent_source_pump": [
        "Percent Source Pump",
        EcotouchTag.PERCENT_SOURCE_PUMP,
        DEVICE_CLASS_PRESSURE,
        PRESSURE_BAR,
        "mdi:gauge",
        False,
        None,
        None,
    ],
    "percent_compressor": [
        "Percent Compressor",
        EcotouchTag.PERCENT_COMPRESSOR,
        DEVICE_CLASS_PRESSURE,
        PRESSURE_BAR,
        "mdi:gauge",
        False,
        None,
        None,
    ],
    "holiday_start_time": [
        "Holiday start",
        EcotouchTag.HOLIDAY_START_TIME,
        DEVICE_CLASS_DATE,
        PRESSURE_BAR,
        "mdi:calendar-arrow-right",
        True,
        None,
        None,
    ],
    "holiday_end_time": [
        "Holiday end",
        EcotouchTag.HOLIDAY_END_TIME,
        DEVICE_CLASS_DATE,
        PRESSURE_BAR,
        "mdi:calendar-arrow-left",
        True,
        None,
        None,
    ],
    "state_service": [
        "State Service",
        EcotouchTag.STATE_SERVICE,
        DEVICE_CLASS_DATE,
        PRESSURE_BAR,
        None,
        True,
        None,
        None,
    ],
    "temperature_heating_set": [
        "Temperature Heating Demand",
        EcotouchTag.TEMPERATURE_HEATING_SET,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        False,
        None,
        None,
    ],
    "temperature_heating_set2": [
        "Temperature Heating Temperatur(set2)",
        EcotouchTag.TEMPERATURE_HEATING_SET2,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        False,
        None,
        None,
    ],
    "temperature_cooling_set": [
        "Temperature Cooling Demand",
        EcotouchTag.TEMPERATURE_COOLING_SET,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        False,
        None,
        None,
    ],
    "temperature_cooling_set2": [
        "Temperature Cooling Temperatur(set2)",
        EcotouchTag.TEMPERATURE_COOLING_SET2,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        False,
        None,
        None,
    ],
    "compressor_power": [
        "Compressor Power",
        EcotouchTag.COMPRESSOR_POWER,
        None,
        None,
        "mdi:thermometer",
        False,
        None,
        None,
    ],
    "temperature_norm_outdoor": [
        "Temperature norm outdoor",
        EcotouchTag.NVI_NORM_AUSSEN,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        False,
        None,
        None,
    ],
    "temperature_norm_heating_circle": [
        "Temperature norm heating circle",
        EcotouchTag.NVI_HEIZKREIS_NORM,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        False,
        None,
        None,
    ],
    "temperature_heating_limit": [
        "Temperature heating limit",
        EcotouchTag.NVI_T_HEIZGRENZE,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        False,
        None,
        None,
    ],
    "temperature_heating_limit_target": [
        "Temperature heating limit target",
        EcotouchTag.NVI_T_HEIZGRENZE_SOLL,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        False,
        None,
        None,
    ],
    "temperature_max_heating": [
        "Limit for setpoint (Max.)",
        EcotouchTag.MAX_VL_TEMP,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        False,
        None,
        None,
    ],
    "temperature_out_begin": [
        "Temperature enable Cooling",
        EcotouchTag.COOL_ENABLE_TEMP,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        False,
        None,
        None,
    ],
    "temperature_cooling": [
        "Temperature Cooling",
        EcotouchTag.NVI_SOLL_KUEHLEN,
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        False,
        None,
        None,
    ],

}
"""

    TEMPERATURE_WATER_SETPOINT = TagData(["A37"], "°C", writeable=True)
    TEMPERATURE_WATER_SETPOINT2 = TagData(["A38"], "°C", writeable=True)
    TEMPERATURE_POOL_SETPOINT = TagData(["A40"], "°C", writeable=True)
    TEMPERATURE_POOL_SETPOINT2 = TagData(["A41"], "°C", writeable=True)
    COMPRESSOR_POWER = TagData(["A50"], "?°C")

    HYSTERESIS_HEATING = TagData(["A61"], "?") # Hysteresis setpoint
    TEMP_SET_0_DEG = TagData(["A97"], "°C")

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


# async def async_setup_entry(hass: HomeAssistantType, entry: ConfigType, async_add_entities) -> None:
async def async_setup_entry(hass: HomeAssistantType, entry: ConfigType, async_add_devices) -> None:
    """Set up the Waterkotte sensor platform."""

    _LOGGER.debug("Sensor async_setup_entry")
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices([WaterkotteHeatpumpSensor(entry, coordinator, sensor_type)
                       for sensor_type in SENSOR_TYPES])


class WaterkotteHeatpumpSensor(SensorEntity, WaterkotteHeatpumpEntity):
    """waterkotte_heatpump Sensor class."""

    def __init__(self, entry, hass_data, sensor_type):  # pylint: disable=unused-argument
        """Initialize the sensor."""
        # super().__init__(self, hass_data)
        self._coordinator = hass_data

        self._type = sensor_type
        self._name = f"{SENSOR_TYPES[self._type][0]}"
        self._unique_id = self._type
        self._entry_data = entry.data
        self._device_id = entry.entry_id

        super().__init__(hass_data, entry)

    @ property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @ property
    def state(self):
        """Return the state of the sensor."""
        # result = ""
        # print(self._coordinator.data)
        try:
            sensor = SENSOR_TYPES[self._type]
            value = self._coordinator.data[sensor[1]]["value"]
            if value is None or value == "":
                value = 'unknown'
        except KeyError:
            value = "unknown"

        if value is True:
            value = "on"
        elif value is False:
            value = "off"
        return value

        # try:
        #     if self._type == "enable_heating":
        #         result = self._coordinator.data[EcotouchTag.ENABLE_HEATING]["value"]
        #     elif self._type == "enable_cooling":
        #         result = self._coordinator.data[EcotouchTag.ENABLE_COOLING]["value"]
        #     elif self._type == "enable_warmwater":
        #         result = self._coordinator.data[EcotouchTag.ENABLE_WARMWATER]["value"]
        #     elif self._type == "enable_pv":
        #         result = self._coordinator.data[EcotouchTag.ENABLE_PV]["value"]
        #     elif self._type == "state_cooling":
        #         result = self._coordinator.data[EcotouchTag.STATE_COOLING]["value"]
        #     elif self._type == "state_sourcepump":
        #         result = self._coordinator.data[EcotouchTag.STATE_SOURCEPUMP]["value"]
        #     elif self._type == "state_water":
        #         result = self._coordinator.data[EcotouchTag.STATE_WATER]["value"]
        #     elif self._type == "status_cooling":
        #         result = self._coordinator.data[EcotouchTag.STATUS_COOLING]["value"]
        #     elif self._type == "status_heating":
        #         result = self._coordinator.data[EcotouchTag.STATUS_HEATING]["value"]
        #     elif self._type == "status_water":
        #         result = self._coordinator.data[EcotouchTag.STATUS_WATER]["value"]
        #     elif self._type == "temperature_outside":
        #         result = self._coordinator.data[EcotouchTag.TEMPERATURE_OUTSIDE]["value"]
        #     elif self._type == "temperature_outside_1h":
        #         result = self._coordinator.data[EcotouchTag.TEMPERATURE_OUTSIDE_1H]["value"]
        #     elif self._type == "temperature_outside_24h":
        #         result = self._coordinator.data[EcotouchTag.TEMPERATURE_OUTSIDE_24H]["value"]
        #     elif self._type == "temperature_source_in":
        #         result = self._coordinator.data[EcotouchTag.TEMPERATURE_SOURCE_IN]["value"]
        #     elif self._type == "temperature_source_out":
        #         result = self._coordinator.data[EcotouchTag.TEMPERATURE_SOURCE_OUT]["value"]
        #     elif self._type == "temperature_evaporation":
        #         result = self._coordinator.data[EcotouchTag.TEMPERATURE_EVAPORATION]["value"]
        #     elif self._type == "temperature_suction":
        #         result = self._coordinator.data[EcotouchTag.TEMPERATURE_SUCTION]["value"]
        #     elif self._type == "temperature_return_set":
        #         result = self._coordinator.data[EcotouchTag.TEMPERATURE_RETURN_SET]["value"]
        #     elif self._type == "temperature_return":
        #         result = self._coordinator.data[EcotouchTag.TEMPERATURE_RETURN]["value"]
        #     elif self._type == "temperature_flow":
        #         result = self._coordinator.data[EcotouchTag.TEMPERATURE_FLOW]["value"]
        #     elif self._type == "temperature_condensation":
        #         result = self._coordinator.data[EcotouchTag.TEMPERATURE_CONDENSATION]["value"]
        #     elif self._type == "temperature_storage":
        #         result = self._coordinator.data[EcotouchTag.TEMPERATURE_STORAGE]["value"]
        #     elif self._type == "temperature_room":
        #         result = self._coordinator.data[EcotouchTag.TEMPERATURE_ROOM]["value"]
        #     elif self._type == "temperature_room_1h":
        #         result = self._coordinator.data[EcotouchTag.TEMPERATURE_ROOM_1H]["value"]
        #     elif self._type == "temperature_water":
        #         result = self._coordinator.data[EcotouchTag.TEMPERATURE_WATER]["value"]
        #     elif self._type == "temperature_solar":
        #         result = self._coordinator.data[EcotouchTag.TEMPERATURE_SOLAR]["value"]
        #     elif self._type == "temperature2_outside_1h":
        #         result = self._coordinator.data[EcotouchTag.TEMPERATURE2_OUTSIDE_1H]["value"]
        #     elif self._type == "pressure_evaporation":
        #         result = self._coordinator.data[EcotouchTag.PRESSURE_EVAPORATION]["value"]
        #     elif self._type == "pressure_condensation":
        #         result = self._coordinator.data[EcotouchTag.PRESSURE_CONDENSATION]["value"]
        #     elif self._type == "position_expansion_valve":
        #         result = self._coordinator.data[EcotouchTag.POSITION_EXPANSION_VALVE]["value"]
        #     elif self._type == "power_compressor":
        #         result = self._coordinator.data[EcotouchTag.POWER_COMPRESSOR]["value"]
        #     elif self._type == "power_heating":
        #         result = self._coordinator.data[EcotouchTag.POWER_HEATING]["value"]
        #     elif self._type == "power_cooling":
        #         result = self._coordinator.data[EcotouchTag.POWER_COOLING]["value"]
        #     elif self._type == "cop_heating":
        #         result = self._coordinator.data[EcotouchTag.COP_HEATING]["value"]
        #     elif self._type == "cop_cooling":
        #         result = self._coordinator.data[EcotouchTag.COP_COOLING]["value"]
        #     elif self._type == "percent_heat_circ_pump":
        #         result = self._coordinator.data[EcotouchTag.PERCENT_HEAT_CIRC_PUMP]["value"]
        #     elif self._type == "percent_source_pump":
        #         result = self._coordinator.data[EcotouchTag.PERCENT_SOURCE_PUMP]["value"]
        #     elif self._type == "percent_compressor":
        #         result = self._coordinator.data[EcotouchTag.PERCENT_COMPRESSOR]["value"]

        #     else:
        #         result = "unavailable"

        #     if result is True:
        #         result = "on"
        #     elif result is False:
        #         result = "off"
        # except KeyError:
        #     return "unavailable"
        # return result

    @ property
    def icon(self):
        """Return the icon of the sensor."""
        return SENSOR_TYPES[self._type][4]
        # return ICON

    @ property
    def device_class(self):
        """Return the device class of the sensor."""
        return SENSOR_TYPES[self._type][2]

    @ property
    def entity_registry_enabled_default(self):
        """Return the entity_registry_enabled_default of the sensor."""
        return SENSOR_TYPES[self._type][5]

    @ property
    def entity_category(self):
        """Return the unit of measurement."""
        return SENSOR_TYPES[self._type][7]

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
