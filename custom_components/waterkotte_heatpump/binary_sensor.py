"""Binary sensor platform for Waterkotte Heatpump."""
import logging
from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.helpers.typing import ConfigType, HomeAssistantType
# from homeassistant.const import ATTR_FRIENDLY_NAME

# from .const import DOMAIN
from custom_components.waterkotte_heatpump.pywaterkotte_ha.ecotouch import EcotouchTag
from .entity import WaterkotteHeatpumpEntity

# from .ecotouch import EcotouchTag
from .const import DOMAIN  # , NAME, CONF_FW, CONF_BIOS, CONF_IP

_LOGGER = logging.getLogger(__name__)
_LANG = None

# Sensor types are defined as:
#   variable -> [0]title, [1] EcoTouchTag, [2]device_class, [3]units, [4]icon, [5]enabled_by_default, [6]options, [7]entity_category #pylint: disable=line-too-long
SENSOR_TYPES = {
    "STATE_SOURCEPUMP": [
        "Sourcepump",
        EcotouchTag.STATE_SOURCEPUMP,
        BinarySensorDeviceClass.RUNNING,
        None,
        "mdi:water-pump",
        True,
        None,
        None,
        "heatsrcpump"
    ],
    "STATE_HEATINGPUMP": [
        "Heatingpump",
        EcotouchTag.STATE_HEATINGPUMP,
        BinarySensorDeviceClass.RUNNING,
        None,
        "mdi:heat-pump",
        True,
        None,
        None,
        "heatpump"
    ],
    # EVD: -> Überhitzungsregler
    "STATE_EVD": [
        "EVD",
        EcotouchTag.STATE_EVD,
        BinarySensorDeviceClass.RUNNING,
        None,
        "mdi:thermometer-high",
        True,
        None,
        None,
        "evd"
    ],
    "STATE_COMPRESSOR": [
        "Compressor",
        EcotouchTag.STATE_COMPRESSOR,
        BinarySensorDeviceClass.RUNNING,
        None,
        "mdi:gauge",
        True,
        None,
        None,
        "comp"
    ],
    "STATE_COMPRESSOR2": [
        "Compressor2",
        EcotouchTag.STATE_COMPRESSOR2,
        BinarySensorDeviceClass.RUNNING,
        None,
        "mdi:gauge",
        False,
        None,
        None,
        "comp"
    ],
    "STATE_EXTERNAL_HEATER": [
        "External Heater",
        EcotouchTag.STATE_EXTERNAL_HEATER,
        BinarySensorDeviceClass.RUNNING,
        None,
        "mdi:heating-coil",
        True,
        None,
        None,
        "heater"
    ],
    "STATE_ALARM": [
        "Alarm",
        EcotouchTag.STATE_ALARM,
        BinarySensorDeviceClass.RUNNING,
        None,
        "mdi:alert",
        False,
        None,
        None,
        "alarm"
    ],
    "STATE_COOLING": [
        "Cooling",
        EcotouchTag.STATE_COOLING,
        BinarySensorDeviceClass.RUNNING,
        None,
        "mdi:snowflake-thermometer",
        False,
        None,
        None,
        "cool"
    ],
    "STATE_WATER": [
        "Water",
        EcotouchTag.STATE_WATER,
        BinarySensorDeviceClass.RUNNING,
        None,
        "mdi:water-thermometer",
        True,
        None,
        None,
        "dhw"
    ],
    "STATE_POOL": [
        "Pool",
        EcotouchTag.STATE_POOL,
        BinarySensorDeviceClass.RUNNING,
        None,
        "mdi:pool",
        True,
        None,
        None,
        "pool"
    ],
    "STATE_SOLAR": [
        "Solar",
        EcotouchTag.STATE_SOLAR,
        BinarySensorDeviceClass.RUNNING,
        None,
        "mdi:solar-power-variant",
        False,
        None,
        None,
        "solar"
    ],
    "STATE_COOLING4WAY": [
        "Cooling4way",
        EcotouchTag.STATE_COOLING4WAY,
        BinarySensorDeviceClass.RUNNING,
        None,
        "mdi:snowflake-thermometer",
        False,
        None,
        None,
        "4wayvalve"
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

# async def async_setup_entry(hass, entry, async_add_devices):
#     """Setup binary_sensor platform."""
#     coordinator = hass.data[DOMAIN][entry.entry_id]
#     async_add_devices([WaterkotteHeatpumpBinarySensor(coordinator, entry)])


async def async_setup_entry(hass: HomeAssistantType, entry: ConfigType, async_add_devices) -> None:
    """Set up the Waterkotte binary_sensor platform."""
    _LOGGER.debug("Binary_Sensor async_setup_entry")
    coordinator = hass.data[DOMAIN][entry.entry_id]
    global _LANG
    _LANG = coordinator.lang
    async_add_devices([WaterkotteHeatpumpBinarySensor(entry, coordinator, sensor_type)
                       for sensor_type in SENSOR_TYPES])


class WaterkotteHeatpumpBinarySensor(WaterkotteHeatpumpEntity, BinarySensorEntity):
    """waterkotte_heatpump binary_sensor class."""
    # _attr_has_entity_name = True

    def __init__(self, entry, hass_data, sensor_type):  # pylint: disable=unused-argument
        """Initialize the sensor."""
        self._coordinator = hass_data
        self._type = sensor_type
        self._unique_id = SENSOR_TYPES[self._type][1].name
        self._entry_data = entry.data
        self._device_id = entry.entry_id
        if SENSOR_TYPES[self._type][8] in _LANG:
            self._name = _LANG[SENSOR_TYPES[self._type][8]]
        else:
            _LOGGER.warning(str(SENSOR_TYPES[self._type][8])+" Binary-Sensor not found in translation")
            self._name = f"{SENSOR_TYPES[self._type][0]}"
        hass_data.alltags.update({self._unique_id: SENSOR_TYPES[self._type][1]})
        super().__init__(hass_data, entry)

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
