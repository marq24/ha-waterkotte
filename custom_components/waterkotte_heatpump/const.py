"""Constants for Waterkotte Heatpump."""
# Base component constants
NAME = "Waterkotte Heatpump"
DOMAIN = "waterkotte_heatpump"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "0.0.1"

ATTRIBUTION = "Data provided by http://jsonplaceholder.typicode.com/"
ISSUE_URL = "https://github.com/pattisonmichael/waterkotte-heatpump/issues"

# Icons
ICON = "mdi:format-quote-close"

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
# Platforms
BINARY_SENSOR = "binary_sensor"
SENSOR = "sensor"
SWITCH = "switch"
PLATFORMS = [BINARY_SENSOR, SENSOR, SWITCH]
SENSORS = ["heating", "cooling", "water"]

# Configuration and options
CONF_ENABLED = "enabled"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_HOST = "host"
CONF_POLLING_INTERVAL = "polling_interval"

# Defaults
DEFAULT_NAME = DOMAIN


STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""
