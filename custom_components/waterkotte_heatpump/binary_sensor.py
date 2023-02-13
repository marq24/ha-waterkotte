"""Binary sensor platform for Waterkotte Heatpump."""
import logging
from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.helpers.typing import ConfigType, HomeAssistantType
# from homeassistant.const import ATTR_FRIENDLY_NAME

# from .const import DOMAIN
from .xecotouch import Ecotouch2Tag
from .entity import WaterkotteHeatpumpEntity

# from .xecotouch import EcotouchTag
from .const import DOMAIN  # , NAME, CONF_FW, CONF_BIOS, CONF_IP

_LOGGER = logging.getLogger(__name__)

# Sensor types are defined as:
#   variable -> [0]title, [1] EcoTouchTag, [2]device_class, [3]units, [4]icon, [5]enabled_by_default, [6]options, [7]entity_category #pylint: disable=line-too-long
SENSOR_TYPES = {
    "STATE_SOURCEPUMP": [
        "Sourcepump",
        Ecotouch2Tag.STATE_SOURCEPUMP,
        BinarySensorDeviceClass.RUNNING,
        None,
        "mdi:snowflake-thermometer",
        True,
        None,
        None,
    ],
    "STATE_HEATINGPUMP": [
        "Heatingpump",
        Ecotouch2Tag.STATE_HEATINGPUMP,
        BinarySensorDeviceClass.RUNNING,
        None,
        "mdi:weather-partly-cloudy",
        True,
        None,
        None,
    ],
    "STATE_EVD": [
        "EVD",
        Ecotouch2Tag.STATE_EVD,
        BinarySensorDeviceClass.RUNNING,
        None,
        "mdi:weather-partly-cloudy",
        False,
        None,
        None,
    ],
    "STATE_COMPRESSOR": [
        "Compressor",
        Ecotouch2Tag.STATE_COMPRESSOR,
        BinarySensorDeviceClass.RUNNING,
        None,
        "mdi:weather-partly-cloudy",
        False,
        None,
        None,
    ],
    "STATE_COMPRESSOR2": [
        "Compressor2",
        Ecotouch2Tag.STATE_COMPRESSOR2,
        BinarySensorDeviceClass.RUNNING,
        None,
        "mdi:weather-partly-cloudy",
        False,
        None,
        None,
    ],
    "STATE_EXTERNAL_HEATER": [
        "External Heater",
        Ecotouch2Tag.STATE_EXTERNAL_HEATER,
        BinarySensorDeviceClass.RUNNING,
        None,
        "mdi:weather-partly-cloudy",
        False,
        None,
        None,
    ],
    "STATE_ALARM": [
        "Alarm",
        Ecotouch2Tag.STATE_ALARM,
        BinarySensorDeviceClass.RUNNING,
        None,
        "mdi:weather-partly-cloudy",
        False,
        None,
        None,
    ],
    "STATE_COOLING": [
        "Cooling",
        Ecotouch2Tag.STATE_COOLING,
        BinarySensorDeviceClass.RUNNING,
        None,
        "mdi:weather-partly-cloudy",
        False,
        None,
        None,
    ],
    "STATE_WATER": [
        "Water",
        Ecotouch2Tag.STATE_WATER,
        BinarySensorDeviceClass.RUNNING,
        None,
        "mdi:weather-partly-cloudy",
        False,
        None,
        None,
    ],
    "STATE_POOL": [
        "Pool",
        Ecotouch2Tag.STATE_POOL,
        BinarySensorDeviceClass.RUNNING,
        None,
        "mdi:weather-partly-cloudy",
        True,
        None,
        None,
    ],
    "STATE_SOLAR": [
        "Solar",
        Ecotouch2Tag.STATE_SOLAR,
        BinarySensorDeviceClass.RUNNING,
        None,
        "mdi:weather-partly-cloudy",
        False,
        None,
        None,
    ],
    "STATE_COOLING4WAY": [
        "Cooling4way",
        Ecotouch2Tag.STATE_COOLING4WAY,
        BinarySensorDeviceClass.RUNNING,
        None,
        "mdi:weather-partly-cloudy",
        False,
        None,
        None,
    ],
    # "holiday_enabled": [
    #     "Holiday Mode",
    #     EcotouchTag.HOLIDAY_ENABLED,
    #     BinarySensorDeviceClass.RUNNING,
    #     None,
    #     None,
    #     True,
    #     None,
    #     None,
    # ],


}
"""


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
#     """Setup binary_sensor platform."""
#     coordinator = hass.data[DOMAIN][entry.entry_id]
#     async_add_devices([WaterkotteHeatpumpBinarySensor(coordinator, entry)])


async def async_setup_entry(hass: HomeAssistantType, entry: ConfigType, async_add_devices) -> None:
    """Set up the Waterkotte sensor platform."""
    # hass_data = hass.data[DOMAIN][entry.entry_id]
    _LOGGER.debug("Sensor async_setup_entry")
    coordinator = hass.data[DOMAIN][entry.entry_id]
    # async_add_devices([WaterkotteHeatpumpSensor(entry, coordinator, "temperature_condensation")])
    # async_add_devices([WaterkotteHeatpumpSensor(entry, coordinator, "temperature_evaporation")])
    async_add_devices([WaterkotteHeatpumpBinarySensor(entry, coordinator, sensor_type)
                       for sensor_type in SENSOR_TYPES])


class WaterkotteHeatpumpBinarySensor(WaterkotteHeatpumpEntity, BinarySensorEntity):
    """waterkotte_heatpump binary_sensor class."""
    # _attr_has_entity_name = True

    def __init__(self, entry, hass_data, sensor_type):  # pylint: disable=unused-argument
        """Initialize the sensor."""
        self._coordinator = hass_data

        self._type = sensor_type
        # self._name = f"{SENSOR_TYPES[self._type][0]} {DOMAIN}"
        self._name = f"{SENSOR_TYPES[self._type][0]}"
        # self._unique_id = f"{SENSOR_TYPES[self._type][0]}_{DOMAIN}"
        # self._unique_id = f"{self._type}_{DOMAIN}"
        self._unique_id = self._type
        self._entry_data = entry.data
        self._device_id = entry.entry_id
        hass_data.alltags.update({self._unique_id: SENSOR_TYPES[self._type][1]})
        super().__init__(hass_data, entry)
        # self._attr_capability_attributes[ATTR_FRIENDLY_NAME] = self._name

    @property
    def tag(self):
        """Return a tag to use for this entity."""
        return SENSOR_TYPES[self._type][1]

    @ property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary_sensor is on."""
        # return self.coordinator.data.get("title", "") == "foo"
        try:
            sensor = SENSOR_TYPES[self._type]
            value = self._coordinator.data[sensor[1]]["value"]
            if value is None or value == "":
                value = None
        except KeyError:
            value = None
            print(value)
        except TypeError:
            return None
        return value

    @ property
    def icon(self):
        """Return the icon of the sensor."""
        if SENSOR_TYPES[self._type][4] is None:
            sensor = SENSOR_TYPES[self._type]
            try:
                if self._type == "holiday_enabled" and 'value' in self._coordinator.data[sensor[1]]:
                    if self._coordinator.data[sensor[1]]["value"] is True:
                        return "mdi:calendar-check"
                    else:
                        return "mdi:calendar-blank"
                else:
                    return None
            except KeyError:
                print(f"KeyError in Binary_sensor.icon: should have value? data:{self._coordinator.data[sensor[1]]}")  # pylint: disable=line-too-long
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
