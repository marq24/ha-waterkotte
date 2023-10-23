"""Select platform for Waterkotte Heatpump."""
import logging
from dataclasses import dataclass

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.helpers.typing import ConfigType, HomeAssistantType

from custom_components.waterkotte_heatpump.pywaterkotte_ha.ecotouch import EcotouchTag
from .entity import WaterkotteHeatpumpEntity, WaterkotteHeatpumpEntity2

from .const import ENUM_OFFAUTOMANUAL, ENUM_HEATING_MODE, DEVICE_CLASS_ENUM, DOMAIN

_LOGGER = logging.getLogger(__name__)

# Sensor types are defined as:
#   variable -> [0]title, [1] EcoTouchTag, [2]device_class, [3]units, [4]icon, [5]enabled_by_default, [6]options, [7]entity_category #pylint: disable=line-too-long
SENSOR_TYPES = {
    "enable_cooling": [
        "Enable Cooling",
        EcotouchTag.ENABLE_COOLING,
        DEVICE_CLASS_ENUM,
        None,
        "mdi:snowflake-thermometer",
        True,
        ENUM_OFFAUTOMANUAL,
        None,
    ],
    "enable_heating": [
        "Enable Heating",
        EcotouchTag.ENABLE_HEATING,
        DEVICE_CLASS_ENUM,
        None,
        "mdi:radiator",
        True,
        ENUM_OFFAUTOMANUAL,
        None,
    ],
    "enable_pv": [
        "Enable PV",
        EcotouchTag.ENABLE_PV,
        DEVICE_CLASS_ENUM,
        None,
        "mdi:solar-power",
        False,
        ENUM_OFFAUTOMANUAL,
        None,
    ],
    "enable_warmwater": [
        "Enable Warmwater",
        EcotouchTag.ENABLE_WARMWATER,
        DEVICE_CLASS_ENUM,
        None,
        "mdi:water-thermometer",
        True,
        ENUM_OFFAUTOMANUAL,
        None,
    ],
    # I265
    "temperature_heating_mode": [
        "Heating Control",
        EcotouchTag.TEMPERATURE_HEATING_MODE,
        DEVICE_CLASS_ENUM,
        None,
        "mdi:radiator",
        False,
        ENUM_HEATING_MODE,
        None,
    ],
}


@dataclass
class ExtSelectEntityDescription(SelectEntityDescription):
    tag: EcotouchTag | None = None


SENSOR_TYPES2 = [
    ExtSelectEntityDescription(
        key="temperature_heating_mode",
        tag=EcotouchTag.TEMPERATURE_HEATING_MODE,
        name="Heating Control",
        entity_registry_enabled_default=True,
        options=ENUM_HEATING_MODE,
        icon="mdi:radiator"
    )
]


async def async_setup_entry(hass: HomeAssistantType, entry: ConfigType, async_add_devices) -> None:
    """Set up the Waterkotte Select platform."""
    _LOGGER.debug("Select async_setup_entry")
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices([WaterkotteHeatpumpSelect(entry, coordinator, sensor_type)
                       for sensor_type in SENSOR_TYPES])

    # async_add_devices([WaterkotteHeatpumpSelect2(coordinator, sensor_type)
    #                   for sensor_type in SENSOR_TYPES2])


class WaterkotteHeatpumpSelect(SelectEntity, WaterkotteHeatpumpEntity):
    """waterkotte_heatpump Sensor class."""

    def __init__(self, entry, coordinator, sensor_type):  # pylint: disable=unused-argument
        """Initialize the sensor."""
        super().__init__(coordinator, entry)
        self.entity_id = f"{DOMAIN}.wkh_{sensor_type}"
        self._coordinator = coordinator
        self._type = sensor_type
        self._attr_unique_id = sensor_type
        self._entry_data = entry.data
        self._device_id = entry.entry_id
        self._attr_translation_key = self._type.lower()

    @property
    def current_option(self) -> str | None:
        try:
            value = self._coordinator.data[self.eco_tag]["value"]
            if value is None or value == "":
                value = 'unknown'
        except KeyError:
            value = "unknown"
        except TypeError:
            return None
        return value
        # return "auto"

    @property
    def options(self) -> list[str]:
        # return ["off", "auto", "manual"]
        return SENSOR_TYPES[self._type][6]

    async def async_select_option(self, option: str) -> None:  # pylint: disable=unused-argument
        """Turn on the switch."""
        try:
            await self._coordinator.async_write_tag(self.eco_tag, option)
        except ValueError:
            return "unavailable"

    @property
    def eco_tag(self):
        """Return a unique ID to use for this entity."""
        return SENSOR_TYPES[self._type][1]

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return SENSOR_TYPES[self._type][2]

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return SENSOR_TYPES[self._type][4]
        # return ICON

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

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return SENSOR_TYPES[self._type][3]

    async def async_update(self):
        """Schedule a custom update via the common entity update service."""
        await self._coordinator.async_request_refresh()

    @property
    def should_poll(self) -> bool:
        """Entities do not individually poll."""
        return False


class WaterkotteHeatpumpSelect2(WaterkotteHeatpumpEntity2, SelectEntity):
    def __init__(
            self,
            coordinator,
            description: ExtSelectEntityDescription
    ):
        """Initialize a singular value sensor."""
        super().__init__(coordinator=coordinator, description=description)

        self._tag = description.tag
        if (hasattr(self.entity_description, 'entity_registry_enabled_default')):
            self._attr_entity_registry_enabled_default = self.entity_description.entity_registry_enabled_default
        else:
            self._attr_entity_registry_enabled_default = True

        key = self.entity_description.key.lower()
        self.entity_id = f"{DOMAIN}.wkh_{key}"

        if description.options is not None:
            self._attr_options = description.options

        # we use the "key" also as our internal translation-key - and EXTREMELY important we have
        # to set the '_attr_has_entity_name' to trigger the calls to the localization framework!
        self._attr_translation_key = f"{key}"
        self._attr_has_entity_name = True

        # if hasattr(description, 'suggested_display_precision') and description.suggested_display_precision is not None:
        #    self._attr_suggested_display_precision = description.suggested_display_precision
        # else:
        #    self._attr_suggested_display_precision = 2

    @property
    def current_option(self) -> str | None:
        try:
            value = self.coordinator.data[self._tag]["value"]
            if value is None or value == "":
                value = 'unknown'
        except KeyError:
            value = "unknown"
        except TypeError:
            return None
        return value
