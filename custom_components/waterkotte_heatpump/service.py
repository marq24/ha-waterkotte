import datetime
import logging

from homeassistant.core import ServiceCall, ServiceResponse

from custom_components.waterkotte_heatpump.pywaterkotte_ha.ecotouch import EcotouchTag

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
                await self._coordinator.async_write_tag(EcotouchTag.HOLIDAY_START_TIME, start)
                await self._coordinator.async_write_tag(EcotouchTag.HOLIDAY_END_TIME, end)
                await self._coordinator.async_refresh()
            except ValueError:
                return "unavailable"

            if call.return_response:
                return {"result": "ok"}

        if call.return_response:
            return {"result": "error"}

    async def set_disinfection_start_time(self, call: ServiceCall):
        startTime = call.data.get('starthhmm', None)
        if startTime is not None:
            startTime = datetime.time.fromisoformat(str(startTime))
            _LOGGER.debug(f"set_disinfection_start_time: {startTime}")
            try:
                await self._coordinator.async_write_tag(EcotouchTag.SCHEDULE_WATER_DISINFECTION_START_TIME, startTime)
                await self._coordinator.async_refresh()
            except ValueError:
                return "unavailable"
            return True
        return False

    async def get_energy_balance(self, call: ServiceCall) -> ServiceResponse:
        try:
            tags = [EcotouchTag.COMPRESSOR_ELECTRIC_CONSUMPTION_YEAR,
                    EcotouchTag.SOURCEPUMP_ELECTRIC_CONSUMPTION_YEAR,
                    EcotouchTag.ELECTRICAL_HEATER_ELECTRIC_CONSUMPTION_YEAR,
                    EcotouchTag.HEATING_ENERGY_PRODUCTION_YEAR,
                    EcotouchTag.HOT_WATER_ENERGY_PRODUCTION_YEAR,
                    EcotouchTag.POOL_ENERGY_PRODUCTION_YEAR,
                    EcotouchTag.COP_HEATPUMP_YEAR,
                    EcotouchTag.COP_HEATPUMP_ACTUAL_YEAR_INFO]
            res = await self._coordinator.async_read_values(tags)

        except ValueError:
            return "unavailable"
        ret = {
            "year": res.get(EcotouchTag.COP_HEATPUMP_ACTUAL_YEAR_INFO, {"value": "unknown"})["value"],
            "cop": res.get(EcotouchTag.COP_HEATPUMP_YEAR, {"value": "unknown"})["value"],
            "compressor": res.get(EcotouchTag.COMPRESSOR_ELECTRIC_CONSUMPTION_YEAR, {"value": "unknown"})["value"],
            "sourcepump": res.get(EcotouchTag.SOURCEPUMP_ELECTRIC_CONSUMPTION_YEAR, {"value": "unknown"})["value"],
            "externalheater": res.get(EcotouchTag.ELECTRICAL_HEATER_ELECTRIC_CONSUMPTION_YEAR, {"value": "unknown"})["value"],
            "heating": res.get(EcotouchTag.HEATING_ENERGY_PRODUCTION_YEAR, {"value": "unknown"})["value"],
            "warmwater": res.get(EcotouchTag.HOT_WATER_ENERGY_PRODUCTION_YEAR, {"value": "unknown"})["value"],
            "pool": res.get(EcotouchTag.POOL_ENERGY_PRODUCTION_YEAR, {"value": "unknown"})["value"]}
        return ret

    async def get_energy_balance_monthly(self, call: ServiceCall) -> ServiceResponse:
        try:
            for x in range(2):
                tags = [EcotouchTag.ENG_CONSUMPTION_COMPRESSOR01,
                        EcotouchTag.ENG_CONSUMPTION_COMPRESSOR02,
                        EcotouchTag.ENG_CONSUMPTION_COMPRESSOR03,
                        EcotouchTag.ENG_CONSUMPTION_COMPRESSOR04,
                        EcotouchTag.ENG_CONSUMPTION_COMPRESSOR05,
                        EcotouchTag.ENG_CONSUMPTION_COMPRESSOR06,
                        EcotouchTag.ENG_CONSUMPTION_COMPRESSOR07,
                        EcotouchTag.ENG_CONSUMPTION_COMPRESSOR08,
                        EcotouchTag.ENG_CONSUMPTION_COMPRESSOR09,
                        EcotouchTag.ENG_CONSUMPTION_COMPRESSOR10,
                        EcotouchTag.ENG_CONSUMPTION_COMPRESSOR11,
                        EcotouchTag.ENG_CONSUMPTION_COMPRESSOR12]
                resCompressor = await self._coordinator.async_read_values(tags)
                found = False
                for value in resCompressor:
                    if resCompressor.get(value, {"value": "unknown"})["value"] == "unknown":
                        found = True
                if len(resCompressor) == 12 and not found:
                    break
            for x in range(2):
                tags = [EcotouchTag.ENG_CONSUMPTION_SOURCEPUMP01,
                        EcotouchTag.ENG_CONSUMPTION_SOURCEPUMP02,
                        EcotouchTag.ENG_CONSUMPTION_SOURCEPUMP03,
                        EcotouchTag.ENG_CONSUMPTION_SOURCEPUMP04,
                        EcotouchTag.ENG_CONSUMPTION_SOURCEPUMP05,
                        EcotouchTag.ENG_CONSUMPTION_SOURCEPUMP06,
                        EcotouchTag.ENG_CONSUMPTION_SOURCEPUMP07,
                        EcotouchTag.ENG_CONSUMPTION_SOURCEPUMP08,
                        EcotouchTag.ENG_CONSUMPTION_SOURCEPUMP09,
                        EcotouchTag.ENG_CONSUMPTION_SOURCEPUMP10,
                        EcotouchTag.ENG_CONSUMPTION_SOURCEPUMP11,
                        EcotouchTag.ENG_CONSUMPTION_SOURCEPUMP12]
                resSourcePump = await self._coordinator.async_read_values(tags)
                found = False
                for value in resSourcePump:
                    if resSourcePump.get(value, {"value": "unknown"})["value"] == "unknown":
                        found = True
                if len(resSourcePump) == 12 and not found:
                    break
            for x in range(2):
                tags = [EcotouchTag.ENG_CONSUMPTION_EXTERNALHEATER01,
                        EcotouchTag.ENG_CONSUMPTION_EXTERNALHEATER02,
                        EcotouchTag.ENG_CONSUMPTION_EXTERNALHEATER03,
                        EcotouchTag.ENG_CONSUMPTION_EXTERNALHEATER04,
                        EcotouchTag.ENG_CONSUMPTION_EXTERNALHEATER05,
                        EcotouchTag.ENG_CONSUMPTION_EXTERNALHEATER06,
                        EcotouchTag.ENG_CONSUMPTION_EXTERNALHEATER07,
                        EcotouchTag.ENG_CONSUMPTION_EXTERNALHEATER08,
                        EcotouchTag.ENG_CONSUMPTION_EXTERNALHEATER09,
                        EcotouchTag.ENG_CONSUMPTION_EXTERNALHEATER10,
                        EcotouchTag.ENG_CONSUMPTION_EXTERNALHEATER11,
                        EcotouchTag.ENG_CONSUMPTION_EXTERNALHEATER12]
                resExternalHeater = await self._coordinator.async_read_values(tags)
                found = False
                for value in resExternalHeater:
                    if resExternalHeater.get(value, {"value": "unknown"})["value"] == "unknown":
                        found = True
                if len(resExternalHeater) == 12 and not found:
                    break
            for x in range(2):
                tags = [EcotouchTag.ENG_PRODUCTION_HEATING01,
                        EcotouchTag.ENG_PRODUCTION_HEATING02,
                        EcotouchTag.ENG_PRODUCTION_HEATING03,
                        EcotouchTag.ENG_PRODUCTION_HEATING04,
                        EcotouchTag.ENG_PRODUCTION_HEATING05,
                        EcotouchTag.ENG_PRODUCTION_HEATING06,
                        EcotouchTag.ENG_PRODUCTION_HEATING07,
                        EcotouchTag.ENG_PRODUCTION_HEATING08,
                        EcotouchTag.ENG_PRODUCTION_HEATING09,
                        EcotouchTag.ENG_PRODUCTION_HEATING10,
                        EcotouchTag.ENG_PRODUCTION_HEATING11,
                        EcotouchTag.ENG_PRODUCTION_HEATING12]
                resHeater = await self._coordinator.async_read_values(tags)
                found = False
                for value in resHeater:
                    if resHeater.get(value, {"value": "unknown"})["value"] == "unknown":
                        found = True
                if len(resHeater) == 12 and not found:
                    break
            for x in range(2):
                tags = [EcotouchTag.ENG_PRODUCTION_WARMWATER01,
                        EcotouchTag.ENG_PRODUCTION_WARMWATER02,
                        EcotouchTag.ENG_PRODUCTION_WARMWATER03,
                        EcotouchTag.ENG_PRODUCTION_WARMWATER04,
                        EcotouchTag.ENG_PRODUCTION_WARMWATER05,
                        EcotouchTag.ENG_PRODUCTION_WARMWATER06,
                        EcotouchTag.ENG_PRODUCTION_WARMWATER07,
                        EcotouchTag.ENG_PRODUCTION_WARMWATER08,
                        EcotouchTag.ENG_PRODUCTION_WARMWATER09,
                        EcotouchTag.ENG_PRODUCTION_WARMWATER10,
                        EcotouchTag.ENG_PRODUCTION_WARMWATER11,
                        EcotouchTag.ENG_PRODUCTION_WARMWATER12]
                resWarmWater = await self._coordinator.async_read_values(tags)
                found = False
                for value in resWarmWater:
                    if resWarmWater.get(value, {"value": "unknown"})["value"] == "unknown":
                        found = True
                if len(resWarmWater) == 12 and not found:
                    break
            for x in range(2):
                tags = [EcotouchTag.ENG_PRODUCTION_POOL01,
                        EcotouchTag.ENG_PRODUCTION_POOL02,
                        EcotouchTag.ENG_PRODUCTION_POOL03,
                        EcotouchTag.ENG_PRODUCTION_POOL04,
                        EcotouchTag.ENG_PRODUCTION_POOL05,
                        EcotouchTag.ENG_PRODUCTION_POOL06,
                        EcotouchTag.ENG_PRODUCTION_POOL07,
                        EcotouchTag.ENG_PRODUCTION_POOL08,
                        EcotouchTag.ENG_PRODUCTION_POOL09,
                        EcotouchTag.ENG_PRODUCTION_POOL10,
                        EcotouchTag.ENG_PRODUCTION_POOL11,
                        EcotouchTag.ENG_PRODUCTION_POOL12]
                resPool = await self._coordinator.async_read_values(tags)
                found = False
                for value in resPool:
                    if resPool.get(value, {"value": "unknown"})["value"] == "unknown":
                        found = True
                if len(resPool) == 12 and not found:
                    break
            for x in range(2):
                tags = [EcotouchTag.ENG_HEATPUMP_COP_MONTH01,
                        EcotouchTag.ENG_HEATPUMP_COP_MONTH02,
                        EcotouchTag.ENG_HEATPUMP_COP_MONTH03,
                        EcotouchTag.ENG_HEATPUMP_COP_MONTH04,
                        EcotouchTag.ENG_HEATPUMP_COP_MONTH05,
                        EcotouchTag.ENG_HEATPUMP_COP_MONTH06,
                        EcotouchTag.ENG_HEATPUMP_COP_MONTH07,
                        EcotouchTag.ENG_HEATPUMP_COP_MONTH08,
                        EcotouchTag.ENG_HEATPUMP_COP_MONTH09,
                        EcotouchTag.ENG_HEATPUMP_COP_MONTH10,
                        EcotouchTag.ENG_HEATPUMP_COP_MONTH11,
                        EcotouchTag.ENG_HEATPUMP_COP_MONTH12]
                resHeatpumpCopMonth = await self._coordinator.async_read_values(tags)
                found = False
                for value in resHeatpumpCopMonth:
                    if resHeatpumpCopMonth.get(value, {"value": "unknown"})["value"] == "unknown":
                        found = True
                if len(resHeatpumpCopMonth) == 12 and not found:
                    break
            for x in range(2):
                tags = [EcotouchTag.DATE_MONTH,
                        EcotouchTag.DATE_YEAR,
                        EcotouchTag.COP_HEATPUMP_YEAR,
                        EcotouchTag.COP_HEATPUMP_ACTUAL_YEAR_INFO]
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
            "cop_year": resDate.get(EcotouchTag.COP_HEATPUMP_ACTUAL_YEAR_INFO, {"value": "unknown"})["value"],
            "cop": resDate.get(EcotouchTag.COP_HEATPUMP_YEAR, {"value": "unknown"})["value"],
            "heatpump_month": resDate.get(EcotouchTag.DATE_MONTH, {"value": "unknown"})["value"],
            "heatpump_year": resDate.get(EcotouchTag.DATE_YEAR, {"value": "unknown"})["value"],
            "month_01": {
                "cop": resHeatpumpCopMonth.get(EcotouchTag.ENG_HEATPUMP_COP_MONTH01, {"value": "unknown"})["value"],
                "compressor": resCompressor.get(EcotouchTag.ENG_CONSUMPTION_COMPRESSOR01, {"value": "unknown"})["value"],
                "sourcepump": resSourcePump.get(EcotouchTag.ENG_CONSUMPTION_SOURCEPUMP01, {"value": "unknown"})["value"],
                "externalheater": resExternalHeater.get(EcotouchTag.ENG_CONSUMPTION_EXTERNALHEATER01, {"value": "unknown"})["value"],
                "heating": resHeater.get(EcotouchTag.ENG_PRODUCTION_HEATING01, {"value": "unknown"})["value"],
                "warmwater": resWarmWater.get(EcotouchTag.ENG_PRODUCTION_WARMWATER01, {"value": "unknown"})["value"],
                "pool": resPool.get(EcotouchTag.ENG_PRODUCTION_POOL01, {"value": "unknown"})["value"]
            },
            "month_02": {
                "cop": resHeatpumpCopMonth.get(EcotouchTag.ENG_HEATPUMP_COP_MONTH02, {"value": "unknown"})["value"],
                "compressor": resCompressor.get(EcotouchTag.ENG_CONSUMPTION_COMPRESSOR02, {"value": "unknown"})["value"],
                "sourcepump": resSourcePump.get(EcotouchTag.ENG_CONSUMPTION_SOURCEPUMP02, {"value": "unknown"})["value"],
                "externalheater": resExternalHeater.get(EcotouchTag.ENG_CONSUMPTION_EXTERNALHEATER02, {"value": "unknown"})["value"],
                "heating": resHeater.get(EcotouchTag.ENG_PRODUCTION_HEATING02, {"value": "unknown"})["value"],
                "warmwater": resWarmWater.get(EcotouchTag.ENG_PRODUCTION_WARMWATER02, {"value": "unknown"})["value"],
                "pool": resPool.get(EcotouchTag.ENG_PRODUCTION_POOL02, {"value": "unknown"})["value"]
            },
            "month_03": {
                "cop": resHeatpumpCopMonth.get(EcotouchTag.ENG_HEATPUMP_COP_MONTH03, {"value": "unknown"})["value"],
                "compressor": resCompressor.get(EcotouchTag.ENG_CONSUMPTION_COMPRESSOR03, {"value": "unknown"})["value"],
                "sourcepump": resSourcePump.get(EcotouchTag.ENG_CONSUMPTION_SOURCEPUMP03, {"value": "unknown"})["value"],
                "externalheater": resExternalHeater.get(EcotouchTag.ENG_CONSUMPTION_EXTERNALHEATER03, {"value": "unknown"})["value"],
                "heating": resHeater.get(EcotouchTag.ENG_PRODUCTION_HEATING03, {"value": "unknown"})["value"],
                "warmwater": resWarmWater.get(EcotouchTag.ENG_PRODUCTION_WARMWATER03, {"value": "unknown"})["value"],
                "pool": resPool.get(EcotouchTag.ENG_PRODUCTION_POOL03, {"value": "unknown"})["value"]
            },
            "month_04": {
                "cop": resHeatpumpCopMonth.get(EcotouchTag.ENG_HEATPUMP_COP_MONTH04, {"value": "unknown"})["value"],
                "compressor": resCompressor.get(EcotouchTag.ENG_CONSUMPTION_COMPRESSOR04, {"value": "unknown"})["value"],
                "sourcepump": resSourcePump.get(EcotouchTag.ENG_CONSUMPTION_SOURCEPUMP04, {"value": "unknown"})["value"],
                "externalheater": resExternalHeater.get(EcotouchTag.ENG_CONSUMPTION_EXTERNALHEATER04, {"value": "unknown"})["value"],
                "heating": resHeater.get(EcotouchTag.ENG_PRODUCTION_HEATING04, {"value": "unknown"})["value"],
                "warmwater": resWarmWater.get(EcotouchTag.ENG_PRODUCTION_WARMWATER04, {"value": "unknown"})["value"],
                "pool": resPool.get(EcotouchTag.ENG_PRODUCTION_POOL04, {"value": "unknown"})["value"]
            },
            "month_05": {
                "cop": resHeatpumpCopMonth.get(EcotouchTag.ENG_HEATPUMP_COP_MONTH05, {"value": "unknown"})["value"],
                "compressor": resCompressor.get(EcotouchTag.ENG_CONSUMPTION_COMPRESSOR05, {"value": "unknown"})["value"],
                "sourcepump": resSourcePump.get(EcotouchTag.ENG_CONSUMPTION_SOURCEPUMP05, {"value": "unknown"})["value"],
                "externalheater": resExternalHeater.get(EcotouchTag.ENG_CONSUMPTION_EXTERNALHEATER05, {"value": "unknown"})["value"],
                "heating": resHeater.get(EcotouchTag.ENG_PRODUCTION_HEATING05, {"value": "unknown"})["value"],
                "warmwater": resWarmWater.get(EcotouchTag.ENG_PRODUCTION_WARMWATER05, {"value": "unknown"})["value"],
                "pool": resPool.get(EcotouchTag.ENG_PRODUCTION_POOL05, {"value": "unknown"})["value"]
            },
            "month_06": {
                "cop": resHeatpumpCopMonth.get(EcotouchTag.ENG_HEATPUMP_COP_MONTH06, {"value": "unknown"})["value"],
                "compressor": resCompressor.get(EcotouchTag.ENG_CONSUMPTION_COMPRESSOR06, {"value": "unknown"})["value"],
                "sourcepump": resSourcePump.get(EcotouchTag.ENG_CONSUMPTION_SOURCEPUMP06, {"value": "unknown"})["value"],
                "externalheater": resExternalHeater.get(EcotouchTag.ENG_CONSUMPTION_EXTERNALHEATER06, {"value": "unknown"})["value"],
                "heating": resHeater.get(EcotouchTag.ENG_PRODUCTION_HEATING06, {"value": "unknown"})["value"],
                "warmwater": resWarmWater.get(EcotouchTag.ENG_PRODUCTION_WARMWATER06, {"value": "unknown"})["value"],
                "pool": resPool.get(EcotouchTag.ENG_PRODUCTION_POOL06, {"value": "unknown"})["value"]
            },
            "month_07": {
                "cop": resHeatpumpCopMonth.get(EcotouchTag.ENG_HEATPUMP_COP_MONTH07, {"value": "unknown"})["value"],
                "compressor": resCompressor.get(EcotouchTag.ENG_CONSUMPTION_COMPRESSOR07, {"value": "unknown"})["value"],
                "sourcepump": resSourcePump.get(EcotouchTag.ENG_CONSUMPTION_SOURCEPUMP07, {"value": "unknown"})["value"],
                "externalheater": resExternalHeater.get(EcotouchTag.ENG_CONSUMPTION_EXTERNALHEATER07, {"value": "unknown"})["value"],
                "heating": resHeater.get(EcotouchTag.ENG_PRODUCTION_HEATING07, {"value": "unknown"})["value"],
                "warmwater": resWarmWater.get(EcotouchTag.ENG_PRODUCTION_WARMWATER07, {"value": "unknown"})["value"],
                "pool": resPool.get(EcotouchTag.ENG_PRODUCTION_POOL07, {"value": "unknown"})["value"]
            },
            "month_08": {
                "cop": resHeatpumpCopMonth.get(EcotouchTag.ENG_HEATPUMP_COP_MONTH08, {"value": "unknown"})["value"],
                "compressor": resCompressor.get(EcotouchTag.ENG_CONSUMPTION_COMPRESSOR08, {"value": "unknown"})["value"],
                "sourcepump": resSourcePump.get(EcotouchTag.ENG_CONSUMPTION_SOURCEPUMP08, {"value": "unknown"})["value"],
                "externalheater": resExternalHeater.get(EcotouchTag.ENG_CONSUMPTION_EXTERNALHEATER08, {"value": "unknown"})["value"],
                "heating": resHeater.get(EcotouchTag.ENG_PRODUCTION_HEATING08, {"value": "unknown"})["value"],
                "warmwater": resWarmWater.get(EcotouchTag.ENG_PRODUCTION_WARMWATER08, {"value": "unknown"})["value"],
                "pool": resPool.get(EcotouchTag.ENG_PRODUCTION_POOL08, {"value": "unknown"})["value"]
            },
            "month_09": {
                "cop": resHeatpumpCopMonth.get(EcotouchTag.ENG_HEATPUMP_COP_MONTH09, {"value": "unknown"})["value"],
                "compressor": resCompressor.get(EcotouchTag.ENG_CONSUMPTION_COMPRESSOR09, {"value": "unknown"})["value"],
                "sourcepump": resSourcePump.get(EcotouchTag.ENG_CONSUMPTION_SOURCEPUMP09, {"value": "unknown"})["value"],
                "externalheater": resExternalHeater.get(EcotouchTag.ENG_CONSUMPTION_EXTERNALHEATER09, {"value": "unknown"})["value"],
                "heating": resHeater.get(EcotouchTag.ENG_PRODUCTION_HEATING09, {"value": "unknown"})["value"],
                "warmwater": resWarmWater.get(EcotouchTag.ENG_PRODUCTION_WARMWATER09, {"value": "unknown"})["value"],
                "pool": resPool.get(EcotouchTag.ENG_PRODUCTION_POOL09, {"value": "unknown"})["value"]
            },
            "month_10": {
                "cop": resHeatpumpCopMonth.get(EcotouchTag.ENG_HEATPUMP_COP_MONTH10, {"value": "unknown"})["value"],
                "compressor": resCompressor.get(EcotouchTag.ENG_CONSUMPTION_COMPRESSOR10, {"value": "unknown"})["value"],
                "sourcepump": resSourcePump.get(EcotouchTag.ENG_CONSUMPTION_SOURCEPUMP10, {"value": "unknown"})["value"],
                "externalheater": resExternalHeater.get(EcotouchTag.ENG_CONSUMPTION_EXTERNALHEATER10, {"value": "unknown"})["value"],
                "heating": resHeater.get(EcotouchTag.ENG_PRODUCTION_HEATING10, {"value": "unknown"})["value"],
                "warmwater": resWarmWater.get(EcotouchTag.ENG_PRODUCTION_WARMWATER10, {"value": "unknown"})["value"],
                "pool": resPool.get(EcotouchTag.ENG_PRODUCTION_POOL10, {"value": "unknown"})["value"]
            },
            "month_11": {
                "cop": resHeatpumpCopMonth.get(EcotouchTag.ENG_HEATPUMP_COP_MONTH11, {"value": "unknown"})["value"],
                "compressor": resCompressor.get(EcotouchTag.ENG_CONSUMPTION_COMPRESSOR11, {"value": "unknown"})["value"],
                "sourcepump": resSourcePump.get(EcotouchTag.ENG_CONSUMPTION_SOURCEPUMP11, {"value": "unknown"})["value"],
                "externalheater": resExternalHeater.get(EcotouchTag.ENG_CONSUMPTION_EXTERNALHEATER11, {"value": "unknown"})["value"],
                "heating": resHeater.get(EcotouchTag.ENG_PRODUCTION_HEATING11, {"value": "unknown"})["value"],
                "warmwater": resWarmWater.get(EcotouchTag.ENG_PRODUCTION_WARMWATER11, {"value": "unknown"})["value"],
                "pool": resPool.get(EcotouchTag.ENG_PRODUCTION_POOL11, {"value": "unknown"})["value"]
            },
            "month_12": {
                "cop": resHeatpumpCopMonth.get(EcotouchTag.ENG_HEATPUMP_COP_MONTH12, {"value": "unknown"})["value"],
                "compressor": resCompressor.get(EcotouchTag.ENG_CONSUMPTION_COMPRESSOR12, {"value": "unknown"})["value"],
                "sourcepump": resSourcePump.get(EcotouchTag.ENG_CONSUMPTION_SOURCEPUMP12, {"value": "unknown"})["value"],
                "externalheater": resExternalHeater.get(EcotouchTag.ENG_CONSUMPTION_EXTERNALHEATER12, {"value": "unknown"})["value"],
                "heating": resHeater.get(EcotouchTag.ENG_PRODUCTION_HEATING12, {"value": "unknown"})["value"],
                "warmwater": resWarmWater.get(EcotouchTag.ENG_PRODUCTION_WARMWATER12, {"value": "unknown"})["value"],
                "pool": resPool.get(EcotouchTag.ENG_PRODUCTION_POOL12, {"value": "unknown"})["value"]
            }
        }
        return ret
