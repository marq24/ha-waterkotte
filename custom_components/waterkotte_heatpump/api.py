"""Sample API Client."""
from typing import Sequence
import asyncio
import logging
import socket

# import re
import aiohttp
import async_timeout
from custom_components.waterkotte_heatpump.pywaterkotte_ha.ecotouch import Ecotouch, EcotouchTag, EASYCON, ECOTOUCH
from custom_components.waterkotte_heatpump.pywaterkotte_ha.easycon import Easycon

TIMEOUT = 10

_LOGGER: logging.Logger = logging.getLogger(__package__)

HEADERS = {"Content-type": "application/json; charset=UTF-8"}

class WaterkotteHeatpumpApiClient:
    """Waterkotte Heatpump API Client Class"""

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        session: aiohttp.ClientSession,
        tags: str,
        systemType: str,
        tagsPerRequest: int,
        lc_lang: str = "en"
    ) -> None:
        """Sample API Client."""
        self._username = username
        self._password = password
        self._session = session
        self._host = host
        # self._hass = hass
        self._systemType = systemType
        if systemType == ECOTOUCH:
            self._client = Ecotouch(host, tagsPerRequest, lc_lang)
        elif systemType == EASYCON:
            self._client = Easycon(host)
        else:
            print("Error unknown System type!")
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
        """getter for Tags"""
        return self.__tags

    @tags.setter
    def tags(self, tags):
        self.__tags = tags

    async def login(self) -> None:
        """Login to the API."""
        if self._client.auth_cookies is None:
            try:
                await self._client.login(self._username, self._password)
            except Exception as exception:  # pylint: disable=broad-except
                print(exception)
                await self._client.logout()
                await self._client.login(self._username, self._password)

        # return ret

    async def async_get_data(self) -> dict:
        """Get data from the API."""

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

    async def async_write_value(self, tag: EcotouchTag, value):
        """Write data to API"""
        res = await self._client.write_value(tag, value)
        return res
        # if res is not None:
        #     self.tags[tag] = res

    async def async_set_title(self, value: str) -> None:
        """Get data from the API."""
        url = "https://jsonplaceholder.typicode.com/posts/1"
        await self.api_wrapper("patch", url, data={"title": value}, headers=HEADERS)

    async def api_wrapper(
        # self, method: str, url: str, data: dict = {}, headers: dict = {}
        self,
        method: str,
        url: str,
        data=None,
        headers=None,
    ) -> dict:
        """Get information from the API."""
        if data is None:
            data = {}
        if headers is None:
            headers = {}
        try:
            async with async_timeout.timeout(  # pylint: disable=unexpected-keyword-arg
                TIMEOUT, loop=asyncio.get_event_loop()
            ):
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
