import datetime
import logging
from typing import Tuple

from homeassistant.core import ServiceCall, ServiceResponse

from custom_components.waterkotte_heatpump.pywaterkotte_ha.tags import WKHPTag

_LOGGER: logging.Logger = logging.getLogger(__package__)


class WaterkotteHeatpumpService():
    """waterkotte_heatpump switch class."""

    def __init__(self, hass, config, coordinator):  # pylint: disable=unused-argument
        """Initialize the sensor."""
        self._hass = hass
        self._config = config
        self._coordinator = coordinator

    async def set_holiday(self, call: ServiceCall):
        """Handle the service call."""
        start = call.data.get('start', None)
        end = call.data.get('end', None)
        if start is not None and end is not None:
            start = datetime.datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
            end = datetime.datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
            _LOGGER.debug(f"set_holiday start: {start} end: {end}")
            try:
                await self._coordinator.async_write_tag(WKHPTag.HOLIDAY_START_TIME, start)
                await self._coordinator.async_write_tag(WKHPTag.HOLIDAY_END_TIME, end)
                await self._coordinator.async_refresh()
            except ValueError:
                return "unavailable"

            if call.return_response:
                return {"result": "ok"}

        if call.return_response:
            return {"result": "error"}

    async def set_disinfection_start_time(self, call: ServiceCall):
        start_time = self._get_time("starthhmm", call)
        if start_time is not None:
            _LOGGER.debug(f"set_disinfection_start_time: {start_time}")
            try:
                await self._coordinator.async_write_tag(WKHPTag.SCHEDULE_WATER_DISINFECTION_START_TIME, start_time)
                await self._coordinator.async_refresh()
            except ValueError:
                return "unavailable"
            return True
        return False

    async def set_schedule_data(self, call: ServiceCall):
        type = call.data.get("schedule_type", None)
        days = call.data.get("schedule_days", None)
        enable = call.data.get("enable", None)
        start_time = self._get_time("start_time", call)
        end_time = self._get_time("end_time", call)

        adj1_enable = call.data.get("adj1_enable", None)
        adj1_value = call.data.get("adj1_value", None)
        adj1_start_time = self._get_time("adj1_start_time", call)
        adj1_end_time = self._get_time("adj1_end_time", call)

        adj2_enable = call.data.get("adj2_enable", None)
        adj2_value = call.data.get("adj2_value", None)
        adj2_start_time = self._get_time("adj2_start_time", call)
        adj2_end_time = self._get_time("adj2_end_time", call)

        if type is not None and days is not None and len(days) > 0:
            try:
                kv_pairs = []
                final_type = f"SCHEDULE_{type.upper()}"
                for a_day in days:
                    if enable is not None:
                        kv_pairs.append((WKHPTag[f"{final_type}_{a_day.upper()}_ENABLE"], enable))
                    if start_time is not None:
                        kv_pairs.append((WKHPTag[f"{final_type}_{a_day.upper()}_START_TIME"], start_time))
                    if end_time is not None:
                        kv_pairs.append((WKHPTag[f"{final_type}_{a_day.upper()}_END_TIME"], end_time))

                    if adj1_enable is not None:
                        kv_pairs.append((WKHPTag[f"{final_type}_{a_day.upper()}_ADJUST1_ENABLE"], adj1_enable))
                    if adj1_value is not None:
                        kv_pairs.append((WKHPTag[f"{final_type}_{a_day.upper()}_ADJUST1_VALUE"], float(adj1_value)))
                    if adj1_start_time is not None:
                        kv_pairs.append((WKHPTag[f"{final_type}_{a_day.upper()}_ADJUST1_START_TIME"], adj1_start_time))
                    if adj1_end_time is not None:
                        kv_pairs.append((WKHPTag[f"{final_type}_{a_day.upper()}_ADJUST1_END_TIME"], adj1_end_time))

                    if adj2_enable is not None:
                        kv_pairs.append((WKHPTag[f"{final_type}_{a_day.upper()}_ADJUST1_ENABLE"], adj2_enable))
                    if adj2_value is not None:
                        kv_pairs.append((WKHPTag[f"{final_type}_{a_day.upper()}_ADJUST2_VALUE"], float(adj2_value)))
                    if adj2_start_time is not None:
                        kv_pairs.append((WKHPTag[f"{final_type}_{a_day.upper()}_ADJUST2_START_TIME"], adj1_start_time))
                    if adj2_end_time is not None:
                        kv_pairs.append((WKHPTag[f"{final_type}_{a_day.upper()}_ADJUST2_END_TIME"], adj1_end_time))

                _LOGGER.debug(f"set_schedule_data for: '{type}' @{days} -> {kv_pairs}")
                await self._coordinator.async_write_tags(kv_pairs)
                await self._coordinator.async_refresh()
            except ValueError as exe:
                return {"error": str(exe)}
            return {"success": "yes"}
        else:
            return {"error": "no type or day provided"}

    def _get_time(self, key: str, call: ServiceCall):
        a_time = call.data.get(key, None)
        if a_time is not None:
            temp = str(a_time)
            if temp.startswith("24:"):
                temp = "00" + temp[2:]
            return datetime.time.fromisoformat(temp)
        return None

    async def get_energy_balance(self, call: ServiceCall) -> ServiceResponse:
        try:
            tags = [WKHPTag.COMPRESSOR_ELECTRIC_CONSUMPTION_YEAR,
                    WKHPTag.SOURCEPUMP_ELECTRIC_CONSUMPTION_YEAR,
                    WKHPTag.ELECTRICAL_HEATER_ELECTRIC_CONSUMPTION_YEAR,
                    WKHPTag.HEATING_ENERGY_PRODUCTION_YEAR,
                    WKHPTag.HOT_WATER_ENERGY_PRODUCTION_YEAR,
                    WKHPTag.POOL_ENERGY_PRODUCTION_YEAR,
                    WKHPTag.COP_HEATPUMP_YEAR,
                    WKHPTag.COP_HEATPUMP_ACTUAL_YEAR_INFO]
            res = await self._coordinator.async_read_values(tags)

        except ValueError:
            return "unavailable"
        ret = {
            "year": res.get(WKHPTag.COP_HEATPUMP_ACTUAL_YEAR_INFO, {"value": "unknown"})["value"],
            "cop": res.get(WKHPTag.COP_HEATPUMP_YEAR, {"value": "unknown"})["value"],
            "compressor": res.get(WKHPTag.COMPRESSOR_ELECTRIC_CONSUMPTION_YEAR, {"value": "unknown"})["value"],
            "sourcepump": res.get(WKHPTag.SOURCEPUMP_ELECTRIC_CONSUMPTION_YEAR, {"value": "unknown"})["value"],
            "externalheater": res.get(WKHPTag.ELECTRICAL_HEATER_ELECTRIC_CONSUMPTION_YEAR, {"value": "unknown"})[
                "value"],
            "heating": res.get(WKHPTag.HEATING_ENERGY_PRODUCTION_YEAR, {"value": "unknown"})["value"],
            "warmwater": res.get(WKHPTag.HOT_WATER_ENERGY_PRODUCTION_YEAR, {"value": "unknown"})["value"],
            "pool": res.get(WKHPTag.POOL_ENERGY_PRODUCTION_YEAR, {"value": "unknown"})["value"]}
        return ret

    async def get_energy_balance_monthly(self, call: ServiceCall) -> ServiceResponse:
        try:
            for x in range(2):
                tags = [WKHPTag.ENG_CONSUMPTION_COMPRESSOR01,
                        WKHPTag.ENG_CONSUMPTION_COMPRESSOR02,
                        WKHPTag.ENG_CONSUMPTION_COMPRESSOR03,
                        WKHPTag.ENG_CONSUMPTION_COMPRESSOR04,
                        WKHPTag.ENG_CONSUMPTION_COMPRESSOR05,
                        WKHPTag.ENG_CONSUMPTION_COMPRESSOR06,
                        WKHPTag.ENG_CONSUMPTION_COMPRESSOR07,
                        WKHPTag.ENG_CONSUMPTION_COMPRESSOR08,
                        WKHPTag.ENG_CONSUMPTION_COMPRESSOR09,
                        WKHPTag.ENG_CONSUMPTION_COMPRESSOR10,
                        WKHPTag.ENG_CONSUMPTION_COMPRESSOR11,
                        WKHPTag.ENG_CONSUMPTION_COMPRESSOR12]
                resCompressor = await self._coordinator.async_read_values(tags)
                found = False
                for value in resCompressor:
                    if resCompressor.get(value, {"value": "unknown"})["value"] == "unknown":
                        found = True
                if len(resCompressor) == 12 and not found:
                    break
            for x in range(2):
                tags = [WKHPTag.ENG_CONSUMPTION_SOURCEPUMP01,
                        WKHPTag.ENG_CONSUMPTION_SOURCEPUMP02,
                        WKHPTag.ENG_CONSUMPTION_SOURCEPUMP03,
                        WKHPTag.ENG_CONSUMPTION_SOURCEPUMP04,
                        WKHPTag.ENG_CONSUMPTION_SOURCEPUMP05,
                        WKHPTag.ENG_CONSUMPTION_SOURCEPUMP06,
                        WKHPTag.ENG_CONSUMPTION_SOURCEPUMP07,
                        WKHPTag.ENG_CONSUMPTION_SOURCEPUMP08,
                        WKHPTag.ENG_CONSUMPTION_SOURCEPUMP09,
                        WKHPTag.ENG_CONSUMPTION_SOURCEPUMP10,
                        WKHPTag.ENG_CONSUMPTION_SOURCEPUMP11,
                        WKHPTag.ENG_CONSUMPTION_SOURCEPUMP12]
                resSourcePump = await self._coordinator.async_read_values(tags)
                found = False
                for value in resSourcePump:
                    if resSourcePump.get(value, {"value": "unknown"})["value"] == "unknown":
                        found = True
                if len(resSourcePump) == 12 and not found:
                    break
            for x in range(2):
                tags = [WKHPTag.ENG_CONSUMPTION_EXTERNALHEATER01,
                        WKHPTag.ENG_CONSUMPTION_EXTERNALHEATER02,
                        WKHPTag.ENG_CONSUMPTION_EXTERNALHEATER03,
                        WKHPTag.ENG_CONSUMPTION_EXTERNALHEATER04,
                        WKHPTag.ENG_CONSUMPTION_EXTERNALHEATER05,
                        WKHPTag.ENG_CONSUMPTION_EXTERNALHEATER06,
                        WKHPTag.ENG_CONSUMPTION_EXTERNALHEATER07,
                        WKHPTag.ENG_CONSUMPTION_EXTERNALHEATER08,
                        WKHPTag.ENG_CONSUMPTION_EXTERNALHEATER09,
                        WKHPTag.ENG_CONSUMPTION_EXTERNALHEATER10,
                        WKHPTag.ENG_CONSUMPTION_EXTERNALHEATER11,
                        WKHPTag.ENG_CONSUMPTION_EXTERNALHEATER12]
                resExternalHeater = await self._coordinator.async_read_values(tags)
                found = False
                for value in resExternalHeater:
                    if resExternalHeater.get(value, {"value": "unknown"})["value"] == "unknown":
                        found = True
                if len(resExternalHeater) == 12 and not found:
                    break
            for x in range(2):
                tags = [WKHPTag.ENG_PRODUCTION_HEATING01,
                        WKHPTag.ENG_PRODUCTION_HEATING02,
                        WKHPTag.ENG_PRODUCTION_HEATING03,
                        WKHPTag.ENG_PRODUCTION_HEATING04,
                        WKHPTag.ENG_PRODUCTION_HEATING05,
                        WKHPTag.ENG_PRODUCTION_HEATING06,
                        WKHPTag.ENG_PRODUCTION_HEATING07,
                        WKHPTag.ENG_PRODUCTION_HEATING08,
                        WKHPTag.ENG_PRODUCTION_HEATING09,
                        WKHPTag.ENG_PRODUCTION_HEATING10,
                        WKHPTag.ENG_PRODUCTION_HEATING11,
                        WKHPTag.ENG_PRODUCTION_HEATING12]
                resHeater = await self._coordinator.async_read_values(tags)
                found = False
                for value in resHeater:
                    if resHeater.get(value, {"value": "unknown"})["value"] == "unknown":
                        found = True
                if len(resHeater) == 12 and not found:
                    break
            for x in range(2):
                tags = [WKHPTag.ENG_PRODUCTION_WARMWATER01,
                        WKHPTag.ENG_PRODUCTION_WARMWATER02,
                        WKHPTag.ENG_PRODUCTION_WARMWATER03,
                        WKHPTag.ENG_PRODUCTION_WARMWATER04,
                        WKHPTag.ENG_PRODUCTION_WARMWATER05,
                        WKHPTag.ENG_PRODUCTION_WARMWATER06,
                        WKHPTag.ENG_PRODUCTION_WARMWATER07,
                        WKHPTag.ENG_PRODUCTION_WARMWATER08,
                        WKHPTag.ENG_PRODUCTION_WARMWATER09,
                        WKHPTag.ENG_PRODUCTION_WARMWATER10,
                        WKHPTag.ENG_PRODUCTION_WARMWATER11,
                        WKHPTag.ENG_PRODUCTION_WARMWATER12]
                resWarmWater = await self._coordinator.async_read_values(tags)
                found = False
                for value in resWarmWater:
                    if resWarmWater.get(value, {"value": "unknown"})["value"] == "unknown":
                        found = True
                if len(resWarmWater) == 12 and not found:
                    break
            for x in range(2):
                tags = [WKHPTag.ENG_PRODUCTION_POOL01,
                        WKHPTag.ENG_PRODUCTION_POOL02,
                        WKHPTag.ENG_PRODUCTION_POOL03,
                        WKHPTag.ENG_PRODUCTION_POOL04,
                        WKHPTag.ENG_PRODUCTION_POOL05,
                        WKHPTag.ENG_PRODUCTION_POOL06,
                        WKHPTag.ENG_PRODUCTION_POOL07,
                        WKHPTag.ENG_PRODUCTION_POOL08,
                        WKHPTag.ENG_PRODUCTION_POOL09,
                        WKHPTag.ENG_PRODUCTION_POOL10,
                        WKHPTag.ENG_PRODUCTION_POOL11,
                        WKHPTag.ENG_PRODUCTION_POOL12]
                resPool = await self._coordinator.async_read_values(tags)
                found = False
                for value in resPool:
                    if resPool.get(value, {"value": "unknown"})["value"] == "unknown":
                        found = True
                if len(resPool) == 12 and not found:
                    break
            for x in range(2):
                tags = [WKHPTag.ENG_HEATPUMP_COP_MONTH01,
                        WKHPTag.ENG_HEATPUMP_COP_MONTH02,
                        WKHPTag.ENG_HEATPUMP_COP_MONTH03,
                        WKHPTag.ENG_HEATPUMP_COP_MONTH04,
                        WKHPTag.ENG_HEATPUMP_COP_MONTH05,
                        WKHPTag.ENG_HEATPUMP_COP_MONTH06,
                        WKHPTag.ENG_HEATPUMP_COP_MONTH07,
                        WKHPTag.ENG_HEATPUMP_COP_MONTH08,
                        WKHPTag.ENG_HEATPUMP_COP_MONTH09,
                        WKHPTag.ENG_HEATPUMP_COP_MONTH10,
                        WKHPTag.ENG_HEATPUMP_COP_MONTH11,
                        WKHPTag.ENG_HEATPUMP_COP_MONTH12]
                resHeatpumpCopMonth = await self._coordinator.async_read_values(tags)
                found = False
                for value in resHeatpumpCopMonth:
                    if resHeatpumpCopMonth.get(value, {"value": "unknown"})["value"] == "unknown":
                        found = True
                if len(resHeatpumpCopMonth) == 12 and not found:
                    break
            for x in range(2):
                tags = [WKHPTag.DATE_MONTH,
                        WKHPTag.DATE_YEAR,
                        WKHPTag.COP_HEATPUMP_YEAR,
                        WKHPTag.COP_HEATPUMP_ACTUAL_YEAR_INFO]
                resDate = await self._coordinator.async_read_values(tags)
                found = False
                for value in resDate:
                    if resDate.get(value, {"value": "unknown"})["value"] == "unknown":
                        found = True
                if len(resDate) == 4 and not found:
                    break
        except ValueError:
            return "unavailable"
        ret = {
            "cop_year": resDate.get(WKHPTag.COP_HEATPUMP_ACTUAL_YEAR_INFO, {"value": "unknown"})["value"],
            "cop": resDate.get(WKHPTag.COP_HEATPUMP_YEAR, {"value": "unknown"})["value"],
            "heatpump_month": resDate.get(WKHPTag.DATE_MONTH, {"value": "unknown"})["value"],
            "heatpump_year": resDate.get(WKHPTag.DATE_YEAR, {"value": "unknown"})["value"],
            "month_01": {
                "cop": resHeatpumpCopMonth.get(WKHPTag.ENG_HEATPUMP_COP_MONTH01, {"value": "unknown"})["value"],
                "compressor": resCompressor.get(WKHPTag.ENG_CONSUMPTION_COMPRESSOR01, {"value": "unknown"})["value"],
                "sourcepump": resSourcePump.get(WKHPTag.ENG_CONSUMPTION_SOURCEPUMP01, {"value": "unknown"})["value"],
                "externalheater": resExternalHeater.get(WKHPTag.ENG_CONSUMPTION_EXTERNALHEATER01, {"value": "unknown"})[
                    "value"],
                "heating": resHeater.get(WKHPTag.ENG_PRODUCTION_HEATING01, {"value": "unknown"})["value"],
                "warmwater": resWarmWater.get(WKHPTag.ENG_PRODUCTION_WARMWATER01, {"value": "unknown"})["value"],
                "pool": resPool.get(WKHPTag.ENG_PRODUCTION_POOL01, {"value": "unknown"})["value"]
            },
            "month_02": {
                "cop": resHeatpumpCopMonth.get(WKHPTag.ENG_HEATPUMP_COP_MONTH02, {"value": "unknown"})["value"],
                "compressor": resCompressor.get(WKHPTag.ENG_CONSUMPTION_COMPRESSOR02, {"value": "unknown"})["value"],
                "sourcepump": resSourcePump.get(WKHPTag.ENG_CONSUMPTION_SOURCEPUMP02, {"value": "unknown"})["value"],
                "externalheater": resExternalHeater.get(WKHPTag.ENG_CONSUMPTION_EXTERNALHEATER02, {"value": "unknown"})[
                    "value"],
                "heating": resHeater.get(WKHPTag.ENG_PRODUCTION_HEATING02, {"value": "unknown"})["value"],
                "warmwater": resWarmWater.get(WKHPTag.ENG_PRODUCTION_WARMWATER02, {"value": "unknown"})["value"],
                "pool": resPool.get(WKHPTag.ENG_PRODUCTION_POOL02, {"value": "unknown"})["value"]
            },
            "month_03": {
                "cop": resHeatpumpCopMonth.get(WKHPTag.ENG_HEATPUMP_COP_MONTH03, {"value": "unknown"})["value"],
                "compressor": resCompressor.get(WKHPTag.ENG_CONSUMPTION_COMPRESSOR03, {"value": "unknown"})["value"],
                "sourcepump": resSourcePump.get(WKHPTag.ENG_CONSUMPTION_SOURCEPUMP03, {"value": "unknown"})["value"],
                "externalheater": resExternalHeater.get(WKHPTag.ENG_CONSUMPTION_EXTERNALHEATER03, {"value": "unknown"})[
                    "value"],
                "heating": resHeater.get(WKHPTag.ENG_PRODUCTION_HEATING03, {"value": "unknown"})["value"],
                "warmwater": resWarmWater.get(WKHPTag.ENG_PRODUCTION_WARMWATER03, {"value": "unknown"})["value"],
                "pool": resPool.get(WKHPTag.ENG_PRODUCTION_POOL03, {"value": "unknown"})["value"]
            },
            "month_04": {
                "cop": resHeatpumpCopMonth.get(WKHPTag.ENG_HEATPUMP_COP_MONTH04, {"value": "unknown"})["value"],
                "compressor": resCompressor.get(WKHPTag.ENG_CONSUMPTION_COMPRESSOR04, {"value": "unknown"})["value"],
                "sourcepump": resSourcePump.get(WKHPTag.ENG_CONSUMPTION_SOURCEPUMP04, {"value": "unknown"})["value"],
                "externalheater": resExternalHeater.get(WKHPTag.ENG_CONSUMPTION_EXTERNALHEATER04, {"value": "unknown"})[
                    "value"],
                "heating": resHeater.get(WKHPTag.ENG_PRODUCTION_HEATING04, {"value": "unknown"})["value"],
                "warmwater": resWarmWater.get(WKHPTag.ENG_PRODUCTION_WARMWATER04, {"value": "unknown"})["value"],
                "pool": resPool.get(WKHPTag.ENG_PRODUCTION_POOL04, {"value": "unknown"})["value"]
            },
            "month_05": {
                "cop": resHeatpumpCopMonth.get(WKHPTag.ENG_HEATPUMP_COP_MONTH05, {"value": "unknown"})["value"],
                "compressor": resCompressor.get(WKHPTag.ENG_CONSUMPTION_COMPRESSOR05, {"value": "unknown"})["value"],
                "sourcepump": resSourcePump.get(WKHPTag.ENG_CONSUMPTION_SOURCEPUMP05, {"value": "unknown"})["value"],
                "externalheater": resExternalHeater.get(WKHPTag.ENG_CONSUMPTION_EXTERNALHEATER05, {"value": "unknown"})[
                    "value"],
                "heating": resHeater.get(WKHPTag.ENG_PRODUCTION_HEATING05, {"value": "unknown"})["value"],
                "warmwater": resWarmWater.get(WKHPTag.ENG_PRODUCTION_WARMWATER05, {"value": "unknown"})["value"],
                "pool": resPool.get(WKHPTag.ENG_PRODUCTION_POOL05, {"value": "unknown"})["value"]
            },
            "month_06": {
                "cop": resHeatpumpCopMonth.get(WKHPTag.ENG_HEATPUMP_COP_MONTH06, {"value": "unknown"})["value"],
                "compressor": resCompressor.get(WKHPTag.ENG_CONSUMPTION_COMPRESSOR06, {"value": "unknown"})["value"],
                "sourcepump": resSourcePump.get(WKHPTag.ENG_CONSUMPTION_SOURCEPUMP06, {"value": "unknown"})["value"],
                "externalheater": resExternalHeater.get(WKHPTag.ENG_CONSUMPTION_EXTERNALHEATER06, {"value": "unknown"})[
                    "value"],
                "heating": resHeater.get(WKHPTag.ENG_PRODUCTION_HEATING06, {"value": "unknown"})["value"],
                "warmwater": resWarmWater.get(WKHPTag.ENG_PRODUCTION_WARMWATER06, {"value": "unknown"})["value"],
                "pool": resPool.get(WKHPTag.ENG_PRODUCTION_POOL06, {"value": "unknown"})["value"]
            },
            "month_07": {
                "cop": resHeatpumpCopMonth.get(WKHPTag.ENG_HEATPUMP_COP_MONTH07, {"value": "unknown"})["value"],
                "compressor": resCompressor.get(WKHPTag.ENG_CONSUMPTION_COMPRESSOR07, {"value": "unknown"})["value"],
                "sourcepump": resSourcePump.get(WKHPTag.ENG_CONSUMPTION_SOURCEPUMP07, {"value": "unknown"})["value"],
                "externalheater": resExternalHeater.get(WKHPTag.ENG_CONSUMPTION_EXTERNALHEATER07, {"value": "unknown"})[
                    "value"],
                "heating": resHeater.get(WKHPTag.ENG_PRODUCTION_HEATING07, {"value": "unknown"})["value"],
                "warmwater": resWarmWater.get(WKHPTag.ENG_PRODUCTION_WARMWATER07, {"value": "unknown"})["value"],
                "pool": resPool.get(WKHPTag.ENG_PRODUCTION_POOL07, {"value": "unknown"})["value"]
            },
            "month_08": {
                "cop": resHeatpumpCopMonth.get(WKHPTag.ENG_HEATPUMP_COP_MONTH08, {"value": "unknown"})["value"],
                "compressor": resCompressor.get(WKHPTag.ENG_CONSUMPTION_COMPRESSOR08, {"value": "unknown"})["value"],
                "sourcepump": resSourcePump.get(WKHPTag.ENG_CONSUMPTION_SOURCEPUMP08, {"value": "unknown"})["value"],
                "externalheater": resExternalHeater.get(WKHPTag.ENG_CONSUMPTION_EXTERNALHEATER08, {"value": "unknown"})[
                    "value"],
                "heating": resHeater.get(WKHPTag.ENG_PRODUCTION_HEATING08, {"value": "unknown"})["value"],
                "warmwater": resWarmWater.get(WKHPTag.ENG_PRODUCTION_WARMWATER08, {"value": "unknown"})["value"],
                "pool": resPool.get(WKHPTag.ENG_PRODUCTION_POOL08, {"value": "unknown"})["value"]
            },
            "month_09": {
                "cop": resHeatpumpCopMonth.get(WKHPTag.ENG_HEATPUMP_COP_MONTH09, {"value": "unknown"})["value"],
                "compressor": resCompressor.get(WKHPTag.ENG_CONSUMPTION_COMPRESSOR09, {"value": "unknown"})["value"],
                "sourcepump": resSourcePump.get(WKHPTag.ENG_CONSUMPTION_SOURCEPUMP09, {"value": "unknown"})["value"],
                "externalheater": resExternalHeater.get(WKHPTag.ENG_CONSUMPTION_EXTERNALHEATER09, {"value": "unknown"})[
                    "value"],
                "heating": resHeater.get(WKHPTag.ENG_PRODUCTION_HEATING09, {"value": "unknown"})["value"],
                "warmwater": resWarmWater.get(WKHPTag.ENG_PRODUCTION_WARMWATER09, {"value": "unknown"})["value"],
                "pool": resPool.get(WKHPTag.ENG_PRODUCTION_POOL09, {"value": "unknown"})["value"]
            },
            "month_10": {
                "cop": resHeatpumpCopMonth.get(WKHPTag.ENG_HEATPUMP_COP_MONTH10, {"value": "unknown"})["value"],
                "compressor": resCompressor.get(WKHPTag.ENG_CONSUMPTION_COMPRESSOR10, {"value": "unknown"})["value"],
                "sourcepump": resSourcePump.get(WKHPTag.ENG_CONSUMPTION_SOURCEPUMP10, {"value": "unknown"})["value"],
                "externalheater": resExternalHeater.get(WKHPTag.ENG_CONSUMPTION_EXTERNALHEATER10, {"value": "unknown"})[
                    "value"],
                "heating": resHeater.get(WKHPTag.ENG_PRODUCTION_HEATING10, {"value": "unknown"})["value"],
                "warmwater": resWarmWater.get(WKHPTag.ENG_PRODUCTION_WARMWATER10, {"value": "unknown"})["value"],
                "pool": resPool.get(WKHPTag.ENG_PRODUCTION_POOL10, {"value": "unknown"})["value"]
            },
            "month_11": {
                "cop": resHeatpumpCopMonth.get(WKHPTag.ENG_HEATPUMP_COP_MONTH11, {"value": "unknown"})["value"],
                "compressor": resCompressor.get(WKHPTag.ENG_CONSUMPTION_COMPRESSOR11, {"value": "unknown"})["value"],
                "sourcepump": resSourcePump.get(WKHPTag.ENG_CONSUMPTION_SOURCEPUMP11, {"value": "unknown"})["value"],
                "externalheater": resExternalHeater.get(WKHPTag.ENG_CONSUMPTION_EXTERNALHEATER11, {"value": "unknown"})[
                    "value"],
                "heating": resHeater.get(WKHPTag.ENG_PRODUCTION_HEATING11, {"value": "unknown"})["value"],
                "warmwater": resWarmWater.get(WKHPTag.ENG_PRODUCTION_WARMWATER11, {"value": "unknown"})["value"],
                "pool": resPool.get(WKHPTag.ENG_PRODUCTION_POOL11, {"value": "unknown"})["value"]
            },
            "month_12": {
                "cop": resHeatpumpCopMonth.get(WKHPTag.ENG_HEATPUMP_COP_MONTH12, {"value": "unknown"})["value"],
                "compressor": resCompressor.get(WKHPTag.ENG_CONSUMPTION_COMPRESSOR12, {"value": "unknown"})["value"],
                "sourcepump": resSourcePump.get(WKHPTag.ENG_CONSUMPTION_SOURCEPUMP12, {"value": "unknown"})["value"],
                "externalheater": resExternalHeater.get(WKHPTag.ENG_CONSUMPTION_EXTERNALHEATER12, {"value": "unknown"})[
                    "value"],
                "heating": resHeater.get(WKHPTag.ENG_PRODUCTION_HEATING12, {"value": "unknown"})["value"],
                "warmwater": resWarmWater.get(WKHPTag.ENG_PRODUCTION_WARMWATER12, {"value": "unknown"})["value"],
                "pool": resPool.get(WKHPTag.ENG_PRODUCTION_POOL12, {"value": "unknown"})["value"]
            }
        }
        return ret
