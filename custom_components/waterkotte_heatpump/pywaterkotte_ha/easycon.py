""" Class to interact with Easycon system """
import xml.etree.ElementTree as ET
import logging

from custom_components.waterkotte_heatpump.pywaterkotte_ha.ecotouch import (  # pylint: disable=import-error
    EcotouchBridge,
    Sequence,
    EcotouchTag,
    aiohttp,
    re,
    List,
    Any,
)

_LOGGER: logging.Logger = logging.getLogger(__package__)


class EasyconBridge(EcotouchBridge):
    """Base Easycon Class, inherits from ecotouch"""

    async def login(
            self, username="waterkotte", password="waterkotte"
    ):  # pylint: disable=unused-argument
        """Login to Heat Pump (not needed for easycon)"""
        return

    async def logout(self):
        """Logout function (not needed for easycon)"""
        return

        #

    # reads a list of ecotouch tags
    #
    async def _read_tags(
            # self, tags: Sequence[EcotouchTag], results={}, results_status={}
            self,
            tags: Sequence[EcotouchTag],
            results=None,
            results_status=None,
    ):
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

        async with aiohttp.ClientSession(cookies=self.auth_cookies) as session:

            async with session.get(f"http://{self.hostname}/config/xml.cgi?{query[1:]}") as response:
                async with response:
                    if response.status == 200:
                        try:
                            r = await response.text()  # pylint: disable=invalid-name
                            tree = ET.fromstring(r)
                            root = tree[0]

                            for tagType in root:
                                for tag in tagType:
                                    if int(tag[0].text) < 50:
                                        print(f"{tagType.tag[0]}{tag[0].text}={tag[1].text}")

                            # return None, None
                        except Exception as exc:
                            _LOGGER.debug(f"Response was: {r} caused {exc}")
                            raise Exception(f"Error in easycon.py parsing. Received: {r}")

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
                                    r,
                                    re.MULTILINE,
                                )
                                # val_status = "E_INACTIVE"  # pylint: disable=possibly-unused-variable
                                # print("Tag: %s is inactive!", tag)
                                if match is None:
                                    # raise Exception(tag + " tag not found in response")
                                    _LOGGER.warning("Tag: %s not found in response!", tag)
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
                    elif response.status == 404:
                        _LOGGER.debug(f"http 404 caused by requesting {response.url} - full: {response}")
                        raise FileNotFoundError(f"HTTP 404 {response.url}")

        return results, results_status

    #
    # writes <value> into the tag <tag>
    #
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

        print(param)
        # args = {
        #     "n": 1,
        #     "returnValue": "true",
        #     "t1": tag,
        #     "v1": value,
        #     'rnd': str(datetime.timestamp(datetime.now()))
        # }
        # result = {}
        results = {}
        resultsStatus = {}
        async with aiohttp.ClientSession(cookies=self.auth_cookies) as session:

            async with session.get(
                    f"http://{self.hostname}/config/query.cgi?{param}"
            ) as resp:
                r = await resp.text()  # pylint: disable=invalid-name
                if r.find("Operation completed succesfully") > 0 and resp.status == 200:

                    for i, tag in enumerate(tags):
                        resultsStatus[tag] = "S_OK"
                        results[tag] = list(value)[i]

            return results, resultsStatus
