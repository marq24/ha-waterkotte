"""Sensor platform for Waterkotte Heatpump."""
import logging

# from homeassistant.helpers.entity import Entity, EntityCategory  # , DeviceInfo
from homeassistant.components.number import NumberEntity, NumberDeviceClass, DEFAULT_STEP
from homeassistant.helpers.typing import ConfigType, HomeAssistantType

# from .const import DEFAULT_NAME


# from .const import ICON
# from .const import SENSOR
#  from .const import UnitOfTemperature

from custom_components.waterkotte_heatpump.mypywaterkotte.ecotouch import EcotouchTag
from .entity import WaterkotteHeatpumpEntity

from .const import ENUM_OFFAUTOMANUAL, DEVICE_CLASS_ENUM, DOMAIN

_LOGGER = logging.getLogger(__name__)

# Sensor types are defined as:
#   variable -> [0]title, [1] EcotouchTag, [2]device_class, [3]min, [4]icon, [5]enabled_by_default, [6]max, [7]step #pylint: disable=line-too-long
SENSOR_TYPES = {
    # temperature sensors

    # not sure if this RETURN temperature should be set able at all?!
    "TEMPERATURE_RETURN_SET": [
        "Temperature Return Setpoint",
        EcotouchTag.TEMPERATURE_RETURN_SET,
        NumberDeviceClass.TEMPERATURE,
        "mdi:thermometer",
        False,
        0,
        100,
        DEFAULT_STEP,
    ],
    # Cooling/Kuehlung...
    # A109
    "TEMPERATURE_COOLING_SETPOINT": [
        "Temperature Cooling Demand",
        EcotouchTag.TEMPERATURE_COOLING_SETPOINT,
        NumberDeviceClass.TEMPERATURE,
        "mdi:thermometer",
        False,
        0,
        100,
        DEFAULT_STEP,
    ],
    # A108
    "TEMPERATURE_COOLING_OUTDOOR_LIMIT": [
        "Temperature Cooling Outdoor Limit",
        EcotouchTag.TEMPERATURE_COOLING_OUTDOOR_LIMIT,
        NumberDeviceClass.TEMPERATURE,
        "mdi:thermometer",
        False,
        0,
        100,
        DEFAULT_STEP,
    ],

    # We should not use the HEATING setpoint directly - adjust
    # the heat curve instead!
    #"temp_heating_setpoint": [
    #    "Temperature Heating Demand",
    #    EcotouchTag.TEMPERATURE_HEATING_SETPOINT,
    #    NumberDeviceClass.TEMPERATURE,
    #    "mdi:thermometer",
    #    False,
    #   0,
    #   100,
    #   DEFAULT_STEP,
    #],

    # Heizung - Heizkennlinie
    # A93
    "TEMPERATURE_HEATING_HC_LIMIT": [
        "Temperature heating curve heating limit",
        EcotouchTag.TEMPERATURE_HEATING_HC_LIMIT,
        NumberDeviceClass.TEMPERATURE,
        "mdi:thermometer",
        False,
        0,
        100,
        DEFAULT_STEP,
    ],
    # A94
    "TEMPERATURE_HEATING_HC_TARGET": [
        "Temperature heating curve heating limit target",
        EcotouchTag.TEMPERATURE_HEATING_HC_TARGET,
        NumberDeviceClass.TEMPERATURE,
        "mdi:thermometer",
        False,
        0,
        100,
        DEFAULT_STEP,
    ],
    # A91
    "TEMPERATURE_HEATING_HC_OUTDOOR_NORM": [
        "Temperature heating curve norm outdoor",
        EcotouchTag.TEMPERATURE_HEATING_HC_OUTDOOR_NORM,
        NumberDeviceClass.TEMPERATURE,
        "mdi:thermometer",
        False,
        0,
        100,
        DEFAULT_STEP,
    ],
    # A92
    "TEMPERATURE_HEATING_HC_NORM": [
        "Temperature heating curve norm heating circle",
        EcotouchTag.TEMPERATURE_HEATING_HC_NORM,
        NumberDeviceClass.TEMPERATURE,
        "mdi:thermometer",
        False,
        0,
        100,
        DEFAULT_STEP,
    ],
    # A95
    "TEMPERATURE_HEATING_SETPOINTLIMIT_MAX": [
        "Temperature heating curve Limit for setpoint (Max.)",
        EcotouchTag.TEMPERATURE_HEATING_SETPOINTLIMIT_MAX,
        NumberDeviceClass.TEMPERATURE,
        "mdi:thermometer",
        False,
        0,
        100,
        DEFAULT_STEP,
    ],
    # A104
    "TEMPERATURE_HEATING_SETPOINTLIMIT_MIN": [
        "Temperature heating curve Limit for setpoint (Min.)",
        EcotouchTag.TEMPERATURE_HEATING_SETPOINTLIMIT_MIN,
        NumberDeviceClass.TEMPERATURE,
        "mdi:thermometer",
        False,
        -40,
        100,
        DEFAULT_STEP,
    ],
    # A38 - Warmwasser
    "TEMPERATURE_WATER_SETPOINT": [
        "Temperature Hot Water setpoint",
        EcotouchTag.TEMPERATURE_WATER_SETPOINT,
        NumberDeviceClass.TEMPERATURE,
        "mdi:thermometer",
        False,
        0,
        100,
        DEFAULT_STEP,
    ],
    # Mischerkreis 1 Heizkennlinie
    # A276
    "TEMPERATURE_MIX1_HC_LIMIT": [
        "Temperature mixing circle 1 heating limit",
        EcotouchTag.TEMPERATURE_MIX1_HC_LIMIT,
        NumberDeviceClass.TEMPERATURE,
        "mdi:thermometer",
        False,
        0,
        100,
        DEFAULT_STEP,
    ],
    # A277
    "TEMPERATURE_MIX1_HC_TARGET": [
        "Temperature mixing circle 1 heating limit target",
        EcotouchTag.TEMPERATURE_MIX1_HC_TARGET,
        NumberDeviceClass.TEMPERATURE,
        "mdi:thermometer",
        False,
        0,
        100,
        DEFAULT_STEP,
    ],
    # A274
    "TEMPERATURE_MIX1_HC_OUTDOOR_NORM": [
        "Temperature mixing circle 1 norm outdoor",
        EcotouchTag.TEMPERATURE_MIX1_HC_OUTDOOR_NORM,
        NumberDeviceClass.TEMPERATURE,
        "mdi:thermometer",
        False,
        0,
        100,
        DEFAULT_STEP,
    ],
    # A275
    "TEMPERATURE_MIX1_HC_HEATING_NORM": [
        "Temperature mixing circle 1 norm heating circle",
        EcotouchTag.TEMPERATURE_MIX1_HC_HEATING_NORM,
        NumberDeviceClass.TEMPERATURE,
        "mdi:thermometer",
        False,
        0,
        100,
        DEFAULT_STEP,
    ],
    # A278
    "TEMPERATURE_MIX1_HC_MAX": [
        "Temperature mixing circle 1 Limit for setpoint (Max.)",
        EcotouchTag.TEMPERATURE_MIX1_HC_MAX,
        NumberDeviceClass.TEMPERATURE,
        "mdi:thermometer",
        False,
        0,
        100,
        DEFAULT_STEP,
    ],
    # Mischerkreis 2 Heizkennlinie
    "TEMPERATURE_MIX2_HC_LIMIT": [
        "Temperature mixing circle 2 heating limit",
        EcotouchTag.TEMPERATURE_MIX2_HC_LIMIT,
        NumberDeviceClass.TEMPERATURE,
        "mdi:thermometer",
        False,
        0,
        100,
        DEFAULT_STEP,
    ],
    "TEMPERATURE_MIX2_HC_TARGET": [
        "Temperature mixing circle 2 heating limit target",
        EcotouchTag.TEMPERATURE_MIX2_HC_TARGET,
        NumberDeviceClass.TEMPERATURE,
        "mdi:thermometer",
        False,
        0,
        100,
        DEFAULT_STEP,
    ],
    "TEMPERATURE_MIX2_HC_OUTDOOR_NORM": [
        "Temperature mixing circle 2 norm outdoor",
        EcotouchTag.TEMPERATURE_MIX2_HC_OUTDOOR_NORM,
        NumberDeviceClass.TEMPERATURE,
        "mdi:thermometer",
        False,
        0,
        100,
        DEFAULT_STEP,
    ],
    "TEMPERATURE_MIX2_HC_HEATING_NORM": [
        "Temperature mixing circle 2 norm heating circle",
        EcotouchTag.TEMPERATURE_MIX2_HC_HEATING_NORM,
        NumberDeviceClass.TEMPERATURE,
        "mdi:thermometer",
        False,
        0,
        100,
        DEFAULT_STEP,
    ],
    "TEMPERATURE_MIX2_HC_MAX": [
        "Temperature mixing circle 2 Limit for setpoint (Max.)",
        EcotouchTag.TEMPERATURE_MIX2_HC_MAX,
        NumberDeviceClass.TEMPERATURE,
        "mdi:thermometer",
        False,
        0,
        100,
        DEFAULT_STEP,
    ],
}

# async def async_setup_entry(hass: HomeAssistantType, entry: ConfigType, async_add_entities) -> None:
async def async_setup_entry(
        hass: HomeAssistantType, entry: ConfigType, async_add_devices
) -> None:
    """Set up the Waterkotte sensor platform."""
    _LOGGER.debug("Sensor async_setup_entry")
    coordinator = hass.data[DOMAIN][entry.entry_id]
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
    def device_class(self):
        """Return the device class of the sensor."""
        return SENSOR_TYPES[self._type][2]

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return SENSOR_TYPES[self._type][3]
        # return ICON

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
    def unique_id(self):
        """Return the unique of the sensor."""
        return self._unique_id

    async def async_update(self):
        """Schedule a custom update via the common entity update service."""
        await self._coordinator.async_request_refresh()

    @property
    def should_poll(self) -> bool:
        """Entities do not individually poll."""
        return False
