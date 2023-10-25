"""Sample API Client."""
import asyncio
from typing import Sequence
import logging

import aiohttp
from custom_components.waterkotte_heatpump.pywaterkotte_ha.const import EASYCON, ECOTOUCH
from custom_components.waterkotte_heatpump.pywaterkotte_ha.ecotouch import EcotouchBridge, EcotouchTag, \
    TooManyUsersException
from custom_components.waterkotte_heatpump.pywaterkotte_ha.easycon import EasyconBridge

TIMEOUT = 10

_LOGGER: logging.Logger = logging.getLogger(__package__)

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
        tagsPerRequest: int
    ) -> None:
        """Sample API Client."""
        self._username = username
        self._password = password
        self._session = session
        self._host = host
        self._systemType = systemType
        if systemType == ECOTOUCH:
            self._client = EcotouchBridge(host, tagsPerRequest)
        elif systemType == EASYCON:
            self._client = EasyconBridge(host)
        else:
            _LOGGER.error("Error unknown System type!")

        self.tags = tags

    @property
    def tags(self):
        """getter for Tags"""
        return self.__tags

    @tags.setter
    def tags(self, tags):
        if tags is not None:
            _LOGGER.info(f"number of tags to query set to: {len(tags)}")
        self.__tags = tags

    async def login(self) -> None:
        """Login to the API."""
        if self._client.auth_cookies is None:
            try:
                await self._client.login(self._username, self._password)

            except TooManyUsersException as too_may_users:
                _LOGGER.warning(f"TooManyUsers while try to login: {too_may_users}")
                await asyncio.sleep(30)
                try:
                    await self._client.login(self._username, self._password)
                except Exception as ex1:
                    _LOGGER.error(f"Error while RETRY login: {ex1}", ex1)

            except Exception as exception:  # pylint: disable=broad-except
                _LOGGER.error(f"Error while login: {exception}", exception)
                await asyncio.sleep(15)
                await self._client.logout()
                try:
                    await self._client.login(self._username, self._password)
                except Exception as ex1:
                    _LOGGER.error(f"Error while RETRY login: {ex1}", ex1)

    async def logout(self) -> None:
        await self._client.logout()

    async def async_get_data(self) -> dict:
        """Get data from the API."""

        res = await self._client.read_values(self.tags)
        return res

    async def async_read_values(self, tags: Sequence[EcotouchTag]) -> dict:
        """Get data from the API."""
        res = await self._client.read_values(tags)
        return res

    async def async_read_value(self, tag: EcotouchTag) -> dict:
        """Get data from the API."""
        res = await self._client.read_value(tag)
        return res

    async def async_write_value(self, tag: EcotouchTag, value):
        """Write data to API"""
        res = await self._client.write_value(tag, value)
        return res
        # if res is not None:
        #     self.tags[tag] = res
