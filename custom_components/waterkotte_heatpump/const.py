"""Constants for Waterkotte Heatpump."""
from typing import Final

from dataclasses import dataclass

from homeassistant.components.binary_sensor import BinarySensorEntityDescription
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.number import NumberEntityDescription
from homeassistant.components.number import NumberDeviceClass, NumberMode, DEFAULT_STEP
from homeassistant.components.select import SelectEntityDescription
from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.components.switch import SwitchEntityDescription

from homeassistant.const import UnitOfTemperature, PERCENTAGE, UnitOfEnergy, UnitOfPower, UnitOfPressure, UnitOfTime, \
    CONCENTRATION_PARTS_PER_MILLION, CONCENTRATION_MICROGRAMS_PER_CUBIC_METER, REVOLUTIONS_PER_MINUTE

from custom_components.waterkotte_heatpump.pywaterkotte_ha.const import SIX_STEPS_MODES
from custom_components.waterkotte_heatpump.pywaterkotte_ha import EcotouchTag

# Base component constants
NAME: Final = "Waterkotte Heatpump [+2020]"
DOMAIN: Final = "waterkotte_heatpump"

TITLE: Final = "Waterkotte"
ISSUE_URL: Final = "https://github.com/marq24/ha-waterkotte/issues"

FEATURE_DISINFECTION: Final = "DISINFECTION"
FEATURE_HEATING_CURVE: Final = "HEATING_CURVE"
FEATURE_VENT: Final = "VENT"
FEATURE_POOL: Final = "POOL"

# Device classes
DEVICE_CLASS_ENUM: Final = "enum"

# States
STATE_AUTO: Final = "auto"
STATE_MANUAL: Final = "manual"
STATE_ON: Final = "on"
STATE_OFF: Final = "off"
# # #### Enum Options ####
ENUM_ONOFFAUTO: Final = [STATE_ON, STATE_OFF, STATE_AUTO]
ENUM_OFFAUTOMANUAL: Final = [STATE_OFF, STATE_AUTO, STATE_MANUAL]
ENUM_HEATING_MODE: Final = list(SIX_STEPS_MODES.values())
ENUM_VENT_OPERATION_MODE: Final = list(SIX_STEPS_MODES.values())

# Configuration and options
CONF_IP: Final = "ip"
CONF_POLLING_INTERVAL: Final = "polling_interval"
CONF_TAGS_PER_REQUEST: Final = "tags_per_request"
CONF_BIOS: Final = "bios"
CONF_FW: Final = "fw"
CONF_SERIAL: Final = "serial"
CONF_SERIES: Final = "series"
CONF_SYSTEMTYPE: Final = "system_type"
CONF_USE_DISINFECTION: Final = "use_disinfection"
CONF_USE_HEATING_CURVE: Final = "use_heating_curve"
CONF_USE_VENT: Final = "use_vent"
CONF_USE_POOL: Final = "use_pool"

STARTUP_MESSAGE: Final = f"""
-------------------------------------------------------------------
{NAME}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""

SERVICE_SET_HOLIDAY: Final = "set_holiday"
SERVICE_SET_DISINFECTION_START_TIME: Final = "set_disinfection_start_time"
SERVICE_GET_ENERGY_BALANCE: Final = "get_energy_balance"
SERVICE_GET_ENERGY_BALANCE_MONTHLY: Final = "get_energy_balance_monthly"

TENTH_STEP = 0.1
FIFTH_STEP = 0.5


@dataclass(frozen=True)
class ExtBinarySensorEntityDescription(BinarySensorEntityDescription):
    tag: EcotouchTag | None = None
    feature: str | None = None


@dataclass(frozen=True)
class ExtNumberEntityDescription(NumberEntityDescription):
    tag: EcotouchTag | None = None
    feature: str | None = None

@dataclass(frozen=True)
class ExtSelectEntityDescription(SelectEntityDescription):
    tag: EcotouchTag | None = None
    feature: str | None = None
    # controls: list[str] | None = None


@dataclass(frozen=True)
class ExtSensorEntityDescription(SensorEntityDescription):
    tag: EcotouchTag | None = None
    feature: str | None = None
    # selfimplemented_display_precision: int | None = None
    # controls: list[str] | None = None


@dataclass(frozen=True)
class ExtSwitchEntityDescription(SwitchEntityDescription):
    tag: EcotouchTag | None = None
    feature: str | None = None
    icon_off: str | None = None


PLATFORMS: Final = ["binary_sensor", "number", "select", "sensor", "switch"]

BINARY_SENSORS = [
    ExtBinarySensorEntityDescription(
        key="STATE_SOURCEPUMP",
        tag=EcotouchTag.STATE_SOURCEPUMP,
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:water-pump",
        entity_registry_enabled_default=True
    ),
    ExtBinarySensorEntityDescription(
        key="STATE_HEATINGPUMP",
        tag=EcotouchTag.STATE_HEATINGPUMP,
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:heat-pump",
        entity_registry_enabled_default=True
    ),
    # EVD: -> Überhitzungsregler
    ExtBinarySensorEntityDescription(
        key="STATE_EVD",
        tag=EcotouchTag.STATE_EVD,
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:thermometer-high",
        entity_registry_enabled_default=True
    ),
    ExtBinarySensorEntityDescription(
        key="STATE_COMPRESSOR",
        tag=EcotouchTag.STATE_COMPRESSOR,
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:gauge",
        entity_registry_enabled_default=True
    ),
    ExtBinarySensorEntityDescription(
        key="STATE_COMPRESSOR2",
        tag=EcotouchTag.STATE_COMPRESSOR2,
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:gauge",
        entity_registry_enabled_default=True
    ),
    ExtBinarySensorEntityDescription(
        key="STATE_EXTERNAL_HEATER",
        tag=EcotouchTag.STATE_EXTERNAL_HEATER,
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:heating-coil",
        entity_registry_enabled_default=True
    ),
    ExtBinarySensorEntityDescription(
        key="STATE_ALARM",
        tag=EcotouchTag.STATE_ALARM,
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:alert",
        entity_registry_enabled_default=False
    ),
    ExtBinarySensorEntityDescription(
        key="STATE_COOLING",
        tag=EcotouchTag.STATE_COOLING,
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:snowflake-thermometer",
        entity_registry_enabled_default=False
    ),
    ExtBinarySensorEntityDescription(
        key="STATE_WATER",
        tag=EcotouchTag.STATE_WATER,
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:water-thermometer",
        entity_registry_enabled_default=True
    ),
    ExtBinarySensorEntityDescription(
        key="STATE_POOL",
        tag=EcotouchTag.STATE_POOL,
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:pool",
        entity_registry_enabled_default=False,
        feature=FEATURE_POOL
    ),
    ExtBinarySensorEntityDescription(
        key="STATE_SOLAR",
        tag=EcotouchTag.STATE_SOLAR,
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:solar-power-variant",
        entity_registry_enabled_default=False
    ),
    ExtBinarySensorEntityDescription(
        key="STATE_COOLING4WAY",
        tag=EcotouchTag.STATE_COOLING4WAY,
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:snowflake-thermometer",
        entity_registry_enabled_default=False
    ),
    # status sensors (Operation Mode 0=off, 1=on or 2=disabled)
    ExtBinarySensorEntityDescription(
        key="STATUS_HEATING",
        tag=EcotouchTag.STATUS_HEATING,
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:radiator",
        entity_registry_enabled_default=True
    ),
    ExtBinarySensorEntityDescription(
        key="STATUS_WATER",
        tag=EcotouchTag.STATUS_WATER,
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:water-thermometer",
        entity_registry_enabled_default=True
    ),
    ExtBinarySensorEntityDescription(
        key="STATUS_COOLING",
        tag=EcotouchTag.STATUS_COOLING,
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:snowflake-thermometer",
        entity_registry_enabled_default=True
    ),
    ExtBinarySensorEntityDescription(
        key="STATUS_POOL",
        tag=EcotouchTag.STATUS_POOL,
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:pool-thermometer",
        entity_registry_enabled_default=False,
        feature=FEATURE_POOL
    ),
    ExtBinarySensorEntityDescription(
        key="STATE_BLOCKING_TIME",
        tag=EcotouchTag.STATE_BLOCKING_TIME,
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:electric-switch",
        entity_registry_enabled_default=False
    ),
    ExtBinarySensorEntityDescription(
        key="STATE_TEST_RUN",
        tag=EcotouchTag.STATE_TEST_RUN,
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:heating-coil",
        entity_registry_enabled_default=True
    ),
    # this is just indicates if the heating circulation pump is running -
    # unfortunately this can't TAG is not writable (at least write does
    # not have any effect)
    ExtBinarySensorEntityDescription(
        key="STATE_HEATING_CIRCULATION_PUMP_D425",
        tag=EcotouchTag.STATE_HEATING_CIRCULATION_PUMP_D425,
        entity_registry_enabled_default=True
    ),
    ExtBinarySensorEntityDescription(
        key="STATE_BUFFERTANK_CIRCULATION_PUMP_D377",
        tag=EcotouchTag.STATE_BUFFERTANK_CIRCULATION_PUMP_D377,
        entity_registry_enabled_default=True
    ),
    ExtBinarySensorEntityDescription(
        key="STATE_POOL_CIRCULATION_PUMP_D549",
        tag=EcotouchTag.STATE_POOL_CIRCULATION_PUMP_D549,
        entity_registry_enabled_default=False,
        feature=FEATURE_POOL
    ),
    ExtBinarySensorEntityDescription(
        key="STATE_MIX1_CIRCULATION_PUMP_D248",
        tag=EcotouchTag.STATE_MIX1_CIRCULATION_PUMP_D248,
        entity_registry_enabled_default=True
    ),

    ExtBinarySensorEntityDescription(
        key="STATE_MIX2_CIRCULATION_PUMP_D291",
        tag=EcotouchTag.STATE_MIX2_CIRCULATION_PUMP_D291,
        entity_registry_enabled_default=False
    ),

    ExtBinarySensorEntityDescription(
        key="STATE_MIX3_CIRCULATION_PUMP_D334",
        tag=EcotouchTag.STATE_MIX3_CIRCULATION_PUMP_D334,
        entity_registry_enabled_default=False
    ),
    ExtBinarySensorEntityDescription(
        key="STATUS_SOLAR",
        tag=EcotouchTag.STATUS_SOLAR,
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:solar-power-variant",
        entity_registry_enabled_default=False
    ),

    ExtBinarySensorEntityDescription(
        key="BASICVENT_STATUS_BYPASS_ACTIVE_D1432",
        tag=EcotouchTag.BASICVENT_STATUS_BYPASS_ACTIVE_D1432,
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:electric-switch",
        entity_registry_enabled_default=False,
        feature=FEATURE_VENT
    ),
    ExtBinarySensorEntityDescription(
        key="BASICVENT_STATUS_HUMIDIFIER_ACTIVE_D1433",
        tag=EcotouchTag.BASICVENT_STATUS_HUMIDIFIER_ACTIVE_D1433,
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:electric-switch",
        entity_registry_enabled_default=False,
        feature=FEATURE_VENT
    ),
    ExtBinarySensorEntityDescription(
        key="BASICVENT_STATUS_COMFORT_BYPASS_ACTIVE_D1465",
        tag=EcotouchTag.BASICVENT_STATUS_COMFORT_BYPASS_ACTIVE_D1465,
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:electric-switch",
        entity_registry_enabled_default=False,
        feature=FEATURE_VENT
    ),
    ExtBinarySensorEntityDescription(
        key="BASICVENT_STATUS_SMART_BYPASS_ACTIVE_D1466",
        tag=EcotouchTag.BASICVENT_STATUS_SMART_BYPASS_ACTIVE_D1466,
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:electric-switch",
        entity_registry_enabled_default=False,
        feature=FEATURE_VENT
    ),
    ExtBinarySensorEntityDescription(
        key="BASICVENT_STATUS_HOLIDAY_ENABLED_D1503",
        tag=EcotouchTag.BASICVENT_STATUS_HOLIDAY_ENABLED_D1503,
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:electric-switch",
        entity_registry_enabled_default=False,
        feature=FEATURE_VENT
    ),
    ExtBinarySensorEntityDescription(
        key="BASICVENT_FILTER_CHANGE_DISPLAY_D1469",
        tag=EcotouchTag.BASICVENT_FILTER_CHANGE_DISPLAY_D1469,
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:electric-switch",
        entity_registry_enabled_default=False,
        feature=FEATURE_VENT
    )

    # "STATUS_HEATING_CIRCULATION_PUMP",
    #     "Status circulation pump heating",
    #     tag=EcotouchTag.STATUS_HEATING_CIRCULATION_PUMP,
    #     device_class=BinarySensorDeviceClass.RUNNING,
    #     #     icon="mdi:pump",
    #     entity_registry_enabled_default=True,
    #     #     #     "I1270"
    # ],
    # "STATUS_SOLAR_CIRCULATION_PUMP",
    #     "Status circulation pump Solar",
    #     tag=EcotouchTag.STATUS_SOLAR_CIRCULATION_PUMP,
    #     device_class=BinarySensorDeviceClass.RUNNING,
    #     #     icon="mdi:pump",
    #     entity_registry_enabled_default=False,
    #     #     #     "I1287"
    # ],
    # "STATUS_BUFFER_TANK_CIRCULATION_PUMP",
    #     "Status circulation pump buffer tank",
    #     tag=EcotouchTag.STATUS_BUFFER_TANK_CIRCULATION_PUMP,
    #     device_class=BinarySensorDeviceClass.RUNNING,
    #     icon="mdi:pump",
    #     entity_registry_enabled_default=True,
    #     #     #     "I1291"
    # ],
    # "STATUS_COMPRESSOR",
    #     "Status compressor",
    #     tag=EcotouchTag.STATUS_COMPRESSOR,
    #     device_class=BinarySensorDeviceClass.RUNNING,
    #     icon="mdi:gauge",
    #     entity_registry_enabled_default=True,
    #     #     #     "I1307"
    # ],
]

NUMBER_SENSORS = [
    # temperature sensors
    # not sure if this RETURN temperature should be set able at all?!
    ExtNumberEntityDescription(
        key="TEMPERATURE_RETURN_SETPOINT",
        tag=EcotouchTag.TEMPERATURE_RETURN_SETPOINT,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:thermometer",
        entity_registry_enabled_default=False,
        native_min_value=0,
        native_max_value=100,
        native_step=DEFAULT_STEP,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    # Cooling/Kuehlung...
    # A109
    ExtNumberEntityDescription(
        key="TEMPERATURE_COOLING_SETPOINT",
        tag=EcotouchTag.TEMPERATURE_COOLING_SETPOINT,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:snowflake-thermometer",
        entity_registry_enabled_default=False,
        native_min_value=5,
        native_max_value=26,
        native_step=TENTH_STEP,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    # A108
    ExtNumberEntityDescription(
        key="TEMPERATURE_COOLING_OUTDOOR_LIMIT",
        tag=EcotouchTag.TEMPERATURE_COOLING_OUTDOOR_LIMIT,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:snowflake-thermometer",
        entity_registry_enabled_default=False,
        native_min_value=0,
        native_max_value=100,
        native_step=DEFAULT_STEP,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    # Heizung
    # A32 manual heat-setpoint (when heat_mode = 1)
    ExtNumberEntityDescription(
        key="TEMPERATURE_HEATING_SETPOINT",
        tag=EcotouchTag.TEMPERATURE_HEATING_SETPOINT,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:radiator",
        entity_registry_enabled_default=True,
        native_min_value=15,
        native_max_value=60,
        native_step=TENTH_STEP,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    ExtNumberEntityDescription(
        key="TEMPERATURE_HEATING_ADJUST",
        tag=EcotouchTag.TEMPERATURE_HEATING_ADJUST,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:radiator",
        entity_registry_enabled_default=True,
        native_min_value=-2,
        native_max_value=2,
        native_step=FIFTH_STEP,
        mode=NumberMode.SLIDER,
        native_unit_of_measurement=UnitOfTemperature.KELVIN,
    ),
    ExtNumberEntityDescription(
        key="TEMPERATURE_HEATING_HYSTERESIS",
        tag=EcotouchTag.TEMPERATURE_HEATING_HYSTERESIS,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:radiator",
        entity_registry_enabled_default=True,
        native_min_value=0,
        native_max_value=10,
        native_step=TENTH_STEP,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.KELVIN,
    ),
    ExtNumberEntityDescription(
        key="TEMPERATURE_MIX1_ADJUST",
        tag=EcotouchTag.TEMPERATURE_MIX1_ADJUST,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:numeric-1-circle",
        entity_registry_enabled_default=True,
        native_min_value=-2,
        native_max_value=2,
        native_step=FIFTH_STEP,
        mode=NumberMode.SLIDER,
        native_unit_of_measurement=UnitOfTemperature.KELVIN,
    ),
    ExtNumberEntityDescription(
        key="TEMPERATURE_MIX2_ADJUST",
        tag=EcotouchTag.TEMPERATURE_MIX2_ADJUST,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:numeric-2-circle",
        entity_registry_enabled_default=False,
        native_min_value=-2,
        native_max_value=2,
        native_step=FIFTH_STEP,
        mode=NumberMode.SLIDER,
        native_unit_of_measurement=UnitOfTemperature.KELVIN,
    ),
    ExtNumberEntityDescription(
        key="TEMPERATURE_MIX3_ADJUST",
        tag=EcotouchTag.TEMPERATURE_MIX3_ADJUST,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:numeric-3-circle",
        entity_registry_enabled_default=False,
        native_min_value=-2,
        native_max_value=2,
        native_step=FIFTH_STEP,
        mode=NumberMode.SLIDER,
        native_unit_of_measurement=UnitOfTemperature.KELVIN,
    ),
    # Heizung - Heizkennlinie
    # A93
    ExtNumberEntityDescription(
        key="TEMPERATURE_HEATING_HC_LIMIT",
        tag=EcotouchTag.TEMPERATURE_HEATING_HC_LIMIT,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:radiator",
        entity_registry_enabled_default=False,
        native_min_value=5,
        native_max_value=35,
        native_step=TENTH_STEP,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        feature=FEATURE_HEATING_CURVE
    ),
    # A94
    ExtNumberEntityDescription(
        key="TEMPERATURE_HEATING_HC_TARGET",
        tag=EcotouchTag.TEMPERATURE_HEATING_HC_TARGET,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:radiator",
        entity_registry_enabled_default=False,
        native_min_value=15,
        native_max_value=65,
        native_step=TENTH_STEP,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        feature=FEATURE_HEATING_CURVE
    ),
    # A91
    ExtNumberEntityDescription(
        key="TEMPERATURE_HEATING_HC_OUTDOOR_NORM",
        tag=EcotouchTag.TEMPERATURE_HEATING_HC_OUTDOOR_NORM,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:radiator",
        entity_registry_enabled_default=False,
        native_min_value=-99,
        native_max_value=99,
        native_step=TENTH_STEP,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        feature=FEATURE_HEATING_CURVE
    ),
    # A92
    ExtNumberEntityDescription(
        key="TEMPERATURE_HEATING_HC_NORM",
        tag=EcotouchTag.TEMPERATURE_HEATING_HC_NORM,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:radiator",
        entity_registry_enabled_default=False,
        native_min_value=0,
        native_max_value=99,
        native_step=TENTH_STEP,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        feature=FEATURE_HEATING_CURVE
    ),
    # A95
    ExtNumberEntityDescription(
        key="TEMPERATURE_HEATING_SETPOINTLIMIT_MAX",
        tag=EcotouchTag.TEMPERATURE_HEATING_SETPOINTLIMIT_MAX,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:radiator",
        entity_registry_enabled_default=False,
        native_min_value=0,
        native_max_value=99,
        native_step=TENTH_STEP,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    # A104
    ExtNumberEntityDescription(
        key="TEMPERATURE_HEATING_SETPOINTLIMIT_MIN",
        tag=EcotouchTag.TEMPERATURE_HEATING_SETPOINTLIMIT_MIN,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:radiator",
        entity_registry_enabled_default=False,
        native_min_value=0,
        native_max_value=99,
        native_step=TENTH_STEP,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    # A38 - Warmwasser
    ExtNumberEntityDescription(
        key="TEMPERATURE_WATER_SETPOINT",
        tag=EcotouchTag.TEMPERATURE_WATER_SETPOINT,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:water-thermometer",
        entity_registry_enabled_default=True,
        native_min_value=10,
        native_max_value=70,
        native_step=TENTH_STEP,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    ExtNumberEntityDescription(
        key="TEMPERATURE_WATER_HYSTERESIS",
        tag=EcotouchTag.TEMPERATURE_WATER_HYSTERESIS,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:water-thermometer",
        entity_registry_enabled_default=True,
        native_min_value=0,
        native_max_value=10,
        native_step=TENTH_STEP,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.KELVIN,
    ),
    # Mischerkreis 1 Heizkennlinie
    # A276
    ExtNumberEntityDescription(
        key="TEMPERATURE_MIX1_HC_LIMIT",
        tag=EcotouchTag.TEMPERATURE_MIX1_HC_LIMIT,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:numeric-1-circle",
        entity_registry_enabled_default=False,
        native_min_value=5,
        native_max_value=35,
        native_step=TENTH_STEP,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        feature=FEATURE_HEATING_CURVE
    ),
    # A277
    ExtNumberEntityDescription(
        key="TEMPERATURE_MIX1_HC_TARGET",
        tag=EcotouchTag.TEMPERATURE_MIX1_HC_TARGET,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:numeric-1-circle",
        entity_registry_enabled_default=False,
        native_min_value=15,
        native_max_value=65,
        native_step=TENTH_STEP,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        feature=FEATURE_HEATING_CURVE
    ),
    # A274
    ExtNumberEntityDescription(
        key="TEMPERATURE_MIX1_HC_OUTDOOR_NORM",
        tag=EcotouchTag.TEMPERATURE_MIX1_HC_OUTDOOR_NORM,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:numeric-1-circle",
        entity_registry_enabled_default=False,
        native_min_value=-99,
        native_max_value=99,
        native_step=TENTH_STEP,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        feature=FEATURE_HEATING_CURVE
    ),
    # A275
    ExtNumberEntityDescription(
        key="TEMPERATURE_MIX1_HC_HEATING_NORM",
        tag=EcotouchTag.TEMPERATURE_MIX1_HC_HEATING_NORM,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:numeric-1-circle",
        entity_registry_enabled_default=False,
        native_min_value=0,
        native_max_value=99,
        native_step=TENTH_STEP,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        feature=FEATURE_HEATING_CURVE
    ),
    # A278
    ExtNumberEntityDescription(
        key="TEMPERATURE_MIX1_HC_MAX",
        tag=EcotouchTag.TEMPERATURE_MIX1_HC_MAX,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:numeric-1-circle",
        entity_registry_enabled_default=False,
        native_min_value=15,
        native_max_value=72,
        native_step=TENTH_STEP,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    # Mischerkreis 2 Heizkennlinie
    ExtNumberEntityDescription(
        key="TEMPERATURE_MIX2_HC_LIMIT",
        tag=EcotouchTag.TEMPERATURE_MIX2_HC_LIMIT,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:numeric-2-circle",
        entity_registry_enabled_default=False,
        native_min_value=5,
        native_max_value=35,
        native_step=TENTH_STEP,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    ExtNumberEntityDescription(
        key="TEMPERATURE_MIX2_HC_TARGET",
        tag=EcotouchTag.TEMPERATURE_MIX2_HC_TARGET,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:numeric-2-circle",
        entity_registry_enabled_default=False,
        native_min_value=15,
        native_max_value=65,
        native_step=TENTH_STEP,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    ExtNumberEntityDescription(
        key="TEMPERATURE_MIX2_HC_OUTDOOR_NORM",
        tag=EcotouchTag.TEMPERATURE_MIX2_HC_OUTDOOR_NORM,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:numeric-2-circle",
        entity_registry_enabled_default=False,
        native_min_value=-99,
        native_max_value=99,
        native_step=TENTH_STEP,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    ExtNumberEntityDescription(
        key="TEMPERATURE_MIX2_HC_HEATING_NORM",
        tag=EcotouchTag.TEMPERATURE_MIX2_HC_HEATING_NORM,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:numeric-2-circle",
        entity_registry_enabled_default=False,
        native_min_value=0,
        native_max_value=99,
        native_step=TENTH_STEP,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    ExtNumberEntityDescription(
        key="TEMPERATURE_MIX2_HC_MAX",
        tag=EcotouchTag.TEMPERATURE_MIX2_HC_MAX,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:numeric-2-circle",
        entity_registry_enabled_default=False,
        native_min_value=15,
        native_max_value=72,
        native_step=TENTH_STEP,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    # Mischerkreis 3 Heizkennlinie
    ExtNumberEntityDescription(
        key="TEMPERATURE_MIX3_HC_LIMIT",
        tag=EcotouchTag.TEMPERATURE_MIX3_HC_LIMIT,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:numeric-3-circle",
        entity_registry_enabled_default=False,
        native_min_value=5,
        native_max_value=35,
        native_step=TENTH_STEP,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    ExtNumberEntityDescription(
        key="TEMPERATURE_MIX3_HC_TARGET",
        tag=EcotouchTag.TEMPERATURE_MIX3_HC_TARGET,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:numeric-3-circle",
        entity_registry_enabled_default=False,
        native_min_value=15,
        native_max_value=65,
        native_step=TENTH_STEP,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    ExtNumberEntityDescription(
        key="TEMPERATURE_MIX3_HC_OUTDOOR_NORM",
        tag=EcotouchTag.TEMPERATURE_MIX3_HC_OUTDOOR_NORM,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:numeric-3-circle",
        entity_registry_enabled_default=False,
        native_min_value=-99,
        native_max_value=99,
        native_step=TENTH_STEP,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    ExtNumberEntityDescription(
        key="TEMPERATURE_MIX3_HC_HEATING_NORM",
        tag=EcotouchTag.TEMPERATURE_MIX3_HC_HEATING_NORM,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:numeric-3-circle",
        entity_registry_enabled_default=False,
        native_min_value=0,
        native_max_value=99,
        native_step=TENTH_STEP,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    ExtNumberEntityDescription(
        key="TEMPERATURE_MIX3_HC_MAX",
        tag=EcotouchTag.TEMPERATURE_MIX3_HC_MAX,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:numeric-3-circle",
        entity_registry_enabled_default=False,
        native_min_value=15,
        native_max_value=72,
        native_step=TENTH_STEP,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    # Pool-Temperature Setpoint's
    ExtNumberEntityDescription(
        key="TEMPERATURE_POOL_SETPOINT",
        tag=EcotouchTag.TEMPERATURE_POOL_SETPOINT,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:pool-thermometer",
        entity_registry_enabled_default=False,
        native_min_value=15,
        native_max_value=75,
        native_step=TENTH_STEP,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        feature=FEATURE_POOL
    ),
    ExtNumberEntityDescription(
        key="TEMPERATURE_POOL_HYSTERESIS",
        tag=EcotouchTag.TEMPERATURE_POOL_HYSTERESIS,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:pool-thermometer",
        entity_registry_enabled_default=False,
        native_min_value=0,
        native_max_value=10,
        native_step=TENTH_STEP,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.KELVIN,
        feature=FEATURE_POOL
    ),
    ExtNumberEntityDescription(
        key="TEMPERATURE_POOL_HC_LIMIT",
        tag=EcotouchTag.TEMPERATURE_POOL_HC_LIMIT,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:pool",
        entity_registry_enabled_default=False,
        native_min_value=5,
        native_max_value=35,
        native_step=TENTH_STEP,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        feature=FEATURE_POOL
    ),
    ExtNumberEntityDescription(
        key="TEMPERATURE_POOL_HC_TARGET",
        tag=EcotouchTag.TEMPERATURE_POOL_HC_TARGET,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:pool",
        entity_registry_enabled_default=False,
        native_min_value=15,
        native_max_value=65,
        native_step=TENTH_STEP,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        feature=FEATURE_POOL
    ),
    ExtNumberEntityDescription(
        key="TEMPERATURE_POOL_HC_OUTDOOR_NORM",
        tag=EcotouchTag.TEMPERATURE_POOL_HC_OUTDOOR_NORM,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:pool",
        entity_registry_enabled_default=False,
        native_min_value=-99,
        native_max_value=99,
        native_step=TENTH_STEP,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        feature=FEATURE_POOL
    ),
    ExtNumberEntityDescription(
        key="TEMPERATURE_POOL_HC_NORM",
        tag=EcotouchTag.TEMPERATURE_POOL_HC_NORM,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:pool",
        entity_registry_enabled_default=False,
        native_min_value=0,
        native_max_value=99,
        native_step=TENTH_STEP,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        feature=FEATURE_POOL
    ),
    # Water disinfection start time & duration -> weekdays will be set in
    # switch.py
    ExtNumberEntityDescription(
        key="TEMPERATURE_WATER_DISINFECTION",
        tag=EcotouchTag.TEMPERATURE_WATER_DISINFECTION,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:shield-bug",
        entity_registry_enabled_default=False,
        native_min_value=60,
        native_max_value=70,
        native_step=TENTH_STEP,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        feature=FEATURE_DISINFECTION
    ),
    ExtNumberEntityDescription(
        key="SCHEDULE_WATER_DISINFECTION_DURATION",
        tag=EcotouchTag.SCHEDULE_WATER_DISINFECTION_DURATION,
        device_class=None,  # duration in h
        icon="mdi:progress-clock",
        entity_registry_enabled_default=False,
        native_min_value=0,
        native_max_value=23,
        native_step=DEFAULT_STEP,
        mode=NumberMode.SLIDER,
        native_unit_of_measurement=UnitOfTime.HOURS,
        feature=FEATURE_DISINFECTION
    ),
    ExtNumberEntityDescription(
        key="SOURCE_PUMP_CAPTURE_TEMPERATURE_A479",
        tag=EcotouchTag.SOURCE_PUMP_CAPTURE_TEMPERATURE_A479,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:thermometer",
        entity_registry_enabled_default=False,
        native_min_value=0,
        native_max_value=40,
        native_step=TENTH_STEP,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.KELVIN,
    )
]

SELECT_SENSORS = [
    ExtSelectEntityDescription(
        key="ENABLE_COOLING",
        tag=EcotouchTag.ENABLE_COOLING,
        device_class=DEVICE_CLASS_ENUM,
        icon="mdi:snowflake-thermometer",
        entity_registry_enabled_default=True,
        options=ENUM_OFFAUTOMANUAL,
    ),
    ExtSelectEntityDescription(
        key="ENABLE_HEATING",
        tag=EcotouchTag.ENABLE_HEATING,
        device_class=DEVICE_CLASS_ENUM,
        icon="mdi:radiator",
        entity_registry_enabled_default=True,
        options=ENUM_OFFAUTOMANUAL,
    ),
    ExtSelectEntityDescription(
        key="ENABLE_PV",
        tag=EcotouchTag.ENABLE_PV,
        device_class=DEVICE_CLASS_ENUM,
        icon="mdi:solar-power",
        entity_registry_enabled_default=False,
        options=ENUM_OFFAUTOMANUAL,
    ),
    ExtSelectEntityDescription(
        key="ENABLE_WARMWATER",
        tag=EcotouchTag.ENABLE_WARMWATER,
        device_class=DEVICE_CLASS_ENUM,
        icon="mdi:water-thermometer",
        entity_registry_enabled_default=True,
        options=ENUM_OFFAUTOMANUAL,
    ),
    ExtSelectEntityDescription(
        key="ENABLE_POOL",
        tag=EcotouchTag.ENABLE_POOL,
        device_class=DEVICE_CLASS_ENUM,
        icon="mdi:pool-thermometer",
        entity_registry_enabled_default=False,
        options=ENUM_OFFAUTOMANUAL,
        feature=FEATURE_POOL
    ),
    ExtSelectEntityDescription(
        key="ENABLE_EXTERNAL_HEATER",
        tag=EcotouchTag.ENABLE_EXTERNAL_HEATER,
        device_class=DEVICE_CLASS_ENUM,
        icon="mdi:heating-coil",
        entity_registry_enabled_default=True,
        options=ENUM_OFFAUTOMANUAL,
    ),
    # I265
    ExtSelectEntityDescription(
        key="TEMPERATURE_HEATING_MODE",
        tag=EcotouchTag.TEMPERATURE_HEATING_MODE,
        device_class=DEVICE_CLASS_ENUM,
        icon="mdi:radiator",
        entity_registry_enabled_default=True,
        options=ENUM_HEATING_MODE,
    ),
    ExtSelectEntityDescription(
        key="BASICVENT_OPERATION_MODE_I4582",
        tag=EcotouchTag.BASICVENT_OPERATION_MODE_I4582,
        device_class=DEVICE_CLASS_ENUM,
        icon="mdi:hvac",
        entity_registry_enabled_default=False,
        options=ENUM_VENT_OPERATION_MODE,
        feature=FEATURE_VENT
    )
]

SENSOR_SENSORS = [
    # temperature sensors
    ExtSensorEntityDescription(
        key="TEMPERATURE_OUTSIDE",
        tag=EcotouchTag.TEMPERATURE_OUTSIDE,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:sun-snowflake-variant",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_OUTSIDE_1H",
        tag=EcotouchTag.TEMPERATURE_OUTSIDE_1H,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:sun-snowflake-variant",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_OUTSIDE_24H",
        tag=EcotouchTag.TEMPERATURE_OUTSIDE_24H,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:sun-snowflake-variant",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_SOURCE_ENTRY",
        tag=EcotouchTag.TEMPERATURE_SOURCE_ENTRY,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_SOURCE_EXIT",
        tag=EcotouchTag.TEMPERATURE_SOURCE_EXIT,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_EVAPORATION",
        tag=EcotouchTag.TEMPERATURE_EVAPORATION,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_SUCTION_LINE",
        tag=EcotouchTag.TEMPERATURE_SUCTION_LINE,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_RETURN",
        tag=EcotouchTag.TEMPERATURE_RETURN,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_FLOW",
        tag=EcotouchTag.TEMPERATURE_FLOW,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_CONDENSATION",
        tag=EcotouchTag.TEMPERATURE_CONDENSATION,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_BUFFERTANK",
        tag=EcotouchTag.TEMPERATURE_BUFFERTANK,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:storage-tank",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_ROOM",
        tag=EcotouchTag.TEMPERATURE_ROOM,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermostat-box",
        entity_registry_enabled_default=False
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_ROOM_1H",
        tag=EcotouchTag.TEMPERATURE_ROOM_1H,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermostat-box",
        entity_registry_enabled_default=False
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_HEATING",
        tag=EcotouchTag.TEMPERATURE_HEATING,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:radiator",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_HEATING_DEMAND",
        tag=EcotouchTag.TEMPERATURE_HEATING_DEMAND,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:radiator",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_COOLING",
        tag=EcotouchTag.TEMPERATURE_COOLING,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:snowflake-thermometer",
        entity_registry_enabled_default=False
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_COOLING_DEMAND",
        tag=EcotouchTag.TEMPERATURE_COOLING_DEMAND,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:snowflake-thermometer",
        entity_registry_enabled_default=False
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_WATER",
        tag=EcotouchTag.TEMPERATURE_WATER,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:water-thermometer",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_WATER_DEMAND",
        tag=EcotouchTag.TEMPERATURE_WATER_DEMAND,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:water-thermometer",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_MIX1",
        tag=EcotouchTag.TEMPERATURE_MIX1,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:numeric-1-circle",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_MIX1_PERCENT",
        tag=EcotouchTag.TEMPERATURE_MIX1_PERCENT,
        device_class=None,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:gauge",
        entity_registry_enabled_default=False
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_MIX1_DEMAND",
        tag=EcotouchTag.TEMPERATURE_MIX1_DEMAND,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:numeric-1-circle",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_MIX2",
        tag=EcotouchTag.TEMPERATURE_MIX2,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:numeric-2-circle",
        entity_registry_enabled_default=False
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_MIX2_PERCENT",
        tag=EcotouchTag.TEMPERATURE_MIX2_PERCENT,
        device_class=None,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:gauge",
        entity_registry_enabled_default=False
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_MIX2_DEMAND",
        tag=EcotouchTag.TEMPERATURE_MIX2_DEMAND,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:numeric-2-circle",
        entity_registry_enabled_default=False
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_MIX3",
        tag=EcotouchTag.TEMPERATURE_MIX3,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:numeric-3-circle",
        entity_registry_enabled_default=False
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_MIX3_PERCENT",
        tag=EcotouchTag.TEMPERATURE_MIX3_PERCENT,
        device_class=None,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:gauge",
        entity_registry_enabled_default=False
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_MIX3_DEMAND",
        tag=EcotouchTag.TEMPERATURE_MIX3_DEMAND,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:numeric-3-circle",
        entity_registry_enabled_default=False
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_POOL",
        tag=EcotouchTag.TEMPERATURE_POOL,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:pool-thermometer",
        entity_registry_enabled_default=False,
        feature=FEATURE_POOL
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_POOL_DEMAND",
        tag=EcotouchTag.TEMPERATURE_POOL_DEMAND,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:pool-thermometer",
        entity_registry_enabled_default=False,
        feature=FEATURE_POOL
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_SOLAR",
        tag=EcotouchTag.TEMPERATURE_SOLAR,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:solar-power-variant",
        entity_registry_enabled_default=False
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_SOLAR_EXIT",
        tag=EcotouchTag.TEMPERATURE_SOLAR_EXIT,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:solar-power-variant",
        entity_registry_enabled_default=False
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_DISCHARGE",
        tag=EcotouchTag.TEMPERATURE_DISCHARGE,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer",
        entity_registry_enabled_default=False
    ),
    # other (none temperature) values...
    ExtSensorEntityDescription(
        key="PRESSURE_EVAPORATION",
        tag=EcotouchTag.PRESSURE_EVAPORATION,
        device_class=SensorDeviceClass.PRESSURE,
        native_unit_of_measurement=UnitOfPressure.BAR,
        icon="mdi:gauge",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="PRESSURE_CONDENSATION",
        tag=EcotouchTag.PRESSURE_CONDENSATION,
        device_class=SensorDeviceClass.PRESSURE,
        native_unit_of_measurement=UnitOfPressure.BAR,
        icon="mdi:gauge",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="PRESSURE_WATER",
        tag=EcotouchTag.PRESSURE_WATER,
        device_class=SensorDeviceClass.PRESSURE,
        native_unit_of_measurement=UnitOfPressure.BAR,
        icon="mdi:gauge",
        entity_registry_enabled_default=False
    ),
    # other data...
    ExtSensorEntityDescription(
        key="POSITION_EXPANSION_VALVE",
        tag=EcotouchTag.POSITION_EXPANSION_VALVE,
        device_class=None,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:gauge",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="SUCTION_GAS_OVERHEATING",
        tag=EcotouchTag.SUCTION_GAS_OVERHEATING,
        device_class=None,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:gauge",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="POWER_ELECTRIC",
        tag=EcotouchTag.POWER_ELECTRIC,
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        icon="mdi:meter-electric",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="POWER_HEATING",
        tag=EcotouchTag.POWER_HEATING,
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        icon="mdi:radiator",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="POWER_COOLING",
        tag=EcotouchTag.POWER_COOLING,
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        icon="mdi:snowflake-thermometer",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="COP_HEATING",
        tag=EcotouchTag.COP_HEATING,
        device_class=None,
        native_unit_of_measurement=None,
        icon="mdi:gauge",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="COP_COOLING",
        tag=EcotouchTag.COP_COOLING,
        device_class=None,
        native_unit_of_measurement=None,
        icon="mdi:gauge",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="ENERGY_CONSUMPTION_TOTAL_YEAR",
        tag=EcotouchTag.ENERGY_CONSUMPTION_TOTAL_YEAR,
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        icon="mdi:lightning-bolt-outline",
        entity_registry_enabled_default=True,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=3
    ),
    ExtSensorEntityDescription(
        key="COMPRESSOR_ELECTRIC_CONSUMPTION_YEAR",
        tag=EcotouchTag.COMPRESSOR_ELECTRIC_CONSUMPTION_YEAR,
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        icon="mdi:gauge",
        entity_registry_enabled_default=True,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=3
    ),
    ExtSensorEntityDescription(
        key="SOURCEPUMP_ELECTRIC_CONSUMPTION_YEAR",
        tag=EcotouchTag.SOURCEPUMP_ELECTRIC_CONSUMPTION_YEAR,
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        icon="mdi:water-pump",
        entity_registry_enabled_default=False,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=3
    ),
    ExtSensorEntityDescription(
        key="ELECTRICAL_HEATER_ELECTRIC_CONSUMPTION_YEAR",
        tag=EcotouchTag.ELECTRICAL_HEATER_ELECTRIC_CONSUMPTION_YEAR,
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        icon="mdi:heating-coil",
        entity_registry_enabled_default=True,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=3
    ),
    ExtSensorEntityDescription(
        key="ENERGY_PRODUCTION_TOTAL_YEAR",
        tag=EcotouchTag.ENERGY_PRODUCTION_TOTAL_YEAR,
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        icon="mdi:home-thermometer-outline",
        entity_registry_enabled_default=True,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=3
    ),
    ExtSensorEntityDescription(
        key="HEATING_ENERGY_PRODUCTION_YEAR",
        tag=EcotouchTag.HEATING_ENERGY_PRODUCTION_YEAR,
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        icon="mdi:radiator",
        entity_registry_enabled_default=True,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=3
    ),
    ExtSensorEntityDescription(
        key="HOT_WATER_ENERGY_PRODUCTION_YEAR",
        tag=EcotouchTag.HOT_WATER_ENERGY_PRODUCTION_YEAR,
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        icon="mdi:water-thermometer",
        entity_registry_enabled_default=True,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=3
    ),
    ExtSensorEntityDescription(
        key="POOL_ENERGY_PRODUCTION_YEAR",
        tag=EcotouchTag.POOL_ENERGY_PRODUCTION_YEAR,
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        icon="mdi:pool-thermometer",
        entity_registry_enabled_default=False,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=3,
        feature=FEATURE_POOL
    ),
    ExtSensorEntityDescription(
        key="COOLING_ENERGY_YEAR",
        tag=EcotouchTag.COOLING_ENERGY_YEAR,
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        icon="mdi:snowflake-thermometer",
        entity_registry_enabled_default=True,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=3
    ),
    ExtSensorEntityDescription(
        key="PERCENT_HEAT_CIRC_PUMP",
        tag=EcotouchTag.PERCENT_HEAT_CIRC_PUMP,
        device_class=SensorDeviceClass.POWER_FACTOR,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:gauge",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="PERCENT_SOURCE_PUMP",
        tag=EcotouchTag.PERCENT_SOURCE_PUMP,
        device_class=SensorDeviceClass.POWER_FACTOR,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:gauge",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="PERCENT_COMPRESSOR",
        tag=EcotouchTag.PERCENT_COMPRESSOR,
        device_class=SensorDeviceClass.POWER_FACTOR,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:gauge",
        entity_registry_enabled_default=True
    ),
    # writeable sensors from here...
    ExtSensorEntityDescription(
        key="HOLIDAY_START_TIME",
        tag=EcotouchTag.HOLIDAY_START_TIME,
        device_class=SensorDeviceClass.DATE,
        native_unit_of_measurement=None,
        icon="mdi:calendar-arrow-right",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="HOLIDAY_END_TIME",
        tag=EcotouchTag.HOLIDAY_END_TIME,
        device_class=SensorDeviceClass.DATE,
        native_unit_of_measurement=None,
        icon="mdi:calendar-arrow-left",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="SCHEDULE_WATER_DISINFECTION_START_TIME",
        tag=EcotouchTag.SCHEDULE_WATER_DISINFECTION_START_TIME,
        device_class=SensorDeviceClass.DATE,
        native_unit_of_measurement=None,
        icon="mdi:clock-digital",
        entity_registry_enabled_default=False,
        feature=FEATURE_DISINFECTION
    ),
    ExtSensorEntityDescription(
        key="STATE_SERVICE",
        tag=EcotouchTag.STATE_SERVICE,
        device_class=None,
        native_unit_of_measurement=None,
        icon="mdi:wrench-clock",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="ALARM_BITS",
        tag=EcotouchTag.ALARM_BITS,
        device_class=None,
        native_unit_of_measurement=None,
        icon="mdi:alarm-light",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="INTERRUPTION_BITS",
        tag=EcotouchTag.INTERRUPTION_BITS,
        device_class=None,
        native_unit_of_measurement=None,
        icon="mdi:alert-circle",
        entity_registry_enabled_default=True
    ),

    ExtSensorEntityDescription(
        key="BASICVENT_TEMPERATURE_OUTGOING_AIR_BEFORE_ETH_A4998",
        tag=EcotouchTag.BASICVENT_TEMPERATURE_OUTGOING_AIR_BEFORE_ETH_A4998,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer",
        entity_registry_enabled_default=False,
        suggested_display_precision=1,
        feature=FEATURE_VENT
    ),
    ExtSensorEntityDescription(
        key="BASICVENT_TEMPERATURE_OUTGOING_AIR_AFTER_EEH_A4994",
        tag=EcotouchTag.BASICVENT_TEMPERATURE_OUTGOING_AIR_AFTER_EEH_A4994,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer",
        entity_registry_enabled_default=False,
        suggested_display_precision=1,
        feature=FEATURE_VENT
    ),
    ExtSensorEntityDescription(
        key="BASICVENT_TEMPERATURE_INCOMING_AIR_BEFORE_ODA_A5000",
        tag=EcotouchTag.BASICVENT_TEMPERATURE_INCOMING_AIR_BEFORE_ODA_A5000,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer",
        entity_registry_enabled_default=False,
        suggested_display_precision=1,
        feature=FEATURE_VENT
    ),
    ExtSensorEntityDescription(
        key="BASICVENT_TEMPERATURE_INCOMING_AIR_AFTER_SUP_A4996",
        tag=EcotouchTag.BASICVENT_TEMPERATURE_INCOMING_AIR_AFTER_SUP_A4996,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer",
        entity_registry_enabled_default=False,
        suggested_display_precision=1,
        feature=FEATURE_VENT
    ),
    ExtSensorEntityDescription(
        key="BASICVENT_FILTER_CHANGE_OPERATING_DAYS_A4498",
        tag=EcotouchTag.BASICVENT_FILTER_CHANGE_OPERATING_DAYS_A4498,
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.DAYS,
        unit_of_measurement=UnitOfTime.DAYS,
        icon="mdi:counter",
        entity_registry_enabled_default=False,
        suggested_display_precision=0,
        feature=FEATURE_VENT
    ),
    ExtSensorEntityDescription(
        key="BASICVENT_FILTER_CHANGE_REMAINING_OPERATING_DAYS_A4504",
        tag=EcotouchTag.BASICVENT_FILTER_CHANGE_REMAINING_OPERATING_DAYS_A4504,
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.DAYS,
        unit_of_measurement=UnitOfTime.DAYS,
        icon="mdi:counter",
        entity_registry_enabled_default=False,
        suggested_display_precision=0,
        feature=FEATURE_VENT
    ),
    ExtSensorEntityDescription(
        key="BASICVENT_HUMIDITY_VALUE_A4990",
        tag=EcotouchTag.BASICVENT_HUMIDITY_VALUE_A4990,
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:cloud-percent",
        entity_registry_enabled_default=False,
        suggested_display_precision=1,
        feature=FEATURE_VENT
    ),
    ExtSensorEntityDescription(
        key="BASICVENT_CO2_VALUE_A4992",
        tag=EcotouchTag.BASICVENT_CO2_VALUE_A4992,
        device_class=SensorDeviceClass.CO2,
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
        icon="mdi:molecule-co2",
        entity_registry_enabled_default=False,
        suggested_display_precision=2,
        feature=FEATURE_VENT
    ),
    ExtSensorEntityDescription(
        key="BASICVENT_VOC_VALUE_A4522",
        tag=EcotouchTag.BASICVENT_VOC_VALUE_A4522,
        device_class=SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS,
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        icon="mdi:counter",
        entity_registry_enabled_default=False,
        suggested_display_precision=2,
        feature=FEATURE_VENT
    ),
    ExtSensorEntityDescription(
        key="BASICVENT_INCOMING_FAN_RPM_A4551",
        tag=EcotouchTag.BASICVENT_INCOMING_FAN_RPM_A4551,
        device_class=None,
        native_unit_of_measurement=REVOLUTIONS_PER_MINUTE,
        icon="mdi:wind-power",
        entity_registry_enabled_default=False,
        suggested_display_precision=0,
        feature=FEATURE_VENT
    ),
    ExtSensorEntityDescription(
        key="BASICVENT_INCOMING_FAN_A4986",
        tag=EcotouchTag.BASICVENT_INCOMING_FAN_A4986,
        device_class=None,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:wind-power",
        entity_registry_enabled_default=False,
        suggested_display_precision=1,
        feature=FEATURE_VENT
    ),
    ExtSensorEntityDescription(
        key="BASICVENT_OUTGOING_FAN_RPM_A4547",
        tag=EcotouchTag.BASICVENT_OUTGOING_FAN_RPM_A4547,
        device_class=None,
        native_unit_of_measurement=REVOLUTIONS_PER_MINUTE,
        icon="mdi:wind-power",
        entity_registry_enabled_default=False,
        suggested_display_precision=0,
        feature=FEATURE_VENT
    ),
    ExtSensorEntityDescription(
        key="BASICVENT_OUTGOING_FAN_A4984",
        tag=EcotouchTag.BASICVENT_OUTGOING_FAN_A4984,
        device_class=None,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:wind-power",
        entity_registry_enabled_default=False,
        suggested_display_precision=1,
        feature=FEATURE_VENT
    ),
    ExtSensorEntityDescription(
        key="BASICVENT_ENERGY_SAVE_TOTAL_A4387",
        tag=EcotouchTag.BASICVENT_ENERGY_SAVE_TOTAL_A4387,
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        icon="mdi:home-lightning-bolt",
        entity_registry_enabled_default=False,
        suggested_display_precision=2,
        feature=FEATURE_VENT
    ),
    ExtSensorEntityDescription(
        key="BASICVENT_ENERGY_SAVE_CURRENT_A4389",
        tag=EcotouchTag.BASICVENT_ENERGY_SAVE_CURRENT_A4389,
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        icon="mdi:home-lightning-bolt",
        entity_registry_enabled_default=False,
        suggested_display_precision=2,
        feature=FEATURE_VENT
    ),
    ExtSensorEntityDescription(
        key="BASICVENT_ENERGY_RECOVERY_RATE_A4391",
        tag=EcotouchTag.BASICVENT_ENERGY_RECOVERY_RATE_A4391,
        device_class=None,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:gauge",
        entity_registry_enabled_default=False,
        suggested_display_precision=1,
        feature=FEATURE_VENT
    ),
]

SWITCH_SENSORS = [
    ExtSwitchEntityDescription(
        key="HOLIDAY_ENABLED",
        tag=EcotouchTag.HOLIDAY_ENABLED,
        icon="mdi:calendar-check",
        icon_off="mdi:calendar-blank",
        entity_registry_enabled_default=True
    ),
    ExtSwitchEntityDescription(
        key="SCHEDULE_WATER_DISINFECTION_1MO",
        tag=EcotouchTag.SCHEDULE_WATER_DISINFECTION_1MO,
        icon="mdi:calendar-today",
        entity_registry_enabled_default=False,
        feature=FEATURE_DISINFECTION
    ),
    ExtSwitchEntityDescription(
        key="SCHEDULE_WATER_DISINFECTION_2TU",
        tag=EcotouchTag.SCHEDULE_WATER_DISINFECTION_2TU,
        icon="mdi:calendar-today",
        entity_registry_enabled_default=False,
        feature=FEATURE_DISINFECTION
    ),
    ExtSwitchEntityDescription(
        key="SCHEDULE_WATER_DISINFECTION_3WE",
        tag=EcotouchTag.SCHEDULE_WATER_DISINFECTION_3WE,
        icon="mdi:calendar-today",
        entity_registry_enabled_default=False,
        feature=FEATURE_DISINFECTION
    ),
    ExtSwitchEntityDescription(
        key="SCHEDULE_WATER_DISINFECTION_4TH",
        tag=EcotouchTag.SCHEDULE_WATER_DISINFECTION_4TH,
        icon="mdi:calendar-today",
        entity_registry_enabled_default=False,
        feature=FEATURE_DISINFECTION
    ),
    ExtSwitchEntityDescription(
        key="SCHEDULE_WATER_DISINFECTION_5FR",
        tag=EcotouchTag.SCHEDULE_WATER_DISINFECTION_5FR,
        icon="mdi:calendar-today",
        entity_registry_enabled_default=False,
        feature=FEATURE_DISINFECTION
    ),
    ExtSwitchEntityDescription(
        key="SCHEDULE_WATER_DISINFECTION_6SA",
        tag=EcotouchTag.SCHEDULE_WATER_DISINFECTION_6SA,
        icon="mdi:calendar-today",
        entity_registry_enabled_default=False,
        feature=FEATURE_DISINFECTION
    ),
    ExtSwitchEntityDescription(
        key="SCHEDULE_WATER_DISINFECTION_7SU",
        tag=EcotouchTag.SCHEDULE_WATER_DISINFECTION_7SU,
        icon="mdi:calendar-today",
        entity_registry_enabled_default=False,
        feature=FEATURE_DISINFECTION
    ),
    ExtSwitchEntityDescription(
        key="PERMANENT_HEATING_CIRCULATION_PUMP_WINTER_D1103",
        tag=EcotouchTag.PERMANENT_HEATING_CIRCULATION_PUMP_WINTER_D1103,
        icon="mdi:pump",
        icon_off="mdi:pump-off",
        entity_registry_enabled_default=True
    ),
    ExtSwitchEntityDescription(
        key="PERMANENT_HEATING_CIRCULATION_PUMP_SUMMER_D1104",
        tag=EcotouchTag.PERMANENT_HEATING_CIRCULATION_PUMP_SUMMER_D1104,
        icon="mdi:pump",
        icon_off="mdi:pump-off",
        entity_registry_enabled_default=False
    ),
    ExtSwitchEntityDescription(
        key="BASICVENT_FILTER_CHANGE_OPERATING_HOURS_RESET_D1544",
        tag=EcotouchTag.BASICVENT_FILTER_CHANGE_OPERATING_HOURS_RESET_D1544,
        icon="mdi:restart",
        entity_registry_enabled_default=False,
        feature=FEATURE_VENT
    )
]
