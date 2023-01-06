"""Sensor platform for Waterkotte Heatpump."""
import logging
# from homeassistant.helpers.entity import Entity, EntityCategory  # , DeviceInfo
from homeassistant.components.select import SelectEntity
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
#   variable -> [0]title, [1] EcoTouchTag, [2]device_class, [3]units, [4]icon, [5]disabled_by_default, [6]options, [7]entity_category
SENSOR_TYPES = {
    "enable_cooling": [
        "enable_cooling",
        EcotouchTag.ENABLE_COOLING,
        DEVICE_CLASS_ENUM,
        None,
        "mdi:snowflake-thermometer",
        True,
        ENUM_ONOFFAUTO,
    ],

    "enable_heating": [
        "enable_cooling",
        EcotouchTag.ENABLE_COOLING,
        DEVICE_CLASS_ENUM,
        None,
        "mdi:snowflake-thermometer",
        True,
        ENUM_ONOFFAUTO,
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


async def async_setup_entry(hass: HomeAssistantType, entry: ConfigType, async_add_devices) -> None:
    """Set up the Waterkotte sensor platform."""
    # hass_data = hass.data[DOMAIN][entry.entry_id]
    _LOGGER.debug("Sensor async_setup_entry")
    coordinator = hass.data[DOMAIN][entry.entry_id]
    # async_add_devices([WaterkotteHeatpumpSensor(entry, coordinator, "temperature_condensation")])
    # async_add_devices([WaterkotteHeatpumpSensor(entry, coordinator, "temperature_evaporation")])
    async_add_devices([WaterkotteHeatpumpSelect(entry, coordinator, sensor_type)
                       for sensor_type in SENSOR_TYPES])


class WaterkotteHeatpumpSelect(SelectEntity, WaterkotteHeatpumpEntity):
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

    @property
    def current_option(self) -> str | None:
        sensor = SENSOR_TYPES[self._type]
        value = self._coordinator.data[sensor[1]]["value"]
        if value is None or value == "":
            value = 'unknown'
        return value
        # return "auto"

    @property
    def options(self) -> list[str]:
        return ["off", "auto", "manual"]

    async def async_select_option(self, option: str) -> None:  # pylint: disable=unused-argument
        """Turn on the switch."""
        print(option)
        # await self._coordinator.api.async_write_value(SENSOR_TYPES[self._type][1], option)
        await self._coordinator.async_write_tag(SENSOR_TYPES[self._type][1], option)

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
        try:
            return SENSOR_TYPES[self._type][7]
        except IndexError:
            return None

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
