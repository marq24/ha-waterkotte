"""Sample API Client."""
from typing import Sequence
import asyncio
import logging
import socket
# import re
import aiohttp
import async_timeout
from .pywaterkotte.ecotouch import Ecotouch, EcotouchTag


TIMEOUT = 10


_LOGGER: logging.Logger = logging.getLogger(__package__)

HEADERS = {"Content-type": "application/json; charset=UTF-8"}


class WaterkotteHeatpumpApiClient:
    """ Waterkotte Heatpump API Client Class """

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        session: aiohttp.ClientSession,
        tags: str,
    ) -> None:
        """Sample API Client."""
        self._username = username
        self._password = password
        self._session = session
        self._host = host
        # self._hass = hass
        self._client = Ecotouch(host)
        # self._entities = []
        self.tags = tags
        # # session = async_create_clientsession(self.hass)
        # client = Ecotouch(host)
        # await client.login(username, password)
        # ret = await client.read_value(EcotouchTag.DATE_DAY)
        # # print(ret)
        # return ret["status"] == "E_OK"
        # # await client.async_get_data()

    @property
    def tags(self):
        return self.__tags

    @tags.setter
    def tags(self, tags):
        self.__tags = tags

    async def login(self) -> None:
        """Login to the API."""
        if self._client.auth_cookies is None:
            await self._client.login(self._username, self._password)

        # return ret

    async def async_get_data(self) -> dict:
        """Get data from the API."""

        # tags = [
        #     EcotouchTag.ENABLE_COOLING,
        #     EcotouchTag.ENABLE_HEATING,
        #     EcotouchTag.ENABLE_PV,
        #     EcotouchTag.ENABLE_WARMWATER,
        #     EcotouchTag.STATE_WATER,
        #     EcotouchTag.STATE_COOLING,
        #     EcotouchTag.STATE_SOURCEPUMP,
        #     EcotouchTag.STATUS_HEATING,
        #     EcotouchTag.STATUS_WATER,
        #     EcotouchTag.STATUS_COOLING,
        #     EcotouchTag.TEMPERATURE_OUTSIDE,
        #     EcotouchTag.TEMPERATURE_OUTSIDE_1H,
        #     EcotouchTag.TEMPERATURE_OUTSIDE_24H,
        #     EcotouchTag.TEMPERATURE_SOURCE_IN,
        #     EcotouchTag.TEMPERATURE_SOURCE_OUT,
        #     EcotouchTag.TEMPERATURE_EVAPORATION,
        #     EcotouchTag.TEMPERATURE_SUCTION,
        #     EcotouchTag.TEMPERATURE_RETURN_SET,
        #     EcotouchTag.TEMPERATURE_RETURN,
        #     EcotouchTag.TEMPERATURE_FLOW,
        #     EcotouchTag.TEMPERATURE_CONDENSATION,
        #     EcotouchTag.TEMPERATURE_STORAGE,
        #     EcotouchTag.TEMPERATURE_ROOM,
        #     EcotouchTag.TEMPERATURE_ROOM_1H,
        #     EcotouchTag.TEMPERATURE_WATER,
        #     EcotouchTag.TEMPERATURE_POOL,
        #     EcotouchTag.TEMPERATURE_SOLAR,
        #     EcotouchTag.TEMPERATURE_SOLAR_FLOW,
        # ]
        ret = await self._client.read_values(self.tags)
        return ret

    async def async_read_values(self, tags: Sequence[EcotouchTag]) -> dict:
        """Get data from the API."""
        ret = await self._client.read_values(tags)
        return ret

    async def async_read_value(self, tag: EcotouchTag) -> dict:
        """Get data from the API."""
        ret = await self._client.read_value(tag)
        return ret

    async def async_set_title(self, value: str) -> None:
        """Get data from the API."""
        url = "https://jsonplaceholder.typicode.com/posts/1"
        await self.api_wrapper("patch", url, data={"title": value}, headers=HEADERS)

    async def api_wrapper(
        # self, method: str, url: str, data: dict = {}, headers: dict = {}
        self, method: str, url: str, data=None, headers=None
    ) -> dict:
        """Get information from the API."""
        if data is None:
            data = {}
        if headers is None:
            headers = {}
        try:
            async with async_timeout.timeout(TIMEOUT, loop=asyncio.get_event_loop()):  # pylint: disable=unexpected-keyword-arg
                # async with async_timeout.timeout(TIMEOUT):
                if method == "get":
                    response = await self._session.get(url, headers=headers)
                    return await response.json()

                elif method == "put":
                    await self._session.put(url, headers=headers, json=data)

                elif method == "patch":
                    await self._session.patch(url, headers=headers, json=data)

                elif method == "post":
                    await self._session.post(url, headers=headers, json=data)

        except asyncio.TimeoutError as exception:
            _LOGGER.error(
                "Timeout error fetching information from %s - %s",
                url,
                exception,
            )

        except (KeyError, TypeError) as exception:
            _LOGGER.error(
                "Error parsing information from %s - %s",
                url,
                exception,
            )
        except (aiohttp.ClientError, socket.gaierror) as exception:
            _LOGGER.error(
                "Error fetching information from %s - %s",
                url,
                exception,
            )
        except Exception as exception:  # pylint: disable=broad-except
            _LOGGER.error("Something really wrong happened! - %s", exception)
