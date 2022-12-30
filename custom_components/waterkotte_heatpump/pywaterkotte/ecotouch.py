""" pyecotouch main module"""
from typing import Any, Callable, Collection, NamedTuple, Sequence, Tuple  # , List

# from unittest import case
import re

from enum import Enum
from datetime import datetime, timedelta
import requests


# import random
import aiohttp

MAX_NO_TAGS = 10


class StatusException(Exception):
    """A Status Exception."""
    # pass


class InvalidResponseException(Exception):
    """A InvalidResponseException."""
    # pass


class InvalidValueException(Exception):
    """A InvalidValueException."""
    # pass


class EcotouchTag:
    """A Dummy Class."""
    # pass


# default method that reads a value based on a single tag
def _parse_value_default(self: EcotouchTag, vals, bitnum=None, *other_args):  # pylint: disable=unused-argument,keyword-arg-before-vararg
    assert len(self.tags) == 1
    ecotouch_tag = self.tags[0]
    assert ecotouch_tag[0] in ["A", "I", "D"]

    if ecotouch_tag not in vals:
        return None

    val = vals[ecotouch_tag]

    if ecotouch_tag[0] == "A":
        return float(val) / 10.0
    if ecotouch_tag[0] == "I":
        if bitnum is None:
            return int(val)
        else:
            return (int(val) & (1 << bitnum)) > 0

    if ecotouch_tag[0] == "D":
        if val == "1":
            return True
        elif val == "0":
            return False
        else:
            raise InvalidValueException(
                # "%s is not a valid value for %s" % (val, ecotouch_tag)
                f"{val} is not a valid value for {ecotouch_tag}"
            )


def _write_value_default(self, value, et_values):
    assert len(self.tags) == 1
    ecotouch_tag = self.tags[0]
    assert ecotouch_tag[0] in ["A", "I", "D"]

    if ecotouch_tag[0] == "I":
        assert isinstance(value, int)
        et_values[ecotouch_tag] = str(value)
    elif ecotouch_tag[0] == "D":
        assert isinstance(value, bool)
        et_values[ecotouch_tag] = "1" if value else "0"
    elif ecotouch_tag[0] == "A":
        assert isinstance(value, float)
        et_values[ecotouch_tag] = str(int(value * 10))


def _parse_time(self, e_vals, *other_args):  # pylint: disable=unused-argument
    vals = [int(e_vals[tag]) for tag in self.tags]
    vals[0] = vals[0] + 2000
    next_day = False
    if vals[3] == 24:
        vals[3] = 0
        next_day = True

    dt = datetime(*vals)
    return dt + timedelta(days=1) if next_day else dt


def _parse_state(self, value, *other_args):  # pylint: disable=unused-argument
    assert len(self.tags) == 1
    ecotouch_tag = self.tags[0]
    # assert isinstance(value[ecotouch_tag],int)
    if value[ecotouch_tag] == "0":
        return "off"
    elif value[ecotouch_tag] == "1":
        return "auto"
    elif value[ecotouch_tag] == "2":
        return "manual"
    else:
        return "Error"


def _write_time(tag, value, et_values):
    assert isinstance(value, datetime)
    vals = [
        str(val)
        for val in [
            value.year % 100,
            value.month,
            value.day,
            value.hour,
            value.minute,
            value.second,
        ]
    ]
    for i in range(len(tag.tags)):
        et_values[tag.tags[i]] = vals[i]


class TagData(NamedTuple):
    """ TagData Class """
    tags: Collection[str]
    unit: str = None
    writeable: bool = False
    read_function: Callable = _parse_value_default
    write_function: Callable = _write_value_default
    bit: int = None


class EcotouchTag(TagData, Enum):  # pylint: disable=function-redefined
    """ EcotouchTag Class """
    TEMPERATURE_OUTSIDE = TagData(["A1"], "°C")
    HOLIDAY_ENABLED = TagData(["D420"], writeable=True)
    HOLIDAY_START_TIME = TagData(
        ["I1254", "I1253", "I1252", "I1250", "I1251"],
        writeable=True,
        read_function=_parse_time,
        write_function=_write_time,
    )
    HOLIDAY_END_TIME = TagData(
        ["I1259", "I1258", "I1257", "I1255", "I1256"],
        writeable=True,
        read_function=_parse_time,
        write_function=_write_time,
    )
    TEMPERATURE_OUTSIDE_1H = TagData(["A2"], "°C")
    TEMPERATURE_OUTSIDE_24H = TagData(["A3"], "°C")
    TEMPERATURE_SOURCE_IN = TagData(["A4"], "°C")
    TEMPERATURE_SOURCE_OUT = TagData(["A5"], "°C")
    TEMPERATURE_EVAPORATION = TagData(["A6"], "°C")
    TEMPERATURE_SUCTION = TagData(["A7"], "°C")
    PRESSURE_EVAPORATION = TagData(["A8"], "bar")
    TEMPERATURE_RETURN_SET = TagData(["A10"], "°C")
    TEMPERATURE_RETURN = TagData(["A11"], "°C")
    TEMPERATURE_FLOW = TagData(["A12"], "°C")
    TEMPERATURE_CONDENSATION = TagData(["A14"], "°C")
    PRESSURE_CONDENSATION = TagData(["A15"], "bar")
    TEMPERATURE_STORAGE = TagData(["A16"], "°C")
    TEMPERATURE_ROOM = TagData(["A17"], "°C")
    TEMPERATURE_ROOM_1H = TagData(["A18"], "°C")
    TEMPERATURE_WATER = TagData(["A19"], "°C")
    TEMPERATURE_POOL = TagData(["A20"], "°C")
    TEMPERATURE_SOLAR = TagData(["A21"], "°C")
    TEMPERATURE_SOLAR_FLOW = TagData(["A22"], "°C")
    POSITION_EXPANSION_VALVE = TagData(["A23"], "?°C")
    POWER_COMPRESSOR = TagData(["A25"], "?°C")
    POWER_HEATING = TagData(["A26"], "?°C")
    POWER_COOLING = TagData(["A27"], "?°C")
    COP_HEATING = TagData(["A28"], "?°C")
    COP_COOLING = TagData(["A29"], "?°C")
    TEMPERATURE_HEATING_RETURN = TagData(["A30"], "°C")
    TEMPERATURE_HEATING_SET = TagData(["A31"], "°C")
    TEMPERATURE_HEATING_SET2 = TagData(["A32"], "°C")
    TEMPERATURE_COOLING_RETURN = TagData(["A33"], "°C")
    TEMPERATURE_COOLING_SET = TagData(["A34"], "°C")
    TEMPERATURE_COOLING_SET2 = TagData(["A35"], "°C")
    TEMPERATURE_WATER_SETPOINT = TagData(["A37"], "°C", writeable=True)
    TEMPERATURE_WATER_SETPOINT2 = TagData(["A38"], "°C", writeable=True)
    TEMPERATURE_POOL_SETPOINT = TagData(["A40"], "°C", writeable=True)
    TEMPERATURE_POOL_SETPOINT2 = TagData(["A41"], "°C", writeable=True)
    COMPRESSOR_POWER = TagData(["A50"], "?°C")
    PERCENT_HEAT_CIRC_PUMP = TagData(["A51"], "%")
    PERCENT_SOURCE_PUMP = TagData(["A52"], "%")
    PERCENT_COMPRESSOR = TagData(["A58"], "%")
    HYSTERESIS_HEATING = TagData(["A61"], "?")
    TEMPERATURE2_OUTSIDE_1H = TagData(["A90"], "°C")
    NVI_NORM_AUSSEN = TagData(["A91"], "?")
    NVI_HEIZKREIS_NORM = TagData(["A92"], "?")
    NVI_T_HEIZGRENZE = TagData(["A93"], "?°C")
    NVI_T_HEIZGRENZE_SOLL = TagData(["A94"], "?°C")
    MAX_VL_TEMP = TagData(["A95"], "°C")
    TEMP_SET_0_DEG = TagData(["A97"], "°C")
    COOL_ENABLE_TEMP = TagData(["A108"], "°C")
    NVI_SOLL_KUEHLEN = TagData(["A109"], "°C")
    TEMPCHANGE_HEATING_PV = TagData(["A682"], "°C")
    TEMPCHANGE_COOLING_PV = TagData(["A683"], "°C")
    TEMPCHANGE_WARMWATER_PV = TagData(["A684"], "°C")
    TEMPCHANGE_POOL_PV = TagData(["A685"], "°C")
    VERSION_CONTROLLER = TagData(["I1"])
    VERSION_CONTROLLER_BUILD = TagData(["I2"])
    VERSION_BIOS = TagData(["I3"])
    DATE_DAY = TagData(["I5"])
    DATE_MONTH = TagData(["I6"])
    DATE_YEAR = TagData(["I7"])
    TIME_HOUR = TagData(["I8"])
    TIME_MINUTE = TagData(["I9"])
    OPERATING_HOURS_COMPRESSOR_1 = TagData(["I10"])
    OPERATING_HOURS_COMPRESSOR_2 = TagData(["I14"])
    OPERATING_HOURS_CIRCULATION_PUMP = TagData(["I18"])
    OPERATING_HOURS_SOURCE_PUMP = TagData(["I20"])
    OPERATING_HOURS_SOLAR = TagData(["I22"])
    ENABLE_HEATING = TagData(["I30"], read_function=_parse_state)
    ENABLE_COOLING = TagData(["I31"], read_function=_parse_state)
    ENABLE_WARMWATER = TagData(["I32"], read_function=_parse_state)
    ENABLE_POOL = TagData(["I33"], read_function=_parse_state)
    ENABLE_PV = TagData(["I41"], read_function=_parse_state)
    STATE_SOURCEPUMP = TagData(["I51"], bit=0)
    STATE_HEATINGPUMP = TagData(["I51"], bit=1)
    STATE_EVD = TagData(["I51"], bit=2)
    STATE_COMPRESSOR = TagData(["I51"], bit=3)
    STATE_COMPRESSOR2 = TagData(["I51"], bit=4)
    STATE_EXTERNAL_HEATER = TagData(["I51"], bit=5)
    STATE_ALARM = TagData(["I51"], bit=6)
    STATE_COOLING = TagData(["I51"], bit=7)
    STATE_WATER = TagData(["I51"], bit=8)
    STATE_POOL = TagData(["I51"], bit=9)
    STATE_SOLAR = TagData(["I51"], bit=10)
    STATE_COOLING4WAY = TagData(["I51"], bit=11)
    ALARM = TagData(["I52"])
    INTERRUPTIONS = TagData(["I53"])
    STATE_SERVICE = TagData(["I135"])
    STATUS_HEATING = TagData(["I37"])
    STATUS_COOLING = TagData(["I38"])
    STATUS_WATER = TagData(["I39"])
    ADAPT_HEATING = TagData(["I263"], writeable=True)
    MANUAL_HEATINGPUMP = TagData(["I1270"])
    MANUAL_SOURCEPUMP = TagData(["I1281"])
    MANUAL_SOLARPUMP1 = TagData(["I1287"])
    MANUAL_SOLARPUMP2 = TagData(["I1289"])
    MANUAL_TANKPUMP = TagData(["I1291"])
    MANUAL_VALVE = TagData(["I1293"])
    MANUAL_POOLVALVE = TagData(["I1295"])
    MANUAL_COOLVALVE = TagData(["I1297"])
    MANUAL_4WAYVALVE = TagData(["I1299"])
    MANUAL_MULTIEXT = TagData(["I1319"])

    def __hash__(self) -> int:
        return hash(self.name)


#
# Class to control Waterkotte Ecotouch heatpumps.
#
class Ecotouch:
    """ Ecotouch Class """
    auth_cookies = None

    def __init__(self, host):
        self.hostname = host
        self.username = 'waterkotte'
        self.password = 'waterkotte'

    # extracts statuscode from response
    def get_status_response(self, r):
        """ get_status_response """
        match = re.search(r"^#([A-Z_]+)", r, re.MULTILINE)
        if match is None:
            raise InvalidResponseException(
                "Ungültige Antwort. Konnte Status nicht auslesen."
            )
        return match.group(1)

    # performs a login. Has to be called before any other method.
    async def login(self, username="waterkotte", password="waterkotte"):
        """ Login to Heat Pump """
        args = {"username": username, "password": password}
        self.username = username
        self.password = password
        # r = requests.get("http://%s/cgi/login" % self.hostname, params=args)
        async with aiohttp.ClientSession() as session:
            # r = await session.get("http://%s/cgi/login" % self.hostname, params=args)
            r = await session.get(f"http://{self.hostname}/cgi/login", params=args)
            async with r:
                assert r.status == 200
                # r = await resp.text()

                print(await r.text())
                print(r.status)
                if self.get_status_response(await r.text()) != "S_OK":
                    raise StatusException(
                        f"Fehler beim Login: Status:{self.get_status_response(await r.text())}"
                    )
                self.auth_cookies = r.cookies

    async def read_value(self, tag: EcotouchTag):
        """ Read a value from Tag """
        res = await self.read_values([tag])
        if tag in res:
            return res[tag]
        return None

    def write_values(self, kv_pairs: Collection[Tuple[EcotouchTag, Any]]):
        """ Write values to Tag """
        to_write = {}
        for k, v in kv_pairs:
            if not k.writeable:
                raise InvalidValueException("tried to write to an readonly field")
            k.write_function(k, v, to_write)

        for k, v in to_write.items():
            self._write_tag(k, v)

    def write_value(self, tag, value):
        """ Write a value """
        self.write_values([(tag, value)])

    async def read_values(self, tags: Sequence[EcotouchTag]):
        """ Async read values """
        # create flat list of ecotouch tags to be read
        e_tags = list(set([etag for tag in tags for etag in tag.tags]))
        e_values, e_status = await self._read_tags(e_tags)

        result = {}
        # result_status = {}
        for tag in tags:
            # tag2=tag._replace(status=e_status[tag.tags[0]])
            # tag.status[0]=e_status[tag.tags[0]]
            # if len(tag.status)==0:
            #     tag.status.append(e_status[tag.tags[0]])
            # else:
            #     tag.status.clear()
            #     tag.status.append(e_status[tag.tags[0]] + str(random.randint(1,10)))
            # result_status[tag] = e_status[tag.tags[0]] + str(random.randint(1,10))
            # tag.status=e_status[tag.tags[0]]
            e_inactive = False
            for tag_status in tag.tags:
                if e_status[tag_status] == "E_INACTIVE":
                    e_inactive = True
            if e_inactive is False:
                val = tag.read_function(tag, e_values, tag.bit)
            else:
                val = None
            result[tag] = {"value": val, "status": e_status[tag_status]}  # pylint: disable=undefined-loop-variable
        return result

    #
    # reads a list of ecotouch tags
    #
    async def _read_tags(
        # self, tags: Sequence[EcotouchTag], results={}, results_status={}
        self, tags: Sequence[EcotouchTag], results=None, results_status=None
    ):
        """ async read tags """
        if results is None:
            results = {}
        if results_status is None:
            results_status = {}

        while len(tags) > MAX_NO_TAGS:
            results, results_status = await self._read_tags(
                tags[:MAX_NO_TAGS], results, results_status)
            tags = tags[MAX_NO_TAGS:]
        # if len(tags) > 0:
        #     results, results_status = await self._read_tags(
        #         tags, results, results_status)

        # if len(tags) > MAX_NO_TAGS:
        #     results, results_status = await self._read_tags(
        #         tags[MAX_NO_TAGS:], results, results_status
        #     )
        # tags = tags[:MAX_NO_TAGS]

        args = {}
        args["n"] = len(tags)
        for i in range(len(tags)):
            args[f"t{(i + 1)}"] = tags[i]
        # r = requests.get(
        #     "http://%s/cgi/readTags" % self.hostname,
        #     params=args,
        #     cookies=self.auth_cookies,
        # )
        async with aiohttp.ClientSession(cookies=self.auth_cookies) as session:

            async with session.get(
                f"http://{self.hostname}/cgi/readTags", params=args
            ) as resp:
                r = await resp.text()
                # print(r)
                if r == "#E_NEED_LOGIN\n":
                    res = await self.login(self.username, self.password)  # pylint: disable=possibly-unused-variable
                    return
                for tag in tags:
                    match = re.search(
                        r"#%s\t(?P<status>[A-Z_]+)\n\d+\t(?P<value>\-?\d+)" % tag,
                        # r.text,
                        r,
                        re.MULTILINE,
                    )
                    if match is None:
                        match = re.search(
                            r"#%s\tE_INACTIVETAG" % tag,
                            # r.text,
                            r,
                            re.MULTILINE,
                        )
                        val_status = "E_INACTIVE"  # pylint: disable=possibly-unused-variable
                        # print("Tag: %s is inactive!", tag)
                        if match is None:
                            raise Exception(tag + " tag not found in response")

                    if "val_status" in locals():
                        results_status[tag] = "E_INACTIVE"
                        results[tag] = None
                    else:
                        results_status[tag] = "E_OK"
                        results[tag] = match.group("value")
                        # tag.status.append="E_OK"
                        # val_status = val_status if 'val_status' in locals() else match.group("status")
                        # tag = tag._replace(status=val_status)

                    # results[tag] = val_str

                    # results[tag].status = val_status
        return results, results_status

    #
    # writes <value> into the tag <tag>
    #
    def _write_tag(self, tag: EcotouchTag, value):
        """ write tag """
        args = {"n": 1, "returnValue": "true", "t1": tag, "v1": value}
        r = requests.get(
            f"http://{self.hostname}/cgi/writeTags",
            params=args,
            cookies=self.auth_cookies,
        )
        val_str = re.search(r"(?:^\d+\t)(\-?\d+)", r.text, re.MULTILINE).group(1)
        return val_str
