import asyncio
import logging
import re
import xml.etree.ElementTree as ElemTree

from datetime import datetime

from typing import (
    Any,
    Sequence,
    Tuple,
    List,
    Collection
)

from custom_components.waterkotte_heatpump.pywaterkotte_ha.const import (
    ECOTOUCH,
    EASYCON,
    SERIES,
    SYSTEM_IDS,
    HEATING_MODES,
    TRANSLATIONS
)

from custom_components.waterkotte_heatpump.pywaterkotte_ha.error import (
    InvalidResponseException,
    InvalidValueException,
    StatusException,
    TooManyUsersException,
    Http404Exception
)

from custom_components.waterkotte_heatpump.pywaterkotte_ha.ecotouch import EcotouchTag

_LOGGER: logging.Logger = logging.getLogger(__package__)


class WaterkotteClient:
    def __init__(self, host: str, system_type: str, web_session, tags: str, tags_per_request: int,
                 lang: str = "en") -> None:
        self._host = host
        self._systemType = system_type
        if system_type == ECOTOUCH:
            self._internal_client = EcotouchBridge(host=host, web_session=web_session,
                                                   tags_per_request=tags_per_request, lang=lang)
        elif system_type == EASYCON:
            self._internal_client = EasyconBridge(host=host, web_session=web_session)
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
        if self._internal_client.auth_cookies is None:
            try:
                await self._internal_client.login()

            except TooManyUsersException:
                _LOGGER.warning(f"TooManyUsers while try to login - will just sleep 30sec")
                await asyncio.sleep(30)

            except Exception as exc:  # pylint: disable=broad-except
                _LOGGER.error(f"Error while login will retry in 15sec: {exc}")
                await asyncio.sleep(15)
                await self._internal_client.logout()
                try:
                    await self._internal_client.login()
                except Exception as exc2:
                    _LOGGER.error(f"Error while RETRY login: {exc2}")

    async def logout(self) -> None:
        await self._internal_client.logout()

    async def async_get_data(self) -> dict:
        if self.tags is not None:
            res = await self._internal_client.read_values(self.tags)
            return res

    async def async_read_values(self, tags: Sequence[EcotouchTag]) -> dict:
        res = await self._internal_client.read_values(tags)
        return res

    async def async_read_value(self, tag: EcotouchTag) -> dict:
        res = await self._internal_client.read_value(tag)
        return res

    async def async_write_value(self, tag: EcotouchTag, value):
        res = await self._internal_client.write_value(tag, value)
        return res


#
# Class to control Waterkotte Ecotouch heatpumps.
#
class EcotouchBridge:
    auth_cookies = None

    def __init__(self, host, web_session, tags_per_request: int = 10, lang: str = "en"):
        self.hostname = host
        self.web_session = web_session
        self.tags_per_request = min(tags_per_request, 75)
        self.lang_map = None
        if lang in TRANSLATIONS:
            self.lang_map = TRANSLATIONS[lang]
        else:
            self.lang_map = TRANSLATIONS["en"]

    # def set_token(self, token:str):
    #    cookies: SimpleCookie[str] = SimpleCookie()
    #    cookies.load(f"Set-Cookie: IDALToken={token}; Path=/")
    #    if hasattr(self.web_session, "_cookie_jar"):
    #        jar = getattr(self.web_session, "_cookie_jar")
    #        jar.update_cookies(cookies)
    #        self.auth_cookies = cookies

    # extracts statuscode from response
    def get_status_response(self, r):  # pylint: disable=invalid-name
        """get_status_response"""
        match = re.search(r"^#([A-Z_]+)", r, re.MULTILINE)
        if match is None:
            raise InvalidResponseException("Invalid reply. Status could not be parsed")
        return match.group(1)

    # performs a login. Has to be called before any other method.
    async def login(self):
        """Login to Heat Pump"""
        _LOGGER.info(f"login to waterkotte host {self.hostname}")

        # this is really true - waterkotte have ONLY hardcoded user credentials!
        args = {"username": "waterkotte", "password": "waterkotte"}

        async with self.web_session.get(f"http://{self.hostname}/cgi/login", params=args) as response:
            response.raise_for_status()
            if response.status == 200:
                content = await response.text()

                tc = content.replace('\n', '<nl>')
                tc = tc.replace('\r', '<cr>')
                _LOGGER.info(f"LOGIN status:{response.status} response: {tc}")

                parsed_response = self.get_status_response(content)
                if parsed_response != "S_OK":
                    if parsed_response.startswith("E_TOO_MANY_USERS"):
                        raise TooManyUsersException("TOO_MANY_USERS")
                    else:
                        raise StatusException(f"Error while LOGIN: status: {parsed_response}")

                # since this is a get, we have to do our own cookie handling...
                if response.cookies is not None:
                    self.auth_cookies = response.cookies
                    _LOGGER.debug(f"{self.auth_cookies}")
                    if hasattr(self.web_session, "_cookie_jar"):
                        jar = getattr(self.web_session, "_cookie_jar")
                        jar.update_cookies(response.cookies)

            else:
                _LOGGER.warning(f"{response}")

    async def logout(self):
        """Logout function"""
        async with self.web_session.get(f"http://{self.hostname}/cgi/logout") as response:
            try:
                response.raise_for_status()
                content = await response.text()
                _LOGGER.info(f"LOGOUT status:{response.status} content: {content}")
            except Exception as exc:
                _LOGGER.warning(f"{exc}")

            self.auth_cookies = None

    async def read_value(self, tag: EcotouchTag):
        """Read a value from Tag"""
        res = await self.read_values([tag])
        if tag in res:
            return res[tag]
        return None

    async def read_values(self, tags: Sequence[EcotouchTag]):
        if self.auth_cookies is None:
            await self.login()

        """Async read values"""
        # create flat list of ecotouch tags to be read
        e_tags = list(set([etag for tag in tags for etag in tag.tags]))
        e_values, e_status = await self._read_tags(e_tags)

        result = {}
        if e_values is not None and len(e_values) > 0:
            for a_eco_tag in tags:
                try:
                    t_values = [e_values[a_tag] for a_tag in a_eco_tag.tags]
                    t_states = [e_status[a_tag] for a_tag in a_eco_tag.tags]
                    result[a_eco_tag] = {
                        "value": a_eco_tag.decode_function(a_eco_tag, t_values),
                        "status": t_states[0]
                    }

                    if a_eco_tag.translate and a_eco_tag.tags[0] in self.lang_map:
                        value_map = self.lang_map[a_eco_tag.tags[0]]
                        final_value = ""
                        temp_values = result[a_eco_tag]["value"]
                        for idx in range(len(temp_values)):
                            if temp_values[idx]:
                                final_value = final_value + ", " + str(value_map[idx])

                        # we need to trim the firsts initial added ', '
                        if len(final_value) > 0:
                            final_value = final_value[2:]

                        result[a_eco_tag]["value"] = final_value

                except KeyError:
                    _LOGGER.warning(
                        f"Key Error while read_values. EcoTag: {a_eco_tag} vals: {t_values} states: {t_states}")
                except Exception as other_exc:
                    _LOGGER.error(
                        f"Exception {other_exc} while read_values. EcoTag: {a_eco_tag} vals: {t_values} states: {t_states}",
                        other_exc
                    )

        return result

    #
    # reads a list of ecotouch tags
    #
    # self, tags: Sequence[EcotouchTag], results={}, results_status={}
    async def _read_tags(self, tags: Sequence[EcotouchTag], results=None, results_status=None):
        """async read tags"""
        # _LOGGER.warning(tags)
        if results is None:
            results = {}
        if results_status is None:
            results_status = {}

        while len(tags) > self.tags_per_request:
            results, results_status = await self._read_tags(tags[:self.tags_per_request], results, results_status)
            tags = tags[self.tags_per_request:]

        args = {}
        args["n"] = len(tags)
        for i in range(len(tags)):
            args[f"t{(i + 1)}"] = tags[i]

        # also the readTags have a timestamp in each request...
        args["_"] = str(int(round(datetime.now().timestamp() * 1000)))
        _LOGGER.info(f"going to request {args['n']} tags in a single call from waterkotte@{self.hostname}")
        async with self.web_session.get(f"http://{self.hostname}/cgi/readTags", params=args) as response:
            try:
                response.raise_for_status()
                if response.status == 200:

                    _LOGGER.debug(f"requested: {response.url}")
                    content = await response.text()
                    if content.startswith("#E_NEED_LOGIN"):
                        try:
                            await self.login()
                            return await self._read_tags(tags=tags, results=results, results_status=results_status)
                        except StatusException as status_exec:
                            _LOGGER.warning(f"StatusException (_read_tags) while trying to login: {status_exec}")
                            return None, None

                    if content.startswith("#E_TOO_MANY_USERS"):
                        return None

                    for tag in tags:
                        match = re.search(
                            rf"#{tag}\t(?P<status>[A-Z_]+)\n\d+\t(?P<value>\-?\d+)",
                            content,
                            re.MULTILINE,
                        )
                        if match is None:
                            match = re.search(
                                rf"#{tag}\tE_INACTIVETAG",
                                content,
                                re.MULTILINE,
                            )
                            # val_status = "E_INACTIVE"  # pylint: disable=possibly-unused-variable
                            if match is None:
                                _LOGGER.warning(f"Tag: '{tag}' not found in response!")
                                results_status[tag] = "E_NOTFOUND"
                            else:
                                # if val_status == "E_INACTIVE":
                                results_status[tag] = "E_INACTIVE"

                            results[tag] = None
                        else:
                            # results_status[tag] = "S_OK"
                            results_status[tag] = match.group("status")
                            results[tag] = match.group("value")

                else:
                    _LOGGER.warning(f"{response}")
            except Exception as exc:
                if response is not None and response.status == 500:
                    self.auth_cookies = None
                    await self.login()
                    return await self._read_tags(tags)
                else:
                    _LOGGER.warning(f"{exc}")

        return results, results_status

    async def write_value(self, tag, value):
        """Write a value"""
        return await self.write_values([(tag, value)])

    async def write_values(self, kv_pairs: Collection[Tuple[EcotouchTag, Any]]):
        if self.auth_cookies is None:
            await self.login()

        """Write values to Tag"""
        to_write = {}
        result = {}
        # we write only one EcotouchTag at the same time (but the EcotouchTag can consist of
        # multiple internal tag fields)
        for a_eco_tag, value in kv_pairs:  # pylint: disable=invalid-name
            if not a_eco_tag.writeable:
                raise InvalidValueException("tried to write to an readonly field")

            # converting the HA values to the final int or bools that the waterkotte understand
            a_eco_tag.encode_function(a_eco_tag, value, to_write)

            e_values, e_status = await self._write_tags(to_write.keys(), to_write.values())

            if e_values is not None and len(e_values) > 0:
                _LOGGER.info(
                    f"after _encode_tags of EcotouchTag {a_eco_tag} > raw-values: {e_values} states: {e_status}")

                all_ok = True
                for a_tag in e_status:
                    if e_status[a_tag] != "S_OK":
                        all_ok = False

                if all_ok:
                    str_vals = [e_values[a_tag] for a_tag in a_eco_tag.tags]
                    val = a_eco_tag.decode_function(a_eco_tag, str_vals)
                    if str(val) != str(value):
                        _LOGGER.error(
                            f"WRITE value does not match value that was READ: '{val}' (read) != '{value}' (write)")
                    else:
                        result[a_eco_tag] = {
                            "value": val,
                            # here we also take just the first status...
                            "status": e_status[a_eco_tag.tags[0]]
                        }
        return result

    #
    # writes <value> into the tag <tag>
    #
    async def _write_tags(self, tags: List[str], value: List[Any]):
        """write tag"""
        args = {}
        args["n"] = len(tags)
        args["returnValue"] = "true"
        args["rnd"] = str(int(round(datetime.now().timestamp() * 1000)))
        for i, tag in enumerate(tags):
            args[f"t{i + 1}"] = tag
            args[f"v{i + 1}"] = list(value)[i]

        results = {}
        results_status = {}
        # _LOGGER.info(f"requesting '{args}' [tags: {tags}, values: {value}]")

        async with self.web_session.get(f"http://{self.hostname}/cgi/writeTags", params=args) as response:
            try:
                response.raise_for_status()
                if response.status == 200:

                    content = await response.text()  # pylint: disable=invalid-name
                    if content.startswith("#E_NEED_LOGIN"):
                        try:
                            await self.login()
                            return await self._write_tags(tags=tags, value=value)
                        except StatusException as status_exec:
                            _LOGGER.warning(f"StatusException (_write_tags) while trying to login: {status_exec}")
                            return None
                    if content.startswith("#E_TOO_MANY_USERS"):
                        return None

                    ###
                    for tag in tags:
                        match = re.search(
                            rf"#{tag}\t(?P<status>[A-Z_]+)\n\d+\t(?P<value>\-?\d+)",
                            content,
                            re.MULTILINE
                        )
                        if match is None:
                            match = re.search(
                                rf"#{tag}\tE_INACTIVETAG",
                                content,
                                re.MULTILINE
                            )
                            # val_status = "E_INACTIVE"  # pylint: disable=possibly-unused-variable
                            if match is None:
                                _LOGGER.warning(f"Tag: '{tag}' not found in response!")
                                results_status[tag] = "E_NOTFOUND"
                            else:
                                # if val_status == "E_INACTIVE":
                                results_status[tag] = "E_INACTIVE"

                            results[tag] = None
                        else:
                            # results_status[tag] = "S_OK"
                            results_status[tag] = match.group("status")
                            results[tag] = match.group("value")


                else:
                    _LOGGER.warning(f"{response}")
            except Exception as exc:
                _LOGGER.warning(f"{exc}")

        return results, results_status


class EasyconBridge(EcotouchBridge):
    """Base Easycon Class, inherits from ecotouch"""

    async def login(self):  # pylint: disable=unused-argument
        """Login to Heat Pump (not needed for easycon)"""
        return

    async def logout(self):
        """Logout function (not needed for easycon)"""
        return

    # reads a list of ecotouch tags
    #
    async def _read_tags(self, tags: Sequence[EcotouchTag], results=None, results_status=None):
        """async read tags"""
        if results is None:
            results = {}
        if results_status is None:
            results_status = {}
        D = []  # pylint: disable=invalid-name
        I = []  # pylint: disable=invalid-name
        A = []  # pylint: disable=invalid-name
        for tag in tags:
            print(tag)
            # for entry in tag.tags:
            #     print(entry)
            if tag[0] == "D":
                D.append(int(tag[1:]))
            elif tag[0] == "I":
                I.append(int(tag[1:]))
            elif tag[0] == "A":
                A.append(int(tag[1:]))

        D.sort()
        I.sort()
        A.sort()

        query = ""
        if len(D) > 0:
            query += f"|D|{D[0]}|{D[len(D) - 1]}"
        if len(A) > 0:
            query += f"|A|{A[0]}|{A[len(A) - 1]}"
        if len(I) > 0:
            query += f"|I|{I[0]}|{I[len(I) - 1]}"
        # query="?" + query[1:]
        print(query)
        if query == "":
            return None, None

        async with self.web_session.get(f"http://{self.hostname}/config/xml.cgi?{query[1:]}") as response:
            try:
                response.raise_for_status()
                if response.status == 200:
                    try:
                        content = await response.text()  # pylint: disable=invalid-name
                        tree = ElemTree.fromstring(content)
                        root = tree[0]

                        for tagType in root:
                            for tag in tagType:
                                if int(tag[0].text) < 50:
                                    print(f"{tagType.tag[0]}{tag[0].text}={tag[1].text}")

                        # return None, None
                    except Exception as exc:
                        _LOGGER.debug(f"Response was: {content} caused {exc}")
                        raise Exception(f"Error in easycon.py parsing. Received: {content}")

                    for tag in tags:
                        if tag[0] == "D":
                            valType = "DIGITAL"
                        elif tag[0] == "I":
                            valType = "INTEGER"
                        elif tag[0] == "A":
                            valType = "ANALOG"
                        match = root.find(f".//{valType}/*/INDEX[.='{tag[1:]}']/../VALUE")
                        if match is None:
                            match = re.search(
                                # r"#%s\tE_INACTIVETAG" % tag,
                                f"#{tag}\tE_INACTIVETAG",
                                content,
                                re.MULTILINE,
                            )
                            # val_status = "E_INACTIVE"  # pylint: disable=possibly-unused-variable
                            # print("Tag: %s is inactive!", tag)
                            if match is None:
                                _LOGGER.warning(f"Tag: '{tag}' not found in response!")
                                results_status[tag] = "E_NOTFOUND"
                            else:
                                # if val_status == "E_INACTIVE":
                                results_status[tag] = "E_INACTIVE"

                            results[tag] = None
                        else:
                            results_status[tag] = "S_OK"
                            if valType == "ANALOG":
                                results[tag] = str(float(match.text) * 10.0)
                            else:
                                results[tag] = match.text
                if response.status == 404:
                    _LOGGER.debug(f"http 404 caused by requesting {response.url} - full: {response}")
                    raise Http404Exception(f"HTTP 404 {response.url}")
                else:
                    _LOGGER.warning(f"{response}")
            except Exception as exc:
                if response is not None and response.status == 404:
                    _LOGGER.debug(f"http 404 caused by requesting {response.url} - full: {response}")
                    raise Http404Exception(f"HTTP 404 {response.url}")
                else:
                    _LOGGER.warning(f"{exc}")

        return results, results_status

    async def _write_tag(self, tags: List[str], value: List[Any]):
        """write tag"""
        # for i in range(len(tags)):
        #    args[f"t{(i + 1)}"] = tags[i]
        # for i in range(len(tag.tags)):
        #     et_values[tag.tags[i]] = vals[i]
        # print(et_values)
        # http://192.168.0.193/config/query.cgi?var%7CI%7C1255%7C20%7Cvar%7CI%7C1256%7C01%7Cvar%7CI%7C1257%7C31%7Cvar%7CI%7C1258%7C01%7Cvar%7CI%7C1259%7C23%7C
        # var|I|1255|20|var|I|1256|01|var|I|1257|31|var|I|1258|01|var|I|1259|23|
        param = ""
        for i, tag in enumerate(tags):
            param += f"var|{tag[0].upper()}|{tag[1:]}|{list(value)[i]}|"

        results = {}
        resultsStatus = {}

        async with self.web_session.get(f"http://{self.hostname}/config/query.cgi?{param}") as response:
            try:
                response.raise_for_status()
                if response.status == 200:
                    content = await response.text()

                is_ok = content.find("Operation completed succesfully") > 0 or content.find(
                    "Operation completed successfully") > 0
                if is_ok and response.status == 200:

                    for i, tag in enumerate(tags):
                        resultsStatus[tag] = "S_OK"
                        results[tag] = list(value)[i]
                else:
                    _LOGGER.warning(f"{response}")
            except Exception as exc:
                _LOGGER.warning(f"{exc}")

            return results, resultsStatus
