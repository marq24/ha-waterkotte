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

from homeassistant.const import UnitOfTemperature, PERCENTAGE, UnitOfEnergy, UnitOfPower, UnitOfPressure, UnitOfTime

from custom_components.waterkotte_heatpump.pywaterkotte_ha.const import HEATING_MODES
from custom_components.waterkotte_heatpump.pywaterkotte_ha import EcotouchTag

# Base component constants
NAME: Final = "Waterkotte Heatpump [+2020]"
DOMAIN: Final = "waterkotte_heatpump"

TITLE: Final = "Waterkotte"
ISSUE_URL: Final = "https://github.com/marq24/ha-waterkotte/issues"

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
ENUM_HEATING_MODE: Final = list(HEATING_MODES.values())

# Configuration and options
CONF_ENABLED: Final = "enabled"
CONF_HOST: Final = "host"
CONF_POLLING_INTERVAL: Final = "polling_interval"
CONF_TAGS_PER_REQUEST: Final = "tags_per_request"
CONF_IP: Final = "ip"
CONF_BIOS: Final = "bios"
CONF_FW: Final = "fw"
CONF_SERIAL: Final = "serial"
CONF_SERIES: Final = "series"
CONF_ID: Final = "id"
CONF_SYSTEMTYPE: Final = "system_type"

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


@dataclass
class ExtBinarySensorEntityDescription(BinarySensorEntityDescription):
    tag: EcotouchTag | None = None


@dataclass
class ExtNumberEntityDescription(NumberEntityDescription):
    tag: EcotouchTag | None = None


@dataclass
class ExtSelectEntityDescription(SelectEntityDescription):
    tag: EcotouchTag | None = None
    # controls: list[str] | None = None


@dataclass
class ExtSensorEntityDescription(SensorEntityDescription):
    tag: EcotouchTag | None = None
    # selfimplemented_display_precision: int | None = None
    # controls: list[str] | None = None


@dataclass
class ExtSwitchEntityDescription(SwitchEntityDescription):
    tag: EcotouchTag | None = None
    icon_off: str | None = None


PLATFORMS: Final = ["binary_sensor", "number", "select", "sensor", "switch"]

BINARY_SENSORS = [
    ExtBinarySensorEntityDescription(
        key="STATE_SOURCEPUMP",
        name="Sourcepump",
        tag=EcotouchTag.STATE_SOURCEPUMP,
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:water-pump",
        entity_registry_enabled_default=True
    ),
    ExtBinarySensorEntityDescription(
        key="STATE_HEATINGPUMP",
        name="Heatingpump",
        tag=EcotouchTag.STATE_HEATINGPUMP,
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:heat-pump",
        entity_registry_enabled_default=True
    ),
    # EVD: -> Überhitzungsregler
    ExtBinarySensorEntityDescription(
        key="STATE_EVD",
        name="EVD",
        tag=EcotouchTag.STATE_EVD,
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:thermometer-high",
        entity_registry_enabled_default=True
    ),
    ExtBinarySensorEntityDescription(
        key="STATE_COMPRESSOR",
        name="Compressor",
        tag=EcotouchTag.STATE_COMPRESSOR,
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:gauge",
        entity_registry_enabled_default=True
    ),
    ExtBinarySensorEntityDescription(
        key="STATE_COMPRESSOR2",
        name="Compressor2",
        tag=EcotouchTag.STATE_COMPRESSOR2,
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:gauge",
        entity_registry_enabled_default=False
    ),
    ExtBinarySensorEntityDescription(
        key="STATE_EXTERNAL_HEATER",
        name="External Heater",
        tag=EcotouchTag.STATE_EXTERNAL_HEATER,
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:heating-coil",
        entity_registry_enabled_default=True
    ),
    ExtBinarySensorEntityDescription(
        key="STATE_ALARM",
        name="Alarm",
        tag=EcotouchTag.STATE_ALARM,
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:alert",
        entity_registry_enabled_default=False
    ),
    ExtBinarySensorEntityDescription(
        key="STATE_COOLING",
        name="Cooling",
        tag=EcotouchTag.STATE_COOLING,
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:snowflake-thermometer",
        entity_registry_enabled_default=False
    ),
    ExtBinarySensorEntityDescription(
        key="STATE_WATER",
        name="Water",
        tag=EcotouchTag.STATE_WATER,
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:water-thermometer",
        entity_registry_enabled_default=True
    ),
    ExtBinarySensorEntityDescription(
        key="STATE_POOL",
        name="Pool",
        tag=EcotouchTag.STATE_POOL,
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:pool",
        entity_registry_enabled_default=False
    ),
    ExtBinarySensorEntityDescription(
        key="STATE_SOLAR",
        name="Solar",
        tag=EcotouchTag.STATE_SOLAR,
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:solar-power-variant",
        entity_registry_enabled_default=False
    ),
    ExtBinarySensorEntityDescription(
        key="STATE_COOLING4WAY",
        name="Cooling4way",
        tag=EcotouchTag.STATE_COOLING4WAY,
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:snowflake-thermometer",
        entity_registry_enabled_default=False
    ),
    # status sensors (Operation Mode 0=off, 1=on or 2=disabled)
    ExtBinarySensorEntityDescription(
        key="STATUS_HEATING",
        name="Status Heating",
        tag=EcotouchTag.STATUS_HEATING,
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:radiator",
        entity_registry_enabled_default=True
    ),
    ExtBinarySensorEntityDescription(
        key="STATUS_WATER",
        name="Status Water",
        tag=EcotouchTag.STATUS_WATER,
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:water-thermometer",
        entity_registry_enabled_default=True
    ),
    ExtBinarySensorEntityDescription(
        key="STATUS_COOLING",
        name="Status Cooling",
        tag=EcotouchTag.STATUS_COOLING,
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:snowflake-thermometer",
        entity_registry_enabled_default=True
    ),
    ExtBinarySensorEntityDescription(
        key="STATUS_POOL",
        name="Status Pool",
        tag=EcotouchTag.STATUS_POOL,
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:pool-thermometer",
        entity_registry_enabled_default=False
    ),
    ExtBinarySensorEntityDescription(
        key="STATE_BLOCKING_TIME",
        name="Blockingtime",
        tag=EcotouchTag.STATE_BLOCKING_TIME,
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:electric-switch",
        entity_registry_enabled_default=False
    ),
    ExtBinarySensorEntityDescription(
        key="STATE_TEST_RUN",
        name="Testrun",
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
        name="Heating circulation pump",
        tag=EcotouchTag.STATE_HEATING_CIRCULATION_PUMP_D425,
        entity_registry_enabled_default=True
    ),
    ExtBinarySensorEntityDescription(
        key="STATE_BUFFERTANK_CIRCULATION_PUMP_D377",
        name="Buffertank circulation pump",
        tag=EcotouchTag.STATE_BUFFERTANK_CIRCULATION_PUMP_D377,
        entity_registry_enabled_default=True
    ),
    ExtBinarySensorEntityDescription(
        key="STATE_POOL_CIRCULATION_PUMP_D549",
        name="Pool circulation pump",
        tag=EcotouchTag.STATE_POOL_CIRCULATION_PUMP_D549,
        entity_registry_enabled_default=False
    ),
    ExtBinarySensorEntityDescription(
        key="STATE_MIX1_CIRCULATION_PUMP_D248",
        name="Mix1 circulation pump",
        tag=EcotouchTag.STATE_MIX1_CIRCULATION_PUMP_D248,
        entity_registry_enabled_default=True
    ),

    ExtBinarySensorEntityDescription(
        key="STATE_MIX2_CIRCULATION_PUMP_D291",
        name="Mix2 circulation pump",
        tag=EcotouchTag.STATE_MIX2_CIRCULATION_PUMP_D291,
        entity_registry_enabled_default=False
    ),

    ExtBinarySensorEntityDescription(
        key="STATE_MIX3_CIRCULATION_PUMP_D334",
        name="Mix3 circulation pump",
        tag=EcotouchTag.STATE_MIX3_CIRCULATION_PUMP_D334,
        entity_registry_enabled_default=False
    ),
    ExtBinarySensorEntityDescription(
        key="STATUS_SOLAR",
        name="Status Solar",
        tag=EcotouchTag.STATUS_SOLAR,
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:solar-power-variant",
        entity_registry_enabled_default=False
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
    #     #     icon="mdi:pump",
    #     entity_registry_enabled_default=True,
    #     #     #     "I1291"
    # ],
    # "STATUS_COMPRESSOR",
    #     "Status compressor",
    #     tag=EcotouchTag.STATUS_COMPRESSOR,
    #     device_class=BinarySensorDeviceClass.RUNNING,
    #     #     icon="mdi:gauge",
    #     entity_registry_enabled_default=True,
    #     #     #     "I1307"
    # ],

    # "MIX1_CIRCULATION_PUMP_D563",
    #    "Mix1 circulation pump",
    #    tag=EcotouchTag.MIX1_CIRCULATION_PUMP_D563,
    #    #    #    #    entity_registry_enabled_default=True,
    #    #    # ]
]
NUMBER_SENSORS = [
    # temperature sensors
    # not sure if this RETURN temperature should be set able at all?!
    ExtNumberEntityDescription(
        key="TEMPERATURE_RETURN_SETPOINT",
        name="Temperature Return Setpoint",
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
        name="Temperature Cooling Demand",
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
        name="Temperature Cooling Outdoor Limit",
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
        name="Temperature Heating Demand",
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
        name="Temperature heating Adjustment",
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
        name="Temperature heating Hysteresis",
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
        name="Temperature mixing circle 1 Adjustment",
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
        name="Temperature mixing circle 2 Adjustment",
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
        name="Temperature mixing circle 3 Adjustment",
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
        name="Temperature heating curve heating limit",
        tag=EcotouchTag.TEMPERATURE_HEATING_HC_LIMIT,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:radiator",
        entity_registry_enabled_default=False,
        native_min_value=5,
        native_max_value=35,
        native_step=TENTH_STEP,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    # A94
    ExtNumberEntityDescription(
        key="TEMPERATURE_HEATING_HC_TARGET",
        name="Temperature heating curve heating limit target",
        tag=EcotouchTag.TEMPERATURE_HEATING_HC_TARGET,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:radiator",
        entity_registry_enabled_default=False,
        native_min_value=15,
        native_max_value=65,
        native_step=TENTH_STEP,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    # A91
    ExtNumberEntityDescription(
        key="TEMPERATURE_HEATING_HC_OUTDOOR_NORM",
        name="Temperature heating curve norm outdoor",
        tag=EcotouchTag.TEMPERATURE_HEATING_HC_OUTDOOR_NORM,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:radiator",
        entity_registry_enabled_default=False,
        native_min_value=-99,
        native_max_value=99,
        native_step=TENTH_STEP,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    # A92
    ExtNumberEntityDescription(
        key="TEMPERATURE_HEATING_HC_NORM",
        name="Temperature heating curve norm heating circle",
        tag=EcotouchTag.TEMPERATURE_HEATING_HC_NORM,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:radiator",
        entity_registry_enabled_default=False,
        native_min_value=0,
        native_max_value=99,
        native_step=TENTH_STEP,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    # A95
    ExtNumberEntityDescription(
        key="TEMPERATURE_HEATING_SETPOINTLIMIT_MAX",
        name="Temperature heating curve Limit for setpoint (Max.)",
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
        name="Temperature heating curve Limit for setpoint (Min.)",
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
        name="Temperature Hot Water setpoint",
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
        name="Temperature Hot Water Hysteresis",
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
        name="Temperature mixing circle 1 heating limit",
        tag=EcotouchTag.TEMPERATURE_MIX1_HC_LIMIT,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:numeric-1-circle",
        entity_registry_enabled_default=False,
        native_min_value=5,
        native_max_value=35,
        native_step=TENTH_STEP,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    # A277
    ExtNumberEntityDescription(
        key="TEMPERATURE_MIX1_HC_TARGET",
        name="Temperature mixing circle 1 heating limit target",
        tag=EcotouchTag.TEMPERATURE_MIX1_HC_TARGET,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:numeric-1-circle",
        entity_registry_enabled_default=False,
        native_min_value=15,
        native_max_value=65,
        native_step=TENTH_STEP,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    # A274
    ExtNumberEntityDescription(
        key="TEMPERATURE_MIX1_HC_OUTDOOR_NORM",
        name="Temperature mixing circle 1 norm outdoor",
        tag=EcotouchTag.TEMPERATURE_MIX1_HC_OUTDOOR_NORM,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:numeric-1-circle",
        entity_registry_enabled_default=False,
        native_min_value=-99,
        native_max_value=99,
        native_step=TENTH_STEP,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    # A275
    ExtNumberEntityDescription(
        key="TEMPERATURE_MIX1_HC_HEATING_NORM",
        name="Temperature mixing circle 1 norm heating circle",
        tag=EcotouchTag.TEMPERATURE_MIX1_HC_HEATING_NORM,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:numeric-1-circle",
        entity_registry_enabled_default=False,
        native_min_value=0,
        native_max_value=99,
        native_step=TENTH_STEP,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    # A278
    ExtNumberEntityDescription(
        key="TEMPERATURE_MIX1_HC_MAX",
        name="Temperature mixing circle 1 Limit for setpoint (Max.)",
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
        name="Temperature mixing circle 2 heating limit",
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
        name="Temperature mixing circle 2 heating limit target",
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
        name="Temperature mixing circle 2 norm outdoor",
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
        name="Temperature mixing circle 2 norm heating circle",
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
        name="Temperature mixing circle 2 Limit for setpoint (Max.)",
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
        name="Temperature mixing circle 3 heating limit",
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
        name="Temperature mixing circle 3 heating limit target",
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
        name="Temperature mixing circle 3 norm outdoor",
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
        name="Temperature mixing circle 3 norm heating circle",
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
        name="Temperature mixing circle 3 Limit for setpoint (Max.)",
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
        name="Temperature Pool setpoint",
        tag=EcotouchTag.TEMPERATURE_POOL_SETPOINT,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:pool-thermometer",
        entity_registry_enabled_default=False,
        native_min_value=15,
        native_max_value=75,
        native_step=TENTH_STEP,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    ExtNumberEntityDescription(
        key="TEMPERATURE_POOL_HYSTERESIS",
        name="Temperature Pool Hysteresis",
        tag=EcotouchTag.TEMPERATURE_POOL_HYSTERESIS,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:pool-thermometer",
        entity_registry_enabled_default=False,
        native_min_value=0,
        native_max_value=10,
        native_step=TENTH_STEP,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.KELVIN,
    ),
    ExtNumberEntityDescription(
        key="TEMPERATURE_POOL_HC_LIMIT",
        name="Temperature Pool heating curve heating limit",
        tag=EcotouchTag.TEMPERATURE_POOL_HC_LIMIT,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:pool",
        entity_registry_enabled_default=False,
        native_min_value=5,
        native_max_value=35,
        native_step=TENTH_STEP,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    ExtNumberEntityDescription(
        key="TEMPERATURE_POOL_HC_TARGET",
        name="Temperature Pool heating curve heating limit target",
        tag=EcotouchTag.TEMPERATURE_POOL_HC_TARGET,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:pool",
        entity_registry_enabled_default=False,
        native_min_value=15,
        native_max_value=65,
        native_step=TENTH_STEP,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    ExtNumberEntityDescription(
        key="TEMPERATURE_POOL_HC_OUTDOOR_NORM",
        name="Temperature Pool heating curve norm outdoor",
        tag=EcotouchTag.TEMPERATURE_POOL_HC_OUTDOOR_NORM,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:pool",
        entity_registry_enabled_default=False,
        native_min_value=-99,
        native_max_value=99,
        native_step=TENTH_STEP,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    ExtNumberEntityDescription(
        key="TEMPERATURE_POOL_HC_NORM",
        name="Temperature Pool heating curve norm",
        tag=EcotouchTag.TEMPERATURE_POOL_HC_NORM,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:pool",
        entity_registry_enabled_default=False,
        native_min_value=0,
        native_max_value=99,
        native_step=TENTH_STEP,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    # Water disinfection start time & duration -> weekdays will be set in
    # switch.py
    ExtNumberEntityDescription(
        key="TEMPERATURE_WATER_DISINFECTION",
        name="Temperature Water disinfection",
        tag=EcotouchTag.TEMPERATURE_WATER_DISINFECTION,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:shield-bug",
        entity_registry_enabled_default=False,
        native_min_value=60,
        native_max_value=70,
        native_step=TENTH_STEP,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    ExtNumberEntityDescription(
        key="SCHEDULE_WATER_DISINFECTION_DURATION",
        name="Water disinfection duration (in hours)",
        tag=EcotouchTag.SCHEDULE_WATER_DISINFECTION_DURATION,
        device_class=None,  # duration in h
        icon="mdi:progress-clock",
        entity_registry_enabled_default=False,
        native_min_value=0,
        native_max_value=23,
        native_step=DEFAULT_STEP,
        mode=NumberMode.SLIDER,
        native_unit_of_measurement=UnitOfTime.HOURS,
    ),
    ExtNumberEntityDescription(
        key="SOURCE_PUMP_CAPTURE_TEMPERATURE_A479",
        name="Heat source pump - ΔT heat source",
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
        name="Enable Cooling",
        tag=EcotouchTag.ENABLE_COOLING,
        device_class=DEVICE_CLASS_ENUM,
        icon="mdi:snowflake-thermometer",
        entity_registry_enabled_default=True,
        options=ENUM_OFFAUTOMANUAL,
    ),
    ExtSelectEntityDescription(
        key="ENABLE_HEATING",
        name="Enable Heating",
        tag=EcotouchTag.ENABLE_HEATING,
        device_class=DEVICE_CLASS_ENUM,
        icon="mdi:radiator",
        entity_registry_enabled_default=True,
        options=ENUM_OFFAUTOMANUAL,
    ),
    ExtSelectEntityDescription(
        key="ENABLE_PV",
        name="Enable PV",
        tag=EcotouchTag.ENABLE_PV,
        device_class=DEVICE_CLASS_ENUM,
        icon="mdi:solar-power",
        entity_registry_enabled_default=False,
        options=ENUM_OFFAUTOMANUAL,
    ),
    ExtSelectEntityDescription(
        key="ENABLE_WARMWATER",
        name="Enable Warmwater",
        tag=EcotouchTag.ENABLE_WARMWATER,
        device_class=DEVICE_CLASS_ENUM,
        icon="mdi:water-thermometer",
        entity_registry_enabled_default=True,
        options=ENUM_OFFAUTOMANUAL,
    ),
    ExtSelectEntityDescription(
        key="ENABLE_POOL",
        name="Enable Pool",
        tag=EcotouchTag.ENABLE_POOL,
        device_class=DEVICE_CLASS_ENUM,
        icon="mdi:pool-thermometer",
        entity_registry_enabled_default=False,
        options=ENUM_OFFAUTOMANUAL,
    ),
    ExtSelectEntityDescription(
        key="ENABLE_EXTERNAL_HEATER",
        name="Enable external heater",
        tag=EcotouchTag.ENABLE_EXTERNAL_HEATER,
        device_class=DEVICE_CLASS_ENUM,
        icon="mdi:heating-coil",
        entity_registry_enabled_default=True,
        options=ENUM_OFFAUTOMANUAL,
    ),
    # I265
    ExtSelectEntityDescription(
        key="TEMPERATURE_HEATING_MODE",
        name="Heating Control",
        tag=EcotouchTag.TEMPERATURE_HEATING_MODE,
        device_class=DEVICE_CLASS_ENUM,
        icon="mdi:radiator",
        entity_registry_enabled_default=True,
        options=ENUM_HEATING_MODE,
    )
]
SENSOR_SENSORS = [
    # temperature sensors
    ExtSensorEntityDescription(
        key="TEMPERATURE_OUTSIDE",
        name="Temperature Outside",
        tag=EcotouchTag.TEMPERATURE_OUTSIDE,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:sun-snowflake-variant",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_OUTSIDE_1H",
        name="Temperature Outside 1h",
        tag=EcotouchTag.TEMPERATURE_OUTSIDE_1H,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:sun-snowflake-variant",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_OUTSIDE_24H",
        name="Temperature Outside 24h",
        tag=EcotouchTag.TEMPERATURE_OUTSIDE_24H,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:sun-snowflake-variant",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_SOURCE_ENTRY",
        name="Temperature Source Entry",
        tag=EcotouchTag.TEMPERATURE_SOURCE_ENTRY,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_SOURCE_EXIT",
        name="Temperature Source Exit",
        tag=EcotouchTag.TEMPERATURE_SOURCE_EXIT,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_EVAPORATION",
        name="Temperature Evaporation",
        tag=EcotouchTag.TEMPERATURE_EVAPORATION,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_SUCTION_LINE",
        name="Temperature Suction Line",
        tag=EcotouchTag.TEMPERATURE_SUCTION_LINE,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_RETURN",
        name="Temperature Return",
        tag=EcotouchTag.TEMPERATURE_RETURN,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_FLOW",
        name="Temperature Flow",
        tag=EcotouchTag.TEMPERATURE_FLOW,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_CONDENSATION",
        name="Temperature Condensation",
        tag=EcotouchTag.TEMPERATURE_CONDENSATION,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_BUFFERTANK",
        name="Temperature Buffer Tank",
        tag=EcotouchTag.TEMPERATURE_BUFFERTANK,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:storage-tank",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_ROOM",
        name="Temperature Room",
        tag=EcotouchTag.TEMPERATURE_ROOM,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermostat-box",
        entity_registry_enabled_default=False
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_ROOM_1H",
        name="Temperature Room 1h",
        tag=EcotouchTag.TEMPERATURE_ROOM_1H,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermostat-box",
        entity_registry_enabled_default=False
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_HEATING",
        name="Temperature Heating",
        tag=EcotouchTag.TEMPERATURE_HEATING,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:radiator",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_HEATING_DEMAND",
        name="Demanded Temperature Heating",
        tag=EcotouchTag.TEMPERATURE_HEATING_DEMAND,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:radiator",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_COOLING",
        name="Temperature Cooling",
        tag=EcotouchTag.TEMPERATURE_COOLING,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:snowflake-thermometer",
        entity_registry_enabled_default=False
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_COOLING_DEMAND",
        name="Demanded Temperature Cooling",
        tag=EcotouchTag.TEMPERATURE_COOLING_DEMAND,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:snowflake-thermometer",
        entity_registry_enabled_default=False
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_WATER",
        name="Temperature Hot Water",
        tag=EcotouchTag.TEMPERATURE_WATER,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:water-thermometer",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_WATER_DEMAND",
        name="Demanded Temperature Hot Water",
        tag=EcotouchTag.TEMPERATURE_WATER_DEMAND,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:water-thermometer",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_MIX1",
        name="Temperature mixing circle 1",
        tag=EcotouchTag.TEMPERATURE_MIX1,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:numeric-1-circle",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_MIX1_PERCENT",
        name="Temperature mixing circle 1 percent",
        tag=EcotouchTag.TEMPERATURE_MIX1_PERCENT,
        device_class=None,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:gauge",
        entity_registry_enabled_default=False
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_MIX1_DEMAND",
        name="Demanded Temperature mixing circle 1",
        tag=EcotouchTag.TEMPERATURE_MIX1_DEMAND,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:numeric-1-circle",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_MIX2",
        name="Temperature mixing circle 2",
        tag=EcotouchTag.TEMPERATURE_MIX2,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:numeric-2-circle",
        entity_registry_enabled_default=False
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_MIX2_PERCENT",
        name="Temperature mixing circle 2 percent",
        tag=EcotouchTag.TEMPERATURE_MIX2_PERCENT,
        device_class=None,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:gauge",
        entity_registry_enabled_default=False
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_MIX2_DEMAND",
        name="Demanded Temperature mixing circle 2",
        tag=EcotouchTag.TEMPERATURE_MIX2_DEMAND,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:numeric-2-circle",
        entity_registry_enabled_default=False
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_MIX3",
        name="Temperature mixing circle 3",
        tag=EcotouchTag.TEMPERATURE_MIX3,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:numeric-3-circle",
        entity_registry_enabled_default=False
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_MIX3_PERCENT",
        name="Temperature mixing circle 3 percent",
        tag=EcotouchTag.TEMPERATURE_MIX3_PERCENT,
        device_class=None,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:gauge",
        entity_registry_enabled_default=False
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_MIX3_DEMAND",
        name="Demanded Temperature mixing circle 3",
        tag=EcotouchTag.TEMPERATURE_MIX3_DEMAND,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:numeric-3-circle",
        entity_registry_enabled_default=False
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_POOL",
        name="Temperature Pool",
        tag=EcotouchTag.TEMPERATURE_POOL,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:pool-thermometer",
        entity_registry_enabled_default=False
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_POOL_DEMAND",
        name="Demanded Temperature Pool",
        tag=EcotouchTag.TEMPERATURE_POOL_DEMAND,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:pool-thermometer",
        entity_registry_enabled_default=False
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_SOLAR",
        name="Temperature Solar",
        tag=EcotouchTag.TEMPERATURE_SOLAR,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:solar-power-variant",
        entity_registry_enabled_default=False
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_SOLAR_EXIT",
        name="Temperature Solar Collector Exit",
        tag=EcotouchTag.TEMPERATURE_SOLAR_EXIT,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:solar-power-variant",
        entity_registry_enabled_default=False
    ),
    ExtSensorEntityDescription(
        key="TEMPERATURE_DISCHARGE",
        name="Temperature Discharge",
        tag=EcotouchTag.TEMPERATURE_DISCHARGE,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer",
        entity_registry_enabled_default=False
    ),
    # other (none temperature) values...
    ExtSensorEntityDescription(
        key="PRESSURE_EVAPORATION",
        name="Pressure Evaporation",
        tag=EcotouchTag.PRESSURE_EVAPORATION,
        device_class=SensorDeviceClass.PRESSURE,
        native_unit_of_measurement=UnitOfPressure.BAR,
        icon="mdi:gauge",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="PRESSURE_CONDENSATION",
        name="Pressure Condensation",
        tag=EcotouchTag.PRESSURE_CONDENSATION,
        device_class=SensorDeviceClass.PRESSURE,
        native_unit_of_measurement=UnitOfPressure.BAR,
        icon="mdi:gauge",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="PRESSURE_WATER",
        name="Pressure Water",
        tag=EcotouchTag.PRESSURE_WATER,
        device_class=SensorDeviceClass.PRESSURE,
        native_unit_of_measurement=UnitOfPressure.BAR,
        icon="mdi:gauge",
        entity_registry_enabled_default=False
    ),
    # other data...
    ExtSensorEntityDescription(
        key="POSITION_EXPANSION_VALVE",
        name="Position Expansion Valve",
        tag=EcotouchTag.POSITION_EXPANSION_VALVE,
        device_class=None,
        native_unit_of_measurement=None,
        icon="mdi:gauge",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="SUCTION_GAS_OVERHEATING",
        name="Suction Gas Overheating",
        tag=EcotouchTag.SUCTION_GAS_OVERHEATING,
        device_class=None,
        native_unit_of_measurement=None,
        icon="mdi:gauge",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="POWER_ELECTRIC",
        name="Power Electrical",
        tag=EcotouchTag.POWER_ELECTRIC,
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        icon="mdi:meter-electric",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="POWER_HEATING",
        name="Power Thermal",
        tag=EcotouchTag.POWER_HEATING,
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        icon="mdi:radiator",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="POWER_COOLING",
        name="Power Cooling",
        tag=EcotouchTag.POWER_COOLING,
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        icon="mdi:snowflake-thermometer",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="COP_HEATING",
        name="COP Heating",
        tag=EcotouchTag.COP_HEATING,
        device_class=None,
        native_unit_of_measurement=None,
        icon="mdi:gauge",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="COP_COOLING",
        name="COP Cooling",
        tag=EcotouchTag.COP_COOLING,
        device_class=None,
        native_unit_of_measurement=None,
        icon="mdi:gauge",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="ENERGY_CONSUMPTION_TOTAL_YEAR",
        name="ENERGY_CONSUMPTION_TOTAL_YEAR",
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
        name="COMPRESSOR_ELECTRIC_CONSUMPTION_YEAR",
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
        name="SOURCEPUMP_ELECTRIC_CONSUMPTION_YEAR",
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
        name="ELECTRICAL_HEATER_ELECTRIC_CONSUMPTION_YEAR",
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
        name="ENERGY_PRODUCTION_TOTAL_YEAR",
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
        name="HEATING_ENERGY_PRODUCTION_YEAR",
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
        name="HOT_WATER_ENERGY_PRODUCTION_YEAR",
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
        name="POOL_ENERGY_PRODUCTION_YEAR",
        tag=EcotouchTag.POOL_ENERGY_PRODUCTION_YEAR,
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        icon="mdi:pool-thermometer",
        entity_registry_enabled_default=False,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=3
    ),
    ExtSensorEntityDescription(
        key="COOLING_ENERGY_YEAR",
        name="COOLING_ENERGY_YEAR",
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
        name="Percent Heat Circ Pump",
        tag=EcotouchTag.PERCENT_HEAT_CIRC_PUMP,
        device_class=SensorDeviceClass.POWER_FACTOR,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:gauge",
        entity_registry_enabled_default=False
    ),
    ExtSensorEntityDescription(
        key="PERCENT_SOURCE_PUMP",
        name="Percent Source Pump",
        tag=EcotouchTag.PERCENT_SOURCE_PUMP,
        device_class=SensorDeviceClass.POWER_FACTOR,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:gauge",
        entity_registry_enabled_default=False
    ),
    ExtSensorEntityDescription(
        key="PERCENT_COMPRESSOR",
        name="Percent Compressor",
        tag=EcotouchTag.PERCENT_COMPRESSOR,
        device_class=SensorDeviceClass.POWER_FACTOR,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:gauge",
        entity_registry_enabled_default=False
    ),
    # writeable sensors from here...
    ExtSensorEntityDescription(
        key="HOLIDAY_START_TIME",
        name="Holiday start",
        tag=EcotouchTag.HOLIDAY_START_TIME,
        device_class=SensorDeviceClass.DATE,
        native_unit_of_measurement=None,
        icon="mdi:calendar-arrow-right",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="HOLIDAY_END_TIME",
        name="Holiday end",
        tag=EcotouchTag.HOLIDAY_END_TIME,
        device_class=SensorDeviceClass.DATE,
        native_unit_of_measurement=None,
        icon="mdi:calendar-arrow-left",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="SCHEDULE_WATER_DISINFECTION_START_TIME",
        name="Water disinfection start time",
        tag=EcotouchTag.SCHEDULE_WATER_DISINFECTION_START_TIME,
        device_class=SensorDeviceClass.DATE,
        native_unit_of_measurement=None,
        icon="mdi:clock-digital",
        entity_registry_enabled_default=False
    ),
    ExtSensorEntityDescription(
        key="STATE_SERVICE",
        name="State Service",
        tag=EcotouchTag.STATE_SERVICE,
        device_class=None,
        native_unit_of_measurement=None,
        icon="mdi:wrench-clock",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="ALARM_BITS",
        name="Alarms",
        tag=EcotouchTag.ALARM_BITS,
        device_class=None,
        native_unit_of_measurement=None,
        icon="mdi:alarm-light",
        entity_registry_enabled_default=True
    ),
    ExtSensorEntityDescription(
        key="INTERRUPTION_BITS",
        name="Interruptions",
        tag=EcotouchTag.INTERRUPTION_BITS,
        device_class=None,
        native_unit_of_measurement=None,
        icon="mdi:alert-circle",
        entity_registry_enabled_default=True
    )
]
SWITCH_SENSORS = [
    ExtSwitchEntityDescription(
        key="HOLIDAY_ENABLED",
        name="Holiday Mode",
        tag=EcotouchTag.HOLIDAY_ENABLED,
        icon="mdi:calendar-check",
        icon_off="mdi:calendar-blank",
        entity_registry_enabled_default=True
    ),
    ExtSwitchEntityDescription(
        key="SCHEDULE_WATER_DISINFECTION_1MO",
        name="SCHEDULE_WATER_DISINFECTION_1MO",
        tag=EcotouchTag.SCHEDULE_WATER_DISINFECTION_1MO,
        icon="mdi:calendar-today",
        entity_registry_enabled_default=False
    ),
    ExtSwitchEntityDescription(
        key="SCHEDULE_WATER_DISINFECTION_2TU",
        name="SCHEDULE_WATER_DISINFECTION_2TU",
        tag=EcotouchTag.SCHEDULE_WATER_DISINFECTION_2TU,
        icon="mdi:calendar-today",
        entity_registry_enabled_default=False
    ),
    ExtSwitchEntityDescription(
        key="SCHEDULE_WATER_DISINFECTION_3WE",
        name="SCHEDULE_WATER_DISINFECTION_3WE",
        tag=EcotouchTag.SCHEDULE_WATER_DISINFECTION_3WE,
        icon="mdi:calendar-today",
        entity_registry_enabled_default=False
    ),
    ExtSwitchEntityDescription(
        key="SCHEDULE_WATER_DISINFECTION_4TH",
        name="SCHEDULE_WATER_DISINFECTION_4TH",
        tag=EcotouchTag.SCHEDULE_WATER_DISINFECTION_4TH,
        icon="mdi:calendar-today",
        entity_registry_enabled_default=False
    ),
    ExtSwitchEntityDescription(
        key="SCHEDULE_WATER_DISINFECTION_5FR",
        name="SCHEDULE_WATER_DISINFECTION_5FR",
        tag=EcotouchTag.SCHEDULE_WATER_DISINFECTION_5FR,
        icon="mdi:calendar-today",
        entity_registry_enabled_default=False
    ),
    ExtSwitchEntityDescription(
        key="SCHEDULE_WATER_DISINFECTION_6SA",
        name="SCHEDULE_WATER_DISINFECTION_6SA",
        tag=EcotouchTag.SCHEDULE_WATER_DISINFECTION_6SA,
        icon="mdi:calendar-today",
        entity_registry_enabled_default=False
    ),
    ExtSwitchEntityDescription(
        key="SCHEDULE_WATER_DISINFECTION_7SU",
        name="SCHEDULE_WATER_DISINFECTION_7SU",
        tag=EcotouchTag.SCHEDULE_WATER_DISINFECTION_7SU,
        icon="mdi:calendar-today",
        entity_registry_enabled_default=False
    ),
    ExtSwitchEntityDescription(
        key="PERMANENT_HEATING_CIRCULATION_PUMP_WINTER_D1103",
        name="PERMANENT_HEATING_CIRCULATION_PUMP_WINTER_D1103",
        tag=EcotouchTag.PERMANENT_HEATING_CIRCULATION_PUMP_WINTER_D1103,
        icon="mdi:pump",
        icon_off="mdi:pump-off",
        entity_registry_enabled_default=True
    ),
    ExtSwitchEntityDescription(
        key="PERMANENT_HEATING_CIRCULATION_PUMP_SUMMER_D1104",
        name="PERMANENT_HEATING_CIRCULATION_PUMP_SUMMER_D1104",
        tag=EcotouchTag.PERMANENT_HEATING_CIRCULATION_PUMP_SUMMER_D1104,
        icon="mdi:pump",
        icon_off="mdi:pump-off",
        entity_registry_enabled_default=False
    )
]
