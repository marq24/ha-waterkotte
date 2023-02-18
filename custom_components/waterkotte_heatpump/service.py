""" Service to setup time for holiday mode """
# from .const import DOMAIN
import datetime
from custom_components.waterkotte_heatpump.mypywaterkotte.ecotouch import EcotouchTag

class WaterkotteHeatpumpService():
    """waterkotte_heatpump switch class."""

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

    async def set_time(self, call):
        """Handle the service call."""
        # name = call.data.get(ATTR_NAME, DEFAULT_NAME)
        startTime = call.data.get('starthhmm', None)
        if startTime is not None:
            startTime = datetime.time.strftime(startTime, '%H:%M')
        print(f"Time: {startTime}")
        try:
            # print(option)
            # await self._coordinator.api.async_write_value(SENSOR_TYPES[self._type][1], option)
            await self._coordinator.async_write_tag(EcotouchTag.SCHEDULE_WATER_DISINFECTION_START_TIME, startTime)
            # sensor = SENSOR_TYPES[self._type]
            # return self._coordinator.data[sensor[1]]["value"]
        except ValueError:
            return "unavailable"
        # self._hass.states.set("waterkotte.set_holiday", name)
