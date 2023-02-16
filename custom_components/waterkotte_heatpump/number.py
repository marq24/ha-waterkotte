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

ADAPT_LOOKUP = [-2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2]

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
