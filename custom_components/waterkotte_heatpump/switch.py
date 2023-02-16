"""Switch platform for Waterkotte Heatpump."""
import logging
from homeassistant.components.switch import SwitchEntity

from custom_components.waterkotte_heatpump.mypywaterkotte.ecotouch import EcotouchTag
from .const import DOMAIN

from .entity import WaterkotteHeatpumpEntity

# from .const import DOMAIN  # , NAME, CONF_FW, CONF_BIOS, CONF_IP

_LOGGER = logging.getLogger(__name__)


# Sensor types are defined as:
#   variable -> [0]title, [1] EcoTouchTag, [2]device_class, [3]units, [4]icon, [5]enabled_by_default, [6]options, [7]entity_category  #pylint: disable=line-too-long
SENSOR_TYPES = {
    "HOLIDAY_ENABLED": [
        "Holiday Mode",
        EcotouchTag.HOLIDAY_ENABLED,
        None,
        None,
        None,
        True,
        None,
        None,
    ],
}


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    # coordinator = hass.data[DOMAIN][entry.entry_id]
    # async_add_devices([WaterkotteHeatpumpBinarySwitch(coordinator, entry)])
    # hass_data = hass.data[DOMAIN][entry.entry_id]
    _LOGGER.debug("Sensor async_setup_entry")
    coordinator = hass.data[DOMAIN][entry.entry_id]
    # async_add_devices([WaterkotteHeatpumpSensor(entry, coordinator, "temperature_condensation")])
    # async_add_devices([WaterkotteHeatpumpSensor(entry, coordinator, "temperature_evaporation")])
    async_add_devices(
        [
            WaterkotteHeatpumpBinarySwitch(entry, coordinator, sensor_type)
            for sensor_type in SENSOR_TYPES
        ]
    )


class WaterkotteHeatpumpBinarySwitch(WaterkotteHeatpumpEntity, SwitchEntity):
    """waterkotte_heatpump switch class."""

    def __init__(
        self, entry, hass_data, sensor_type
    ):  # pylint: disable=unused-argument
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

    def __del__(self):
        try:
            del self._coordinator[self._unique_id]
        except Exception:  # pylint: disable=broad-except
            pass

    async def async_turn_on(self, **kwargs):  # pylint: disable=unused-argument
        """Turn on the switch."""
        # await self.coordinator.api.async_set_title("bar")
        # await self.coordinator.async_request_refresh()
        try:
            # print(option)
            # await self._coordinator.api.async_write_value(SENSOR_TYPES[self._type][1], option)
            await self._coordinator.async_write_tag(SENSOR_TYPES[self._type][1], True)
            sensor = SENSOR_TYPES[self._type]
            return self._coordinator.data[sensor[1]]["value"]
        except ValueError:
            return "unavailable"

    async def async_turn_off(self, **kwargs):  # pylint: disable=unused-argument
        """Turn off the switch."""
        # await self.coordinator.api.async_set_title("foo")
        # await self.coordinator.async_request_refresh()
        try:
            # print(option)
            # await self._coordinator.api.async_write_value(SENSOR_TYPES[self._type][1], option)
            await self._coordinator.async_write_tag(SENSOR_TYPES[self._type][1], False)
            sensor = SENSOR_TYPES[self._type]
            return self._coordinator.data[sensor[1]]["value"]
        except ValueError:
            return "unavailable"

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

    @property
    def tag(self):
        """Return a unique ID to use for this entity."""
        return SENSOR_TYPES[self._type][1]

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def icon(self):
        """Return the icon of the sensor."""
        if SENSOR_TYPES[self._type][4] is None:
            sensor = SENSOR_TYPES[self._type]
            try:
                if (
                    self._type == "holiday_enabled"
                    and sensor[1] in self._coordinator.data
                ):
                    if self._coordinator.data[sensor[1]]["value"] is True:
                        return "mdi:calendar-check"
                    else:
                        return "mdi:calendar-blank"
                else:
                    return None
            except KeyError:
                print(
                    f"KeyError in switch.icon: should have value? data:{self._coordinator.data[sensor[1]]}"
                )
            except TypeError:
                return None
        return SENSOR_TYPES[self._type][4]
        # return ICON

    # @property
    # def is_on(self):
    #     """Return true if the switch is on."""
    #     return self.coordinator.data.get("title", "") == "foo"

    @property
    def entity_registry_enabled_default(self):
        """Return the entity_registry_enabled_default of the sensor."""
        return SENSOR_TYPES[self._type][5]

    @property
    def unique_id(self):
        """Return the unique of the sensor."""
        return self._unique_id
