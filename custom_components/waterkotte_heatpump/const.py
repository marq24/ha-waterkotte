"""Constants for Waterkotte Heatpump."""
from typing import Final

from custom_components.waterkotte_heatpump.pywaterkotte_ha.const import HEATING_MODES

# Base component constants
NAME: Final = "Waterkotte Heatpump [+2020]"
DOMAIN: Final = "waterkotte_heatpump"
PLATFORMS: Final = ["binary_sensor", "number", "select", "sensor", "switch"]

DOMAIN_DATA: Final = f"{DOMAIN}_data"
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
CONF_USERNAME: Final = "username"
CONF_PASSWORD: Final = "password"
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

DEFAULT_NAME: Final = DOMAIN

STARTUP_MESSAGE: Final = f"""
-------------------------------------------------------------------
{NAME}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""
