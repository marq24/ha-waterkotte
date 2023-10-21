"""Constants for Waterkotte Heatpump."""
from custom_components.waterkotte_heatpump.pywaterkotte_ha.ecotouch import HEATING_MODES
# Base component constants
NAME = "Waterkotte Heatpump [+2020]"
DOMAIN = "waterkotte_heatpump"
DOMAIN_DATA = f"{DOMAIN}_data"
TITLE = "Waterkotte"
ISSUE_URL = "https://github.com/marq24/ha-waterkotte/issues"

# Device classes
BINARY_SENSOR_DEVICE_CLASS = "connectivity"
DEVICE_CLASS_ENUM = "enum"

# States
STATE_AUTO = "auto"
STATE_MANUAL = "manual"
STATE_ON = "on"
STATE_OFF = "off"
# # #### Enum Options ####
ENUM_ONOFFAUTO = [STATE_ON, STATE_OFF, STATE_AUTO]
ENUM_OFFAUTOMANUAL = [STATE_OFF, STATE_AUTO, STATE_MANUAL]
ENUM_HEATING_MODE = list(HEATING_MODES.values())


# Platforms
BINARY_SENSOR = "binary_sensor"
SENSOR = "sensor"
SWITCH = "switch"
SELECT = "select"
NUMBER = "number"
# TEXT = "text"
#PLATFORMS = [SENSOR]
PLATFORMS = [BINARY_SENSOR, SELECT, SENSOR, SWITCH, NUMBER]  #
SENSORS = ["heating", "cooling", "water"]


# Configuration and options
CONF_ENABLED = "enabled"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_HOST = "host"
CONF_POLLING_INTERVAL = "polling_interval"
CONF_TAGS_PER_REQUEST = "tags_per_request"
CONF_IP = "ip"
CONF_BIOS = "bios"
CONF_FW = "fw"
CONF_SERIAL = "serial"
CONF_SERIES = "series"
CONF_ID = "id"
CONF_SYSTEMTYPE = "system_type"
# Defaults
DEFAULT_NAME = DOMAIN


STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""
