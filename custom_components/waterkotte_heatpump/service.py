""" Service to setup time for holiday mode """
# from .const import DOMAIN
import datetime
#from re import M
from pywaterkotte.ecotouch import EcotouchTag
#import voluptuous as vol
#from typing import Sequence
#from homeassistant.util.json import JsonObjectType
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse, SupportsResponse

class WaterkotteHeatpumpService():
    """waterkotte_heatpump switch class."""

    # GET_ENERGY_BALANCE_SERVICE_NAME = "get_energy_balance"
    # GET_ENERGY_BALANCE_SCHEMA = vol.Schema({
    #     vol.Required("year"): int,
    #     vol.Required("cop"): float,
    #     vol.Required("compressor"): float,
    #     vol.Required("sourcepump"): float,
    #     vol.Required("externalheater"): float,
    #     vol.Required("heating"): float,
    #     vol.Required("warmwater"): float,
    #     vol.Required("pool"): float,
    # })


    def __init__(self, hass, config, coordinator):  # pylint: disable=unused-argument
        """Initialize the sensor."""
        self._hass = hass
        self._config = config
        self._coordinator = coordinator

    async def set_holiday(self, call):
        """Handle the service call."""
       # name = call.data.get(ATTR_NAME, DEFAULT_NAME)
        start = call.data.get('start', None)
        end = call.data.get('end', None)
        if start is not None and end is not None:
            start = datetime.datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
            end = datetime.datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
        print(f"Start: {start} End: {end}")
        try:
            # print(option)
            # await self._coordinator.api.async_write_value(SENSOR_TYPES[self._type][1], option)
            await self._coordinator.async_write_tag(EcotouchTag.HOLIDAY_START_TIME, start)
            await self._coordinator.async_write_tag(EcotouchTag.HOLIDAY_END_TIME, end)
            # sensor = SENSOR_TYPES[self._type]
            # return self._coordinator.data[sensor[1]]["value"]
        except ValueError:
            return "unavailable"
        # self._hass.states.set("waterkotte.set_holiday", name)

    async def get_energy_balance(self, call: ServiceCall) -> ServiceResponse:
        """Handle the service call."""

        try:
            tags=[EcotouchTag.ANUAL_CONSUMPTION_COMPRESSOR,
                  EcotouchTag.ANUAL_CONSUMPTION_SOURCEPUMP,
                  EcotouchTag.ANUAL_CONSUMPTION_EXTERNALHEATER,
                  EcotouchTag.ANUAL_CONSUMPTION_HEATING,
                  EcotouchTag.ANUAL_CONSUMPTION_WATER,
                  EcotouchTag.ANUAL_CONSUMPTION_POOL,
                  EcotouchTag.HEATPUMP_COP,
                  EcotouchTag.HEATPUMP_COP_YEAR]
            res = await self._coordinator.async_read_values(tags)

        except ValueError:
            return "unavailable"
        ret= {
            "year":res.get(EcotouchTag.HEATPUMP_COP_YEAR,{"value":"unknown"})["value"],
            "cop":res.get(EcotouchTag.HEATPUMP_COP,{"value":"unknown"})["value"],
            "compressor":res.get(EcotouchTag.ANUAL_CONSUMPTION_COMPRESSOR,{"value":"unknown"})["value"],
            "sourcepump":res.get(EcotouchTag.ANUAL_CONSUMPTION_SOURCEPUMP,{"value":"unknown"})["value"],
            "externalheater":res.get(EcotouchTag.ANUAL_CONSUMPTION_EXTERNALHEATER,{"value":"unknown"})["value"],
            "heating":res.get(EcotouchTag.ANUAL_CONSUMPTION_HEATING,{"value":"unknown"})["value"],
            "warmwater":res.get(EcotouchTag.ANUAL_CONSUMPTION_WATER,{"value":"unknown"})["value"],
            "pool":res.get(EcotouchTag.ANUAL_CONSUMPTION_POOL,{"value":"unknown"})["value"]}
        return ret

    async def get_energy_balance_monthly(self, call: ServiceCall) -> ServiceResponse:
        try:
            for x in range(2):
                tags=[EcotouchTag.CONSUMPTION_COMPRESSOR1,
                    EcotouchTag.CONSUMPTION_COMPRESSOR2,
                    EcotouchTag.CONSUMPTION_COMPRESSOR3,
                    EcotouchTag.CONSUMPTION_COMPRESSOR4,
                    EcotouchTag.CONSUMPTION_COMPRESSOR5,
                    EcotouchTag.CONSUMPTION_COMPRESSOR6,
                    EcotouchTag.CONSUMPTION_COMPRESSOR7,
                    EcotouchTag.CONSUMPTION_COMPRESSOR8,
                    EcotouchTag.CONSUMPTION_COMPRESSOR9,
                    EcotouchTag.CONSUMPTION_COMPRESSOR10,
                    EcotouchTag.CONSUMPTION_COMPRESSOR11,
                    EcotouchTag.CONSUMPTION_COMPRESSOR12]
                resCompressor = await self._coordinator.async_read_values(tags)
                found=False
                for value in resCompressor:
                    if resCompressor.get(value,{"value":"unknown"})["value"] == "unknown":
                        found=True
                if len(resCompressor)==12 and not found:
                    break
            for x in range(2):
                tags=[EcotouchTag.CONSUMPTION_SOURCEPUMP1,
                    EcotouchTag.CONSUMPTION_SOURCEPUMP2,
                    EcotouchTag.CONSUMPTION_SOURCEPUMP3,
                    EcotouchTag.CONSUMPTION_SOURCEPUMP4,
                    EcotouchTag.CONSUMPTION_SOURCEPUMP5,
                    EcotouchTag.CONSUMPTION_SOURCEPUMP6,
                    EcotouchTag.CONSUMPTION_SOURCEPUMP7,
                    EcotouchTag.CONSUMPTION_SOURCEPUMP8,
                    EcotouchTag.CONSUMPTION_SOURCEPUMP9,
                    EcotouchTag.CONSUMPTION_SOURCEPUMP10,
                    EcotouchTag.CONSUMPTION_SOURCEPUMP11,
                    EcotouchTag.CONSUMPTION_SOURCEPUMP12]
                resSourcePump = await self._coordinator.async_read_values(tags)
                found=False
                for value in resSourcePump:
                    if resSourcePump.get(value,{"value":"unknown"})["value"] == "unknown":
                        found=True
                if len(resSourcePump)==12 and not found:
                    break
            for x in range(2):
                tags=[EcotouchTag.CONSUMPTION_EXTERNALHEATER1,
                    EcotouchTag.CONSUMPTION_EXTERNALHEATER2,
                    EcotouchTag.CONSUMPTION_EXTERNALHEATER3,
                    EcotouchTag.CONSUMPTION_EXTERNALHEATER4,
                    EcotouchTag.CONSUMPTION_EXTERNALHEATER5,
                    EcotouchTag.CONSUMPTION_EXTERNALHEATER6,
                    EcotouchTag.CONSUMPTION_EXTERNALHEATER7,
                    EcotouchTag.CONSUMPTION_EXTERNALHEATER8,
                    EcotouchTag.CONSUMPTION_EXTERNALHEATER9,
                    EcotouchTag.CONSUMPTION_EXTERNALHEATER10,
                    EcotouchTag.CONSUMPTION_EXTERNALHEATER11,
                    EcotouchTag.CONSUMPTION_EXTERNALHEATER12]
                resExternalHeater = await self._coordinator.async_read_values(tags)
                found=False
                for value in resExternalHeater:
                    if resExternalHeater.get(value,{"value":"unknown"})["value"] == "unknown":
                        found=True
                if len(resExternalHeater)==12 and not found:
                    break
            for x in range(2):
                tags=[EcotouchTag.CONSUMPTION_HEATING1,
                    EcotouchTag.CONSUMPTION_HEATING2,
                    EcotouchTag.CONSUMPTION_HEATING3,
                    EcotouchTag.CONSUMPTION_HEATING4,
                    EcotouchTag.CONSUMPTION_HEATING5,
                    EcotouchTag.CONSUMPTION_HEATING6,
                    EcotouchTag.CONSUMPTION_HEATING7,
                    EcotouchTag.CONSUMPTION_HEATING8,
                    EcotouchTag.CONSUMPTION_HEATING9,
                    EcotouchTag.CONSUMPTION_HEATING10,
                    EcotouchTag.CONSUMPTION_HEATING11,
                    EcotouchTag.CONSUMPTION_HEATING12]
                resHeater = await self._coordinator.async_read_values(tags)
                found=False
                for value in resHeater:
                    if resHeater.get(value,{"value":"unknown"})["value"] == "unknown":
                        found=True
                if len(resHeater)==12 and not found:
                    break
            for x in range(2):
                tags=[EcotouchTag.CONSUMPTION_WARMWATER1,
                    EcotouchTag.CONSUMPTION_WARMWATER2,
                    EcotouchTag.CONSUMPTION_WARMWATER3,
                    EcotouchTag.CONSUMPTION_WARMWATER4,
                    EcotouchTag.CONSUMPTION_WARMWATER5,
                    EcotouchTag.CONSUMPTION_WARMWATER6,
                    EcotouchTag.CONSUMPTION_WARMWATER7,
                    EcotouchTag.CONSUMPTION_WARMWATER8,
                    EcotouchTag.CONSUMPTION_WARMWATER9,
                    EcotouchTag.CONSUMPTION_WARMWATER10,
                    EcotouchTag.CONSUMPTION_WARMWATER11,
                    EcotouchTag.CONSUMPTION_WARMWATER12]
                resWarmWater = await self._coordinator.async_read_values(tags)
                found=False
                for value in resWarmWater:
                    if resWarmWater.get(value,{"value":"unknown"})["value"] == "unknown":
                        found=True
                if len(resWarmWater)==12 and not found:
                    break
            for x in range(2):
                tags=[EcotouchTag.CONSUMPTION_POOL1,
                    EcotouchTag.CONSUMPTION_POOL2,
                    EcotouchTag.CONSUMPTION_POOL3,
                    EcotouchTag.CONSUMPTION_POOL4,
                    EcotouchTag.CONSUMPTION_POOL5,
                    EcotouchTag.CONSUMPTION_POOL6,
                    EcotouchTag.CONSUMPTION_POOL7,
                    EcotouchTag.CONSUMPTION_POOL8,
                    EcotouchTag.CONSUMPTION_POOL9,
                    EcotouchTag.CONSUMPTION_POOL10,
                    EcotouchTag.CONSUMPTION_POOL11,
                    EcotouchTag.CONSUMPTION_POOL12]
                resPool = await self._coordinator.async_read_values(tags)
                found=False
                for value in resPool:
                    if resPool.get(value,{"value":"unknown"})["value"] == "unknown":
                        found=True
                if len(resPool)==12 and not found:
                    break
            for x in range(2):
                tags=[EcotouchTag.HEATPUMP_COP_MONTH1,
                    EcotouchTag.HEATPUMP_COP_MONTH2,
                    EcotouchTag.HEATPUMP_COP_MONTH3,
                    EcotouchTag.HEATPUMP_COP_MONTH4,
                    EcotouchTag.HEATPUMP_COP_MONTH5,
                    EcotouchTag.HEATPUMP_COP_MONTH6,
                    EcotouchTag.HEATPUMP_COP_MONTH7,
                    EcotouchTag.HEATPUMP_COP_MONTH8,
                    EcotouchTag.HEATPUMP_COP_MONTH9,
                    EcotouchTag.HEATPUMP_COP_MONTH10,
                    EcotouchTag.HEATPUMP_COP_MONTH11,
                    EcotouchTag.HEATPUMP_COP_MONTH12]
                resHeatpumpCopMonth = await self._coordinator.async_read_values(tags)
                found=False
                for value in resHeatpumpCopMonth:
                    if resHeatpumpCopMonth.get(value,{"value":"unknown"})["value"] == "unknown":
                        found=True
                if len(resHeatpumpCopMonth)==12 and not found:
                    break
            for x in range(2):
                tags=[EcotouchTag.DATE_MONTH,
                    EcotouchTag.DATE_YEAR,
                    EcotouchTag.HEATPUMP_COP,
                    EcotouchTag.HEATPUMP_COP_YEAR]
                resDate = await self._coordinator.async_read_values(tags)
                found=False
                for value in resDate:
                    if resDate.get(value,{"value":"unknown"})["value"] == "unknown":
                        found=True
                if len(resDate)==4 and not found:
                    break
        except ValueError:
            return "unavailable"
        ret= {
            "cop_year":resDate.get(EcotouchTag.HEATPUMP_COP_YEAR,{"value":"unknown"})["value"],
            "cop":resDate.get(EcotouchTag.HEATPUMP_COP,{"value":"unknown"})["value"],
            "heatpump_month":resDate.get(EcotouchTag.DATE_MONTH,{"value":"unknown"})["value"],
            "heatpump_year":resDate.get(EcotouchTag.DATE_YEAR,{"value":"unknown"})["value"],
            "month1":{
                "cop":resHeatpumpCopMonth.get(EcotouchTag.HEATPUMP_COP_MONTH1,{"value":"unknown"})["value"],
                "compressor":resCompressor.get(EcotouchTag.CONSUMPTION_COMPRESSOR1,{"value":"unknown"})["value"],
                "sourcepump":resSourcePump.get(EcotouchTag.CONSUMPTION_SOURCEPUMP1,{"value":"unknown"})["value"],
                "externalheater":resExternalHeater.get(EcotouchTag.CONSUMPTION_EXTERNALHEATER1,{"value":"unknown"})["value"],
                "heating":resHeater.get(EcotouchTag.CONSUMPTION_HEATING1,{"value":"unknown"})["value"],
                "warmwater":resWarmWater.get(EcotouchTag.CONSUMPTION_WARMWATER1,{"value":"unknown"})["value"],
                "pool":resPool.get(EcotouchTag.CONSUMPTION_POOL1,{"value":"unknown"})["value"]
                },
            "month2":{
                "cop":resHeatpumpCopMonth.get(EcotouchTag.HEATPUMP_COP_MONTH2,{"value":"unknown"})["value"],
                "compressor":resCompressor.get(EcotouchTag.CONSUMPTION_COMPRESSOR2,{"value":"unknown"})["value"],
                "sourcepump":resSourcePump.get(EcotouchTag.CONSUMPTION_SOURCEPUMP2,{"value":"unknown"})["value"],
                "externalheater":resExternalHeater.get(EcotouchTag.CONSUMPTION_EXTERNALHEATER2,{"value":"unknown"})["value"],
                "heating":resHeater.get(EcotouchTag.CONSUMPTION_HEATING2,{"value":"unknown"})["value"],
                "warmwater":resWarmWater.get(EcotouchTag.CONSUMPTION_WARMWATER2,{"value":"unknown"})["value"],
                "pool":resPool.get(EcotouchTag.CONSUMPTION_POOL2,{"value":"unknown"})["value"]
                },
            "month3":{
                "cop":resHeatpumpCopMonth.get(EcotouchTag.HEATPUMP_COP_MONTH3,{"value":"unknown"})["value"],
                "compressor":resCompressor.get(EcotouchTag.CONSUMPTION_COMPRESSOR3,{"value":"unknown"})["value"],
                "sourcepump":resSourcePump.get(EcotouchTag.CONSUMPTION_SOURCEPUMP3,{"value":"unknown"})["value"],
                "externalheater":resExternalHeater.get(EcotouchTag.CONSUMPTION_EXTERNALHEATER3,{"value":"unknown"})["value"],
                "heating":resHeater.get(EcotouchTag.CONSUMPTION_HEATING3,{"value":"unknown"})["value"],
                "warmwater":resWarmWater.get(EcotouchTag.CONSUMPTION_WARMWATER3,{"value":"unknown"})["value"],
                "pool":resPool.get(EcotouchTag.CONSUMPTION_POOL3,{"value":"unknown"})["value"]
                },
            "month4":{
                "cop":resHeatpumpCopMonth.get(EcotouchTag.HEATPUMP_COP_MONTH4,{"value":"unknown"})["value"],
                "compressor":resCompressor.get(EcotouchTag.CONSUMPTION_COMPRESSOR4,{"value":"unknown"})["value"],
                "sourcepump":resSourcePump.get(EcotouchTag.CONSUMPTION_SOURCEPUMP4,{"value":"unknown"})["value"],
                "externalheater":resExternalHeater.get(EcotouchTag.CONSUMPTION_EXTERNALHEATER4,{"value":"unknown"})["value"],
                "heating":resHeater.get(EcotouchTag.CONSUMPTION_HEATING4,{"value":"unknown"})["value"],
                "warmwater":resWarmWater.get(EcotouchTag.CONSUMPTION_WARMWATER4,{"value":"unknown"})["value"],
                "pool":resPool.get(EcotouchTag.CONSUMPTION_POOL4,{"value":"unknown"})["value"]
                },
            "month5":{
                "cop":resHeatpumpCopMonth.get(EcotouchTag.HEATPUMP_COP_MONTH5,{"value":"unknown"})["value"],
                "compressor":resCompressor.get(EcotouchTag.CONSUMPTION_COMPRESSOR5,{"value":"unknown"})["value"],
                "sourcepump":resSourcePump.get(EcotouchTag.CONSUMPTION_SOURCEPUMP5,{"value":"unknown"})["value"],
                "externalheater":resExternalHeater.get(EcotouchTag.CONSUMPTION_EXTERNALHEATER5,{"value":"unknown"})["value"],
                "heating":resHeater.get(EcotouchTag.CONSUMPTION_HEATING5,{"value":"unknown"})["value"],
                "warmwater":resWarmWater.get(EcotouchTag.CONSUMPTION_WARMWATER5,{"value":"unknown"})["value"],
                "pool":resPool.get(EcotouchTag.CONSUMPTION_POOL5,{"value":"unknown"})["value"]
                },
            "month6":{
                "cop":resHeatpumpCopMonth.get(EcotouchTag.HEATPUMP_COP_MONTH6,{"value":"unknown"})["value"],
                "compressor":resCompressor.get(EcotouchTag.CONSUMPTION_COMPRESSOR6,{"value":"unknown"})["value"],
                "sourcepump":resSourcePump.get(EcotouchTag.CONSUMPTION_SOURCEPUMP6,{"value":"unknown"})["value"],
                "externalheater":resExternalHeater.get(EcotouchTag.CONSUMPTION_EXTERNALHEATER6,{"value":"unknown"})["value"],
                "heating":resHeater.get(EcotouchTag.CONSUMPTION_HEATING6,{"value":"unknown"})["value"],
                "warmwater":resWarmWater.get(EcotouchTag.CONSUMPTION_WARMWATER6,{"value":"unknown"})["value"],
                "pool":resPool.get(EcotouchTag.CONSUMPTION_POOL6,{"value":"unknown"})["value"]
                },
            "month7":{
                "cop":resHeatpumpCopMonth.get(EcotouchTag.HEATPUMP_COP_MONTH7,{"value":"unknown"})["value"],
                "compressor":resCompressor.get(EcotouchTag.CONSUMPTION_COMPRESSOR7,{"value":"unknown"})["value"],
                "sourcepump":resSourcePump.get(EcotouchTag.CONSUMPTION_SOURCEPUMP7,{"value":"unknown"})["value"],
                "externalheater":resExternalHeater.get(EcotouchTag.CONSUMPTION_EXTERNALHEATER7,{"value":"unknown"})["value"],
                "heating":resHeater.get(EcotouchTag.CONSUMPTION_HEATING7,{"value":"unknown"})["value"],
                "warmwater":resWarmWater.get(EcotouchTag.CONSUMPTION_WARMWATER7,{"value":"unknown"})["value"],
                "pool":resPool.get(EcotouchTag.CONSUMPTION_POOL7,{"value":"unknown"})["value"]
                },
            "month8":{
                "cop":resHeatpumpCopMonth.get(EcotouchTag.HEATPUMP_COP_MONTH8,{"value":"unknown"})["value"],
                "compressor":resCompressor.get(EcotouchTag.CONSUMPTION_COMPRESSOR8,{"value":"unknown"})["value"],
                "sourcepump":resSourcePump.get(EcotouchTag.CONSUMPTION_SOURCEPUMP8,{"value":"unknown"})["value"],
                "externalheater":resExternalHeater.get(EcotouchTag.CONSUMPTION_EXTERNALHEATER8,{"value":"unknown"})["value"],
                "heating":resHeater.get(EcotouchTag.CONSUMPTION_HEATING8,{"value":"unknown"})["value"],
                "warmwater":resWarmWater.get(EcotouchTag.CONSUMPTION_WARMWATER8,{"value":"unknown"})["value"],
                "pool":resPool.get(EcotouchTag.CONSUMPTION_POOL8,{"value":"unknown"})["value"]
                },
            "month9":{
                "cop":resHeatpumpCopMonth.get(EcotouchTag.HEATPUMP_COP_MONTH9,{"value":"unknown"})["value"],
                "compressor":resCompressor.get(EcotouchTag.CONSUMPTION_COMPRESSOR9,{"value":"unknown"})["value"],
                "sourcepump":resSourcePump.get(EcotouchTag.CONSUMPTION_SOURCEPUMP9,{"value":"unknown"})["value"],
                "externalheater":resExternalHeater.get(EcotouchTag.CONSUMPTION_EXTERNALHEATER9,{"value":"unknown"})["value"],
                "heating":resHeater.get(EcotouchTag.CONSUMPTION_HEATING9,{"value":"unknown"})["value"],
                "warmwater":resWarmWater.get(EcotouchTag.CONSUMPTION_WARMWATER9,{"value":"unknown"})["value"],
                "pool":resPool.get(EcotouchTag.CONSUMPTION_POOL9,{"value":"unknown"})["value"]
                },
            "month10":{
                "cop":resHeatpumpCopMonth.get(EcotouchTag.HEATPUMP_COP_MONTH10,{"value":"unknown"})["value"],
                "compressor":resCompressor.get(EcotouchTag.CONSUMPTION_COMPRESSOR10,{"value":"unknown"})["value"],
                "sourcepump":resSourcePump.get(EcotouchTag.CONSUMPTION_SOURCEPUMP10,{"value":"unknown"})["value"],
                "externalheater":resExternalHeater.get(EcotouchTag.CONSUMPTION_EXTERNALHEATER10,{"value":"unknown"})["value"],
                "heating":resHeater.get(EcotouchTag.CONSUMPTION_HEATING10,{"value":"unknown"})["value"],
                "warmwater":resWarmWater.get(EcotouchTag.CONSUMPTION_WARMWATER10,{"value":"unknown"})["value"],
                "pool":resPool.get(EcotouchTag.CONSUMPTION_POOL10,{"value":"unknown"})["value"]
                },
            "month11":{
                "cop":resHeatpumpCopMonth.get(EcotouchTag.HEATPUMP_COP_MONTH11,{"value":"unknown"})["value"],
                "compressor":resCompressor.get(EcotouchTag.CONSUMPTION_COMPRESSOR11,{"value":"unknown"})["value"],
                "sourcepump":resSourcePump.get(EcotouchTag.CONSUMPTION_SOURCEPUMP11,{"value":"unknown"})["value"],
                "externalheater":resExternalHeater.get(EcotouchTag.CONSUMPTION_EXTERNALHEATER11,{"value":"unknown"})["value"],
                "heating":resHeater.get(EcotouchTag.CONSUMPTION_HEATING11,{"value":"unknown"})["value"],
                "warmwater":resWarmWater.get(EcotouchTag.CONSUMPTION_WARMWATER11,{"value":"unknown"})["value"],
                "pool":resPool.get(EcotouchTag.CONSUMPTION_POOL11,{"value":"unknown"})["value"]
                },
            "month12":{
                "cop":resHeatpumpCopMonth.get(EcotouchTag.HEATPUMP_COP_MONTH12,{"value":"unknown"})["value"],
                "compressor":resCompressor.get(EcotouchTag.CONSUMPTION_COMPRESSOR12,{"value":"unknown"})["value"],
                "sourcepump":resSourcePump.get(EcotouchTag.CONSUMPTION_SOURCEPUMP12,{"value":"unknown"})["value"],
                "externalheater":resExternalHeater.get(EcotouchTag.CONSUMPTION_EXTERNALHEATER12,{"value":"unknown"})["value"],
                "heating":resHeater.get(EcotouchTag.CONSUMPTION_HEATING12,{"value":"unknown"})["value"],
                "warmwater":resWarmWater.get(EcotouchTag.CONSUMPTION_WARMWATER12,{"value":"unknown"})["value"],
                "pool":resPool.get(EcotouchTag.CONSUMPTION_POOL12,{"value":"unknown"})["value"]
                }
            }
        return ret