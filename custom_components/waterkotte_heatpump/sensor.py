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
    DEGREE,
    #    DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_PRESSURE,
    DEVICE_CLASS_TEMPERATURE,
    #    LENGTH_KILOMETERS,
    PRESSURE_HPA,
    PRESSURE_BAR,
    SPEED_KILOMETERS_PER_HOUR,
    TEMP_CELSIUS,
    #    TIME_SECONDS,
)
from .entity import WaterkotteHeatpumpEntity
from .pywaterkotte.ecotouch import EcotouchTag
from .const import ENUM_ONOFFAUTO, DEVICE_CLASS_ENUM, DOMAIN  # , NAME, CONF_FW, CONF_BIOS, CONF_IP

_LOGGER = logging.getLogger(__name__)


# Sensor types are defined as:
#   variable -> [0]title, [1]device_class, [2]units, [3]icon, [4]disabled_by_default, [5]options, [6]entity_category
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
        "State Sourcepump",
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
    "temperature_heating_return": [
        "Temperature Heating Return",
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        False,
    ],
    "temperature_cooling_return": [
        "Temperature Cooling Return",
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        False,
    ],
    "temperature2_outside_1h": [  # TEMPERATURE2_OUTSIDE_1H = TagData(["A90"], "°C")
        "Temperature2 Outside 1h",
        DEVICE_CLASS_TEMPERATURE,
        TEMP_CELSIUS,
        "mdi:thermometer",
        False,
    ],
    "pressure_evaporation": [
        "Pressure Evaporation",
        DEVICE_CLASS_PRESSURE,
        PRESSURE_BAR,
        "mdi:gauge",
        False,
    ],
    "pressure_condensation": [
        "Pressure Condensation",
        DEVICE_CLASS_PRESSURE,
        PRESSURE_BAR,
        "mdi:gauge",
        False,
    ],
    "position_expansion_valve": [
        "Position Expansion Valve",
        DEVICE_CLASS_PRESSURE,
        PRESSURE_BAR,
        "mdi:gauge",
        False,
    ],
    "power_compressor": [
        "Power Compressor",
        DEVICE_CLASS_PRESSURE,
        PRESSURE_BAR,
        "mdi:gauge",
        False,
    ],
    "power_heating": [
        "Power Heating",
        DEVICE_CLASS_PRESSURE,
        PRESSURE_BAR,
        "mdi:gauge",
        False,
    ],
    "power_cooling": [
        "Power Cooling",
        DEVICE_CLASS_PRESSURE,
        PRESSURE_BAR,
        "mdi:gauge",
        False,
    ],
    "cop_heating": [
        "COP Heating",
        DEVICE_CLASS_PRESSURE,
        PRESSURE_BAR,
        "mdi:gauge",
        False,
    ],
    "cop_cooling": [
        "COP Cooling",
        DEVICE_CLASS_PRESSURE,
        PRESSURE_BAR,
        "mdi:gauge",
        False,
    ],
    "percent_heat_circ_pump": [
        "Percent Heat Circ Pump",
        DEVICE_CLASS_PRESSURE,
        PRESSURE_BAR,
        "mdi:gauge",
        False,
    ],
    "percent_source_pump": [
        "Percent Source Pump",
        DEVICE_CLASS_PRESSURE,
        PRESSURE_BAR,
        "mdi:gauge",
        False,
    ],
    "percent_compressor": [
        "Percent Compressor",
        DEVICE_CLASS_PRESSURE,
        PRESSURE_BAR,
        "mdi:gauge",
        False,
    ],
    # "version_controller": [
    #     "Version Controller",
    #     DEVICE_CLASS_PRESSURE,
    #     PRESSURE_BAR,
    #     "mdi:gauge",
    #     False,
    #     None,
    #     EntityCategory.DIAGNOSTIC,
    # ],
    # "version_controller_build": [
    #     "Version Controller Build",
    #     DEVICE_CLASS_PRESSURE,
    #     PRESSURE_BAR,
    #     "mdi:gauge",
    #     False,
    #     None,
    #     EntityCategory.DIAGNOSTIC,
    # ],
    # "version_bios": [
    #     "Version BIOS",
    #     DEVICE_CLASS_PRESSURE,
    #     PRESSURE_BAR,
    #     "mdi:gauge",
    #     False,
    #     None,
    #     EntityCategory.DIAGNOSTIC,
    # ],

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
    ENABLE_HEATING = TagData(["I30"], read_function=_parse_state)
    ENABLE_COOLING = TagData(["I31"], read_function=_parse_state)
    ENABLE_WARMWATER = TagData(["I32"], read_function=_parse_state)
    ENABLE_POOL = TagData(["I33"], read_function=_parse_state)
    ENABLE_PV = TagData(["I41"], read_function=_parse_state)
    STATE_SOURCEPUMP = TagData(["I51"], bit=0)
    STATE_HEATINGPUMP = TagData(["I51"], bit=1)
    STATE_EVD = TagData(["I51"], bit=2)
    STATE_COMPRESSOR = TagData(["I51"], bit=3)
    STATE_COMPRESSOR2 = TagData(["I51"], bit=4)
    STATE_EXTERNAL_HEATER = TagData(["I51"], bit=5)
    STATE_ALARM = TagData(["I51"], bit=6)
    STATE_COOLING = TagData(["I51"], bit=7)
    STATE_WATER = TagData(["I51"], bit=8)
    STATE_POOL = TagData(["I51"], bit=9)
    STATE_SOLAR = TagData(["I51"], bit=10)
    STATE_COOLING4WAY = TagData(["I51"], bit=11)
    ALARM = TagData(["I52"])
    INTERRUPTIONS = TagData(["I53"])
    STATE_SERVICE = TagData(["I135"])
    STATUS_HEATING = TagData(["I37"])
    STATUS_COOLING = TagData(["I38"])
    STATUS_WATER = TagData(["I39"])
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


# async def async_setup_entry(hass, entry, async_add_devices):
#    """Setup sensor platform."""
#    coordinator = hass.data[DOMAIN][entry.entry_id]
#    async_add_devices([WaterkotteHeatpumpSensor(coordinator, entry)])

# async def async_setup_entry(hass: HomeAssistantType, entry: ConfigType, async_add_entities) -> None:
async def async_setup_entry(hass: HomeAssistantType, entry: ConfigType, async_add_devices) -> None:
    """Set up the Waterkotte sensor platform."""
    # hass_data = hass.data[DOMAIN][entry.entry_id]
    _LOGGER.debug("Sensor async_setup_entry")
    coordinator = hass.data[DOMAIN][entry.entry_id]
    # async_add_devices([WaterkotteHeatpumpSensor(entry, coordinator, "temperature_condensation")])
    # async_add_devices([WaterkotteHeatpumpSensor(entry, coordinator, "temperature_evaporation")])
    async_add_devices([WaterkotteHeatpumpSensor(entry, coordinator, sensor_type)
                       for sensor_type in SENSOR_TYPES])

    # print(entry)
    # async_add_entities(
    #     [
    #         WaterkotteHeatpumpSensor(entry, hass_data, sensor_type)
    #         for sensor_type in SENSOR_TYPES
    #     ],
    # False,
    # )


# class WaterkotteHeatpumpSensor(WaterkotteHeatpumpEntity):
# class WaterkotteHeatpumpSensor(Entity):
class WaterkotteHeatpumpSensor(SensorEntity, WaterkotteHeatpumpEntity):
    """waterkotte_heatpump Sensor class."""

    def __init__(self, entry, hass_data, sensor_type):  # pylint: disable=unused-argument
        """Initialize the sensor."""
        # super().__init__(self, hass_data)
        self._coordinator = hass_data

        self._type = sensor_type
        self._name = f"{SENSOR_TYPES[self._type][0]} {DOMAIN}"
        self._unique_id = f"{SENSOR_TYPES[self._type][0]}_{DOMAIN}"
        self._entry_data = entry.data
        # self._config = list(self.hass.data['waterkotte_heatpump'].values())[0].config_entry.data
        # self._fw = self._config["fw"]
        # self._bios = self._config["bios"]
        # self._ip = self._config["ip"]
        self._device_id = entry.entry_id
        # self._name = f"{DOMAIN}_{SENSOR_TYPES[self._type][0]}"
        # self._unique_id = f"{DOMAIN}_{SENSOR_TYPES[self._type][0]}"
        super().__init__(hass_data, entry)
        # super(coordi, self).__init__(self, hass_data)
        # super(entry,self).__init__(self, hass_data)

    @ property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @ property
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
                result = self._coordinator.data[EcotouchTag.TEMPERATURE_OUTSIDE_24H]["value"]
            elif self._type == "temperature_source_in":
                result = self._coordinator.data[EcotouchTag.TEMPERATURE_SOURCE_IN]["value"]
            elif self._type == "temperature_source_out":
                result = self._coordinator.data[EcotouchTag.TEMPERATURE_SOURCE_OUT]["value"]
            elif self._type == "temperature_evaporation":
                result = self._coordinator.data[EcotouchTag.TEMPERATURE_EVAPORATION]["value"]
            elif self._type == "temperature_suction":
                result = self._coordinator.data[EcotouchTag.TEMPERATURE_SUCTION]["value"]
            elif self._type == "temperature_return_set":
                result = self._coordinator.data[EcotouchTag.TEMPERATURE_RETURN_SET]["value"]
            elif self._type == "temperature_return":
                result = self._coordinator.data[EcotouchTag.TEMPERATURE_RETURN]["value"]
            elif self._type == "temperature_flow":
                result = self._coordinator.data[EcotouchTag.TEMPERATURE_FLOW]["value"]
            elif self._type == "temperature_condensation":
                result = self._coordinator.data[EcotouchTag.TEMPERATURE_CONDENSATION]["value"]
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
            elif self._type == "temperature2_outside_1h":
                result = self._coordinator.data[EcotouchTag.TEMPERATURE2_OUTSIDE_1H]["value"]
            elif self._type == "pressure_evaporation":
                result = self._coordinator.data[EcotouchTag.PRESSURE_EVAPORATION]["value"]
            elif self._type == "pressure_condensation":
                result = self._coordinator.data[EcotouchTag.PRESSURE_CONDENSATION]["value"]
            elif self._type == "position_expansion_valve":
                result = self._coordinator.data[EcotouchTag.POSITION_EXPANSION_VALVE]["value"]
            elif self._type == "power_compressor":
                result = self._coordinator.data[EcotouchTag.POWER_COMPRESSOR]["value"]
            elif self._type == "power_heating":
                result = self._coordinator.data[EcotouchTag.POWER_HEATING]["value"]
            elif self._type == "power_cooling":
                result = self._coordinator.data[EcotouchTag.POWER_COOLING]["value"]
            elif self._type == "cop_heating":
                result = self._coordinator.data[EcotouchTag.COP_HEATING]["value"]
            elif self._type == "cop_cooling":
                result = self._coordinator.data[EcotouchTag.COP_COOLING]["value"]
            elif self._type == "percent_heat_circ_pump":
                result = self._coordinator.data[EcotouchTag.PERCENT_HEAT_CIRC_PUMP]["value"]
            elif self._type == "percent_source_pump":
                result = self._coordinator.data[EcotouchTag.PERCENT_SOURCE_PUMP]["value"]
            elif self._type == "percent_compressor":
                result = self._coordinator.data[EcotouchTag.PERCENT_COMPRESSOR]["value"]
            # elif self._type == "version_controller":
            #     result = self._coordinator.data[EcotouchTag.VERSION_CONTROLLER]["value"]
            # elif self._type == "version_controller_build":
            #     result = self._coordinator.data[EcotouchTag.VERSION_CONTROLLER_BUILD]["value"]
            # elif self._type == "version_bios":
            #     result = self._coordinator.data[EcotouchTag.VERSION_BIOS]["value"]

            else:
                result = "unavailable"
            if result is True:
                result = "on"
            elif result is False:
                result = "off"
        except KeyError:
            return "unavailable"
        return result

    @ property
    def icon(self):
        """Return the icon of the sensor."""
        return SENSOR_TYPES[self._type][3]
        # return ICON

    @ property
    def device_class(self):
        """Return the device class of the sensor."""
        return SENSOR_TYPES[self._type][1]

    @ property
    def entity_registry_enabled_default(self):
        """Return the entity_registry_enabled_default of the sensor."""
        return SENSOR_TYPES[self._type][4]

    @ property
    def entity_category(self):
        """Return the unit of measurement."""
        try:
            return SENSOR_TYPES[self._type][6]
        except IndexError:
            return None

    @ property
    def unique_id(self):
        """Return the unique of the sensor."""
        return self._unique_id

    @ property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return SENSOR_TYPES[self._type][2]

    async def async_update(self):
        """Schedule a custom update via the common entity update service."""
        await self._coordinator.async_request_refresh()

    @ property
    def should_poll(self) -> bool:
        """Entities do not individually poll."""
        return False

    # @property
    # def device_info(self) -> DeviceInfo:
    #     """Return the device info."""
    #     # ip = "123"
    #     return DeviceInfo(
    #         id=DOMAIN,
    #         identifiers={
    #             # Serial numbers are unique identifiers within a specific domain
    #             #                (DOMAIN
    #             # , self.unique_id
    #             #                )
    #             (DOMAIN, self._device_id),
    #             ("IP", self._entry_data['ip']),
    #             ('device', self._device_id)
    #         },
    #         name=NAME,
    #         manufacturer=NAME,
    #         model="modelstr",
    #         sw_version=f"{self._entry_data['fw']} BIOS:{self._entry_data['bios']}",
    #         # via_device=(hue.DOMAIN, self.api.bridgeid),
    #     )
