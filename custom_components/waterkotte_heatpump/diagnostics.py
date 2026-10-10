"""Diagnostics of the Waterkotte Heatpump integration (Settings -> Devices & services -> Download diagnostics)."""
from datetime import date, time
from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant

from .const import CONF_SERIAL, DOMAIN

# the credentials and the identification of the heat pump are not part of the diagnostics
TO_REDACT = {CONF_HOST, CONF_PASSWORD, CONF_USERNAME, CONF_SERIAL, "unique_id", "title"}


def _json_value(value: Any) -> Any:
    """The value of a tag as JSON value"""
    if isinstance(value, (date, time)):
        return value.isoformat()
    return value


async def async_get_config_entry_diagnostics(hass: HomeAssistant, config_entry: ConfigEntry) -> dict[str, Any]:
    """Return the diagnostics of a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    return {
        "entry": async_redact_data(config_entry.as_dict(), TO_REDACT),
        "available_features": coordinator.available_features,
        "update_interval": coordinator.update_interval.total_seconds() if coordinator.update_interval else None,
        "last_update_success": coordinator.last_update_success,
        "requested_tags": sorted(tag.name for tag in coordinator.bridge.tags or []),
        # the values of the last update (only the tags of the enabled entities are requested)
        "data": {
            tag.name: {"value": _json_value(value.get("value")), "status": value.get("status")}
            for tag, value in sorted((coordinator.data or {}).items(), key=lambda item: item[0].name)
        },
    }