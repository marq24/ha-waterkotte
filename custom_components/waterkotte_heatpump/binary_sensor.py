"""Binary sensor platform for Waterkotte Heatpump."""
import logging
from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.helpers.typing import ConfigType, HomeAssistantType

from custom_components.waterkotte_heatpump.pywaterkotte_ha.ecotouch import EcotouchTag
from .entity import WaterkotteHeatpumpEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

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
        False,
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

    # status sensors (Operation Mode 0=off, 1=on or 2=disabled)
    "STATUS_HEATING": [
        "Status Heating",
        EcotouchTag.STATUS_HEATING,
        BinarySensorDeviceClass.RUNNING,
        None,
        "mdi:radiator",
        True,
        None,
        None,
        "I137"
    ],
    "STATUS_WATER": [
        "Status Water",
        EcotouchTag.STATUS_WATER,
        BinarySensorDeviceClass.RUNNING,
        None,
        "mdi:water-thermometer",
        True,
        None,
        None,
        "I138"
    ],
    "STATUS_COOLING": [
        "Status Cooling",
        EcotouchTag.STATUS_COOLING,
        BinarySensorDeviceClass.RUNNING,
        None,
        "mdi:snowflake-thermometer",
        True,
        None,
        None,
        "I139"
    ],
    "STATUS_POOL": [
        "Status Pool",
        EcotouchTag.STATUS_POOL,
        BinarySensorDeviceClass.RUNNING,
        None,
        "mdi:pool-thermometer",
        False,
        None,
        None,
        "I140"
    ],
    "STATUS_SOLAR": [
        "Status Solar",
        EcotouchTag.STATUS_SOLAR,
        BinarySensorDeviceClass.RUNNING,
        None,
        "mdi:solar-power-variant",
        False,
        None,
        None,
        "I141"
    ],
    # "STATUS_HEATING_CIRCULATION_PUMP": [
    #     "Status circulation pump heating",
    #     EcotouchTag.STATUS_HEATING_CIRCULATION_PUMP,
    #     BinarySensorDeviceClass.RUNNING,
    #     None,
    #     "mdi:pump",
    #     True,
    #     None,
    #     None,
    #     "I1270"
    # ],
    # "STATUS_SOLAR_CIRCULATION_PUMP": [
    #     "Status circulation pump Solar",
    #     EcotouchTag.STATUS_SOLAR_CIRCULATION_PUMP,
    #     BinarySensorDeviceClass.RUNNING,
    #     None,
    #     "mdi:pump",
    #     False,
    #     None,
    #     None,
    #     "I1287"
    # ],
    # "STATUS_BUFFER_TANK_CIRCULATION_PUMP": [
    #     "Status circulation pump buffer tank",
    #     EcotouchTag.STATUS_BUFFER_TANK_CIRCULATION_PUMP,
    #     BinarySensorDeviceClass.RUNNING,
    #     None,
    #     "mdi:pump",
    #     True,
    #     None,
    #     None,
    #     "I1291"
    # ],
    # "STATUS_COMPRESSOR": [
    #     "Status compressor",
    #     EcotouchTag.STATUS_COMPRESSOR,
    #     BinarySensorDeviceClass.RUNNING,
    #     None,
    #     "mdi:gauge",
    #     True,
    #     None,
    #     None,
    #     "I1307"
    # ],
    "STATE_BLOCKING_TIME": [
        "Blockingtime",
        EcotouchTag.STATE_BLOCKING_TIME,
        BinarySensorDeviceClass.RUNNING,
        None,
        "mdi:electric-switch",
        False,
        None,
        None,
        "heatsrcpump"
    ],
    "STATE_TEST_RUN": [
        "Testrun",
        EcotouchTag.STATE_TEST_RUN,
        BinarySensorDeviceClass.RUNNING,
        None,
        "mdi:heating-coil",
        True,
        None,
        None,
        "heatsrcpump"
    ],
    # this is just indicates if the heating circulation pump is running -
    # unfortunately this can't TAG is not writable (at least write does
    # not have any effect)
    "STATE_HEATING_CIRCULATION_PUMP_D425": [
        "Heating circulation pump",
        EcotouchTag.STATE_HEATING_CIRCULATION_PUMP_D425,
        None,
        None,
        None,
        True,
        None,
        None,
    ],
    "STATE_BUFFERTANK_CIRCULATION_PUMP_D377": [
        "Buffertank circulation pump",
        EcotouchTag.STATE_BUFFERTANK_CIRCULATION_PUMP_D377,
        None,
        None,
        None,
        True,
        None,
        None,
    ],
    "STATE_POOL_CIRCULATION_PUMP_D549": [
        "Pool circulation pump",
        EcotouchTag.STATE_POOL_CIRCULATION_PUMP_D549,
        None,
        None,
        None,
        False,
        None,
        None,
    ],
    "STATE_MIX1_CIRCULATION_PUMP_D248": [
        "Mix1 circulation pump",
        EcotouchTag.STATE_MIX1_CIRCULATION_PUMP_D248,
        None,
        None,
        None,
        True,
        None,
        None,
    ],
    "STATE_MIX2_CIRCULATION_PUMP_D291": [
        "Mix2 circulation pump",
        EcotouchTag.STATE_MIX2_CIRCULATION_PUMP_D291,
        None,
        None,
        None,
        False,
        None,
        None,
    ],
    "STATE_MIX3_CIRCULATION_PUMP_D334": [
        "Mix3 circulation pump",
        EcotouchTag.STATE_MIX3_CIRCULATION_PUMP_D334,
        None,
        None,
        None,
        False,
        None,
        None,
    ],
    # "MIX1_CIRCULATION_PUMP_D563": [
    #    "Mix1 circulation pump",
    #    EcotouchTag.MIX1_CIRCULATION_PUMP_D563,
    #    None,
    #    None,
    #    None,
    #    True,
    #    None,
    #    None,
    # ]
}


# async def async_setup_entry(hass, entry, async_add_devices):
#     """Setup binary_sensor platform."""
#     coordinator = hass.data[DOMAIN][entry.entry_id]
#     async_add_devices([WaterkotteHeatpumpBinarySensor(coordinator, entry)])


async def async_setup_entry(hass: HomeAssistantType, entry: ConfigType, async_add_devices) -> None:
    """Set up the Waterkotte binary_sensor platform."""
    _LOGGER.debug("Binary_Sensor async_setup_entry")
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices([WaterkotteHeatpumpBinarySensor(entry, coordinator, sensor_type)
                       for sensor_type in SENSOR_TYPES])


class WaterkotteHeatpumpBinarySensor(WaterkotteHeatpumpEntity, BinarySensorEntity):
    """waterkotte_heatpump binary_sensor class."""

    # _attr_has_entity_name = True

    def __init__(self, entry, hass_data, sensor_type):  # pylint: disable=unused-argument
        """Initialize the sensor."""
        self.entity_id = f"{DOMAIN}.wkh_{sensor_type}"
        self._coordinator = hass_data
        self._type = sensor_type
        self._attr_unique_id = sensor_type
        self._entry_data = entry.data
        self._device_id = entry.entry_id
        self._attr_translation_key = self._type.lower()
        super().__init__(hass_data, entry)

    @property
    def eco_tag(self):
        """Return a tag to use for this entity."""
        return SENSOR_TYPES[self._type][1]

    @property
    def is_on(self) -> bool | None:
        try:
            value = None
            if self.eco_tag in self._coordinator.data:
                value_and_state = self._coordinator.data[self.eco_tag]
                if "value" in value_and_state:
                    value = value_and_state["value"]
                else:
                    _LOGGER.debug(f"is_on: for {self._type} could not read value from data: {value_and_state}")
            else:
                if len(self._coordinator.data) > 0:
                    _LOGGER.debug(
                        f"is_on: for {self._type} could not be found in available data: {self._coordinator.data}")
            if value is None or value == "":
                value = None

            # if value is not None and str(self._type).startswith("STATUS"):
            #    _LOGGER.debug(f"{self._type} -> {value}")

        except KeyError:
            _LOGGER.warning(f"is_on caused KeyError for: {self._type}")
            value = None
        except TypeError:
            return None

        if not isinstance(value, bool):
            if isinstance(value, str):
                # parse anything else then 'on' to False!
                if value.lower() == 'on':
                    value = True
                else:
                    value = False
            else:
                value = False

        return value

    @property
    def icon(self):
        if SENSOR_TYPES[self._type][4] is None:
            if self.is_on:
                match self._type:
                    case "STATE_HEATING_CIRCULATION_PUMP_D425" | \
                         "STATE_BUFFERTANK_CIRCULATION_PUMP_D377" | \
                         "STATE_POOL_CIRCULATION_PUMP_D549" | \
                         "STATE_MIX1_CIRCULATION_PUMP_D248" | \
                         "STATE_MIX2_CIRCULATION_PUMP_D291" | \
                         "STATE_MIX3_CIRCULATION_PUMP_D334" | \
                         "STATUS_HEATING_CIRCULATION_PUMP" | \
                         "STATUS_SOLAR_CIRCULATION_PUMP" | \
                         "STATUS_BUFFER_TANK_CIRCULATION_PUMP":
                        return "mdi:pump"
                    case _:
                        return None
            else:
                match self._type:
                    case "STATE_HEATING_CIRCULATION_PUMP_D425" | \
                         "STATE_BUFFERTANK_CIRCULATION_PUMP_D377" | \
                         "STATE_POOL_CIRCULATION_PUMP_D549" | \
                         "STATE_MIX1_CIRCULATION_PUMP_D248" | \
                         "STATE_MIX2_CIRCULATION_PUMP_D291" | \
                         "STATE_MIX3_CIRCULATION_PUMP_D334" | \
                         "STATUS_HEATING_CIRCULATION_PUMP" | \
                         "STATUS_SOLAR_CIRCULATION_PUMP" | \
                         "STATUS_BUFFER_TANK_CIRCULATION_PUMP":
                        return "mdi:pump-off"
                    case _:
                        return None
        else:
            return SENSOR_TYPES[self._type][4]

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return SENSOR_TYPES[self._type][2]

    @property
    def entity_registry_enabled_default(self):
        """Return the entity_registry_enabled_default of the sensor."""
        return SENSOR_TYPES[self._type][5]

    @property
    def entity_category(self):
        """Return the unit of measurement."""
        try:
            return SENSOR_TYPES[self._type][7]
        except IndexError:
            return None

    @property
    def unique_id(self):
        """Return the unique of the sensor."""
        return self._attr_unique_id
