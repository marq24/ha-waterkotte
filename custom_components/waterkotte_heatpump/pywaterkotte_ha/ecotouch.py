""" ecotouch main module"""
import aiohttp
import re
import logging

from enum import Enum
from datetime import datetime

from typing import (
    Any,
    Sequence,
    Tuple,
    List,
    Collection
)

from custom_components.waterkotte_heatpump.pywaterkotte_ha import TagData, InvalidValueException

_LOGGER: logging.Logger = logging.getLogger(__package__)


class InvalidResponseException(Exception):
    """A InvalidResponseException."""

    # pass


class StatusException(Exception):
    """A Status Exception."""

    # pass


class TooManyUsersException(StatusException):
    """A TooManyUsers Exception."""

    # pass


class EcotouchTag(TagData, Enum):  # pylint: disable=function-redefined
    """EcotouchTag Class"""

    HOLIDAY_ENABLED = TagData(["D420"], writeable=True)
    HOLIDAY_START_TIME = TagData(
        ["I1254", "I1253", "I1252", "I1250", "I1251"],
        writeable=True,
        decode_function=TagData._decode_datetime,
        encode_function=TagData._encode_datetime,
    )
    HOLIDAY_END_TIME = TagData(
        ["I1259", "I1258", "I1257", "I1255", "I1256"],
        writeable=True,
        decode_function=TagData._decode_datetime,
        encode_function=TagData._encode_datetime,
    )
    TEMPERATURE_OUTSIDE = TagData(["A1"], "°C")
    TEMPERATURE_OUTSIDE_1H = TagData(["A2"], "°C")
    TEMPERATURE_OUTSIDE_24H = TagData(["A3"], "°C")
    TEMPERATURE_SOURCE_ENTRY = TagData(["A4"], "°C")
    TEMPERATURE_SOURCE_EXIT = TagData(["A5"], "°C")
    TEMPERATURE_EVAPORATION = TagData(["A6"], "°C")
    TEMPERATURE_SUCTION_LINE = TagData(["A7"], "°C")
    PRESSURE_EVAPORATION = TagData(["A8"], "bar")
    TEMPERATURE_RETURN_SETPOINT = TagData(["A10"], "°C")
    TEMPERATURE_RETURN = TagData(["A11"], "°C")
    TEMPERATURE_FLOW = TagData(["A12"], "°C")
    TEMPERATURE_CONDENSATION = TagData(["A13"], "°C")
    TEMPERATURE_BUBBLEPOINT = TagData(["A14"], "°C")
    PRESSURE_CONDENSATION = TagData(["A15"], "bar")
    TEMPERATURE_BUFFERTANK = TagData(["A16"], "°C")
    TEMPERATURE_ROOM = TagData(["A17"], "°C")
    TEMPERATURE_ROOM_1H = TagData(["A18"], "°C")
    # TODO - CHECK... [currently no Sensors based on these tags]
    TEMPERATURE_ROOM_TARGET = TagData(["A100"], "°C", writeable=True)
    ROOM_INFLUENCE = TagData(["A101"], "%", writeable=True)

    TEMPERATURE_SOLAR = TagData(["A21"], "°C")
    TEMPERATURE_SOLAR_EXIT = TagData(["A22"], "°C")
    POSITION_EXPANSION_VALVE = TagData(["A23"], "")
    SUCTION_GAS_OVERHEATING = TagData(["A24"], "")

    POWER_ELECTRIC = TagData(["A25"], "kW")
    POWER_HEATING = TagData(["A26"], "kW")
    POWER_COOLING = TagData(["A27"], "kW")
    COP_HEATING = TagData(["A28"], "")
    COP_COOLING = TagData(["A29"], "")

    # ENERGY-YEAR-BALANCE
    COP_HEATPUMP_YEAR = TagData(["A460"], "")
    COP_TOTAL_SYSTEM_YEAR = TagData(["A461"], "")
    COP_HEATING_YEAR = TagData(["A695"])
    COP_HOT_WATER_YEAR = TagData(["A697"])

    ENERGY_CONSUMPTION_TOTAL_YEAR = TagData(["A450", "A451"], "kWh")
    COMPRESSOR_ELECTRIC_CONSUMPTION_YEAR = TagData(["A444", "A445"], "kWh")
    SOURCEPUMP_ELECTRIC_CONSUMPTION_YEAR = TagData(["A446", "A447"], "kWh")
    ELECTRICAL_HEATER_ELECTRIC_CONSUMPTION_YEAR = TagData(["A448", "A449"], "kWh")
    ENERGY_PRODUCTION_TOTAL_YEAR = TagData(["A458", "A459"], "kWh")
    HEATING_ENERGY_PRODUCTION_YEAR = TagData(["A452", "A453"], "kWh")
    HOT_WATER_ENERGY_PRODUCTION_YEAR = TagData(["A454", "A455"], "kWh")
    POOL_ENERGY_PRODUCTION_YEAR = TagData(["A456", "A457"], "kWh")
    COOLING_ENERGY_YEAR = TagData(["A462", "A463"], "kWh")

    # The LAST12M values for ENERGY_CONSUMPTION_TOTAL (also the individual values for compressor, sourcepump & e-heater
    # will be calculated based on values for each month (and will be summarized in the FE))
    # The same applies to the ENERGY_PRODUCTION_TOTAL (with the individual values for heating, hot_water & pool)
    COP_TOTAL_SYSTEM_LAST12M = TagData(["A435"])
    COOLING_ENERGY_LAST12M = TagData(["A436"], "kWh")

    # Temperature stuff
    TEMPERATURE_HEATING = TagData(["A30"], "°C")
    TEMPERATURE_HEATING_DEMAND = TagData(["A31"], "°C")
    TEMPERATURE_HEATING_ADJUST = TagData(["I263"], "K", writeable=True)
    TEMPERATURE_HEATING_HYSTERESIS = TagData(["A61"], "K", writeable=True)
    TEMPERATURE_HEATING_PV_CHANGE = TagData(["A682"], "K", writeable=True)
    TEMPERATURE_HEATING_HC_OUTDOOR_1H = TagData(["A90"], "°C")
    TEMPERATURE_HEATING_HC_LIMIT = TagData(["A93"], "°C", writeable=True)
    TEMPERATURE_HEATING_HC_TARGET = TagData(["A94"], "°C", writeable=True)
    TEMPERATURE_HEATING_HC_OUTDOOR_NORM = TagData(["A91"], "°C", writeable=True)
    TEMPERATURE_HEATING_HC_NORM = TagData(["A92"], "°C", writeable=True)
    TEMPERATURE_HEATING_HC_RESULT = TagData(["A96"], "°C")
    TEMPERATURE_HEATING_ANTIFREEZE = TagData(["A1231"], "°C", writeable=True)
    TEMPERATURE_HEATING_SETPOINTLIMIT_MAX = TagData(["A95"], "°C", writeable=True)
    TEMPERATURE_HEATING_SETPOINTLIMIT_MIN = TagData(["A104"], "°C", writeable=True)
    TEMPERATURE_HEATING_POWLIMIT_MAX = TagData(["A504"], "%", writeable=True)
    TEMPERATURE_HEATING_POWLIMIT_MIN = TagData(["A505"], "%", writeable=True)
    TEMPERATURE_HEATING_SGREADY_STATUS4 = TagData(["A967"], "°C", writeable=True)

    # TEMPERATURE_HEATING_BUFFERTANK_ROOM_SETPOINT = TagData(["A413"], "°C", writeable=True)

    TEMPERATURE_HEATING_MODE = TagData(["I265"], writeable=True, decode_function=TagData._decode_heat_mode,
                                       encode_function=TagData._encode_heat_mode)
    # this A32 value is not visible in the GUI - and IMHO (marq24) there should
    # be no way to set the heating temperature directly - use the values of the
    # 'TEMPERATURE_HEATING_HC' instead (HC = HeatCurve)
    TEMPERATURE_HEATING_SETPOINT = TagData(["A32"], "°C", writeable=True)
    # same as A32 ?!
    TEMPERATURE_HEATING_SETPOINT_FOR_SOLAR = TagData(["A1710"], "°C", writeable=True)

    TEMPERATURE_COOLING = TagData(["A33"], "°C")
    TEMPERATURE_COOLING_DEMAND = TagData(["A34"], "°C")
    TEMPERATURE_COOLING_SETPOINT = TagData(["A109"], "°C", writeable=True)
    TEMPERATURE_COOLING_OUTDOOR_LIMIT = TagData(["A108"], "°C", writeable=True)
    TEMPERATURE_COOLING_HYSTERESIS = TagData(["A107"], "K", writeable=True)
    TEMPERATURE_COOLING_PV_CHANGE = TagData(["A683"], "K", writeable=True)

    TEMPERATURE_WATER = TagData(["A19"], "°C")
    TEMPERATURE_WATER_DEMAND = TagData(["A37"], "°C")
    TEMPERATURE_WATER_SETPOINT = TagData(["A38"], "°C", writeable=True)
    TEMPERATURE_WATER_HYSTERESIS = TagData(["A139"], "K", writeable=True)
    TEMPERATURE_WATER_PV_CHANGE = TagData(["A684"], "K", writeable=True)
    TEMPERATURE_WATER_DISINFECTION = TagData(["A168"], "°C", writeable=True)
    SCHEDULE_WATER_DISINFECTION_START_TIME = TagData(["I505", "I506"],
                                                     writeable=True,
                                                     decode_function=TagData._decode_time_hhmm,
                                                     encode_function=TagData._encode_time_hhmm,
                                                     )
    # SCHEDULE_WATER_DISINFECTION_START_HOUR = TagData(["I505"], "", writeable=True)
    # SCHEDULE_WATER_DISINFECTION_START_MINUTE = TagData(["I506"], "", writeable=True)
    SCHEDULE_WATER_DISINFECTION_DURATION = TagData(["I507"], "h", writeable=True)
    SCHEDULE_WATER_DISINFECTION_1MO = TagData(["D153"], "", writeable=True)
    SCHEDULE_WATER_DISINFECTION_2TU = TagData(["D154"], "", writeable=True)
    SCHEDULE_WATER_DISINFECTION_3WE = TagData(["D155"], "", writeable=True)
    SCHEDULE_WATER_DISINFECTION_4TH = TagData(["D156"], "", writeable=True)
    SCHEDULE_WATER_DISINFECTION_5FR = TagData(["D157"], "", writeable=True)
    SCHEDULE_WATER_DISINFECTION_6SA = TagData(["D158"], "", writeable=True)
    SCHEDULE_WATER_DISINFECTION_7SU = TagData(["D159"], "", writeable=True)

    TEMPERATURE_WATER_SETPOINT_FOR_SOLAR = TagData(["A169"], "°C", writeable=True)
    # Changeover temperature to extern heating when exceeding T hot water
    # Umschalttemperatur ext. Waermeerzeuger bei Ueberschreitung der T Warmwasser
    TEMPERATURE_WATER_CHANGEOVER_EXT_HOTWATER = TagData(["A1019"], "°C", writeable=True)
    # Changeover temperature to extern heating when exceeding T flow
    # Umschalttemperatur ext. Waermeerzeuger bei Ueberschreitung der T Vorlauf
    TEMPERATURE_WATER_CHANGEOVER_EXT_FLOW = TagData(["A1249"], "°C", writeable=True)
    TEMPERATURE_WATER_POWLIMIT_MAX = TagData(["A171"], "%", writeable=True)
    TEMPERATURE_WATER_POWLIMIT_MIN = TagData(["A172"], "%", writeable=True)

    TEMPERATURE_POOL = TagData(["A20"], "°C")
    TEMPERATURE_POOL_DEMAND = TagData(["A40"], "°C")
    TEMPERATURE_POOL_SETPOINT = TagData(["A41"], "°C", writeable=True)
    TEMPERATURE_POOL_HYSTERESIS = TagData(["A174"], "K", writeable=True)
    TEMPERATURE_POOL_PV_CHANGE = TagData(["A685"], "K", writeable=True)
    TEMPERATURE_POOL_HC_OUTDOOR_1H = TagData(["A746"], "°C")
    TEMPERATURE_POOL_HC_LIMIT = TagData(["A749"], "°C", writeable=True)
    TEMPERATURE_POOL_HC_TARGET = TagData(["A750"], "°C", writeable=True)
    TEMPERATURE_POOL_HC_OUTDOOR_NORM = TagData(["A747"], "°C", writeable=True)
    TEMPERATURE_POOL_HC_NORM = TagData(["A748"], "°C", writeable=True)
    TEMPERATURE_POOL_HC_RESULT = TagData(["A752"], "°C")

    TEMPERATURE_MIX1 = TagData(["A44"], "°C")
    TEMPERATURE_MIX1_DEMAND = TagData(["A45"], "°C")
    TEMPERATURE_MIX1_ADJUST = TagData(["I776"], "K", writeable=True)
    TEMPERATURE_MIX1_PV_CHANGE = TagData(["A1094"], "K", writeable=True)
    TEMPERATURE_MIX1_PERCENT = TagData(["A510"], "%")
    TEMPERATURE_MIX1_HC_LIMIT = TagData(["A276"], "°C", writeable=True)
    TEMPERATURE_MIX1_HC_TARGET = TagData(["A277"], "°C", writeable=True)
    TEMPERATURE_MIX1_HC_OUTDOOR_NORM = TagData(["A274"], "°C", writeable=True)
    TEMPERATURE_MIX1_HC_HEATING_NORM = TagData(["A275"], "°C", writeable=True)
    TEMPERATURE_MIX1_HC_MAX = TagData(["A278"], "°C", writeable=True)

    TEMPERATURE_MIX2 = TagData(["A46"], "°C")
    TEMPERATURE_MIX2_DEMAND = TagData(["A47"], "°C")
    TEMPERATURE_MIX2_ADJUST = TagData(["I896"], "K", writeable=True)
    TEMPERATURE_MIX2_PV_CHANGE = TagData(["A1095"], "K", writeable=True)
    TEMPERATURE_MIX2_PERCENT = TagData(["A512"], "%")
    TEMPERATURE_MIX2_HC_LIMIT = TagData(["A322"], "°C", writeable=True)
    TEMPERATURE_MIX2_HC_TARGET = TagData(["A323"], "°C", writeable=True)
    TEMPERATURE_MIX2_HC_OUTDOOR_NORM = TagData(["A320"], "°C", writeable=True)
    TEMPERATURE_MIX2_HC_HEATING_NORM = TagData(["A321"], "°C", writeable=True)
    TEMPERATURE_MIX2_HC_MAX = TagData(["A324"], "°C", writeable=True)

    TEMPERATURE_MIX3 = TagData(["A48"], "°C")
    TEMPERATURE_MIX3_DEMAND = TagData(["A49"], "°C")
    TEMPERATURE_MIX3_ADJUST = TagData(["I1017"], "K", writeable=True)
    TEMPERATURE_MIX3_PV_CHANGE = TagData(["A1096"], "K", writeable=True)
    TEMPERATURE_MIX3_PERCENT = TagData(["A514"], "%")
    TEMPERATURE_MIX3_HC_LIMIT = TagData(["A368"], "°C", writeable=True)
    TEMPERATURE_MIX3_HC_TARGET = TagData(["A369"], "°C", writeable=True)
    TEMPERATURE_MIX3_HC_OUTDOOR_NORM = TagData(["A366"], "°C", writeable=True)
    TEMPERATURE_MIX3_HC_HEATING_NORM = TagData(["A367"], "°C", writeable=True)
    TEMPERATURE_MIX3_HC_MAX = TagData(["A370"], "°C", writeable=True)

    # no information found in <host>/easycon/js/dictionary.js
    # COMPRESSOR_POWER = TagData(["A50"], "?°C")
    PERCENT_HEAT_CIRC_PUMP = TagData(["A51"], "%")
    PERCENT_SOURCE_PUMP = TagData(["A52"], "%")
    # A58 is listed as 'Power compressor' in <host>/easycon/js/dictionary.js
    # even if this value will not be displayed in the Waterkotte GUI - looks
    # like that this is really the same as the other two values (A51 & A52)
    # just a percentage value (from 0.0 - 100.0)
    PERCENT_COMPRESSOR = TagData(["A58"], "%")

    # just found... Druckgastemperatur
    TEMPERATURE_DISCHARGE = TagData(["A1462"], "°C")

    # implement https://github.com/marq24/ha-waterkotte/issues/3
    PRESSURE_WATER = TagData(["A1669"], "bar")

    # I1264 -> Heizstab Leistung?! -> 6000

    # keep but not found in Waterkotte GUI
    TEMPERATURE_COLLECTOR = TagData(["A42"], "°C")  # aktuelle Temperatur Kollektor
    TEMPERATURE_FLOW2 = TagData(["A43"], "°C")  # aktuelle Temperatur Vorlauf

    VERSION_CONTROLLER = TagData(["I1", "I2"], writeable=False, decode_function=TagData._decode_ro_fw)
    # VERSION_CONTROLLER_BUILD = TagData(["I2"])
    VERSION_BIOS = TagData(["I3"], writeable=False, decode_function=TagData._decode_ro_bios)
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
    ENABLE_HEATING = TagData(["I30"], decode_function=TagData._decode_state, encode_function=TagData._encode_state,
                             writeable=True)
    ENABLE_COOLING = TagData(["I31"], decode_function=TagData._decode_state, encode_function=TagData._encode_state,
                             writeable=True)
    ENABLE_WARMWATER = TagData(["I32"], decode_function=TagData._decode_state, encode_function=TagData._encode_state,
                               writeable=True)
    ENABLE_POOL = TagData(["I33"], decode_function=TagData._decode_state, encode_function=TagData._encode_state,
                          writeable=True)
    ENABLE_PV = TagData(["I41"], decode_function=TagData._decode_state, encode_function=TagData._encode_state,
                        writeable=True)

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
    STATUS_HEATING = TagData(["I137"], decode_function=TagData._decode_ro_status)
    STATUS_COOLING = TagData(["I138"], decode_function=TagData._decode_ro_status)
    STATUS_WATER = TagData(["I139"], decode_function=TagData._decode_ro_status)
    INFO_SERIES = TagData(["I105"], decode_function=TagData._decode_ro_series)
    INFO_ID = TagData(["I110"], decode_function=TagData._decode_ro_id)
    INFO_SERIAL = TagData(["I114", "I115"], writeable=False, decode_function=TagData._decode_ro_sn)
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

    STATE_BLOCKING_TIME = TagData(["D71"])
    STATE_TEST_RUN = TagData(["D581"])

    # SERVICE_HEATING = TagData(["D251"])
    # SERVICE_COOLING = TagData(["D252"])
    # SERVICE_WATER = TagData(["D117"])
    # SERVICE_HEATING_D23 = TagData(["D23"])
    # SERVICE_HEATING_D24 = TagData(["D24"])
    # SERVICE_WATER_D118 = TagData(["D118"])
    # SERVICE_OPMODE = TagData(["I136"])
    # RAW_D430 = TagData(["D430"])  # animation
    # RAW_D28 = TagData(["D28"])  # ?QE
    # RAW_D879 = TagData(["D879"])  # ?RMH
    # MODE_HEATING_PUMP = TagData(["A522"])
    # MODE_HEATING = TagData(["A530"])
    # MODE_HEATING_EXTERNAL = TagData(["A528"])
    # MODE_COOLING = TagData(["A532"])
    # MODE_WATER = TagData(["A534"])
    # MODE_POOL = TagData(["A536"])
    # MODE_SOLAR = TagData(["A538"])

    # found on the "extended" Tab in the Waterkotte WebGui
    # (all values can be read/write) - no clue about the unit yet
    # reading the values always returned '0' -> so I guess they have
    # no use for us?!
    # ENERGY_THERMAL_WORK_1 = TagData("I1923")
    # ENERGY_THERMAL_WORK_2 = TagData("I1924")
    # ENERGY_COOLING = TagData("I1925")
    # ENERGY_HEATING = TagData("I1926")
    # ENERGY_HOT_WATER = TagData("I1927")
    # ENERGY_POOL_HEATER = TagData("I1928")
    # ENERGY_COMPRESSOR = TagData("I1929")
    # ENERGY_HEAT_SOURCE_PUMP = TagData("I1930")
    # ENERGY_EXTERNAL_HEATER = TagData("I1931")

    def __hash__(self) -> int:
        return hash(self.name)


#
# Class to control Waterkotte Ecotouch heatpumps.
#
class EcotouchBridge:
    """Ecotouch Class"""

    auth_cookies = None

    def __init__(self, host, tagsPerRequest: int = 10):
        self.hostname = host
        self.username = "waterkotte"
        self.password = "waterkotte"
        self.tagsPerRequest = min(tagsPerRequest, 75)

    # extracts statuscode from response
    def get_status_response(self, r):  # pylint: disable=invalid-name
        """get_status_response"""
        match = re.search(r"^#([A-Z_]+)", r, re.MULTILINE)
        if match is None:
            raise InvalidResponseException("Invalid reply. Status could not be parsed")
        return match.group(1)

    # performs a login. Has to be called before any other method.
    async def login(self, username="waterkotte", password="waterkotte"):
        """Login to Heat Pump"""
        _LOGGER.info(f"login to waterkotte host {self.hostname}")
        args = {"username": username, "password": password}
        self.username = username
        self.password = password
        async with aiohttp.ClientSession() as session:
            response = await session.get(f"http://{self.hostname}/cgi/login", params=args)
            async with response:
                assert response.status == 200
                content = await response.text()

                tc = content.replace('\n', '<nl>')
                tc = tc.replace('\r', '<cr>')
                _LOGGER.info(f"LOGIN status:{response.status} response: {tc}")

                parsed_response = self.get_status_response(content)
                if parsed_response != "S_OK":
                    if parsed_response.startswith("E_TOO_MANY_USERS"):
                        raise TooManyUsersException("TOO MANY USERS")
                    else:
                        raise StatusException(f"Error while LOGIN: status: {parsed_response}")
                self.auth_cookies = response.cookies

    async def logout(self):
        """Logout function"""
        async with aiohttp.ClientSession() as session:
            response = await session.get(f"http://{self.hostname}/cgi/logout")
            async with response:
                content = await response.text()
                # tc = content.replace("\n", "<nl>").replace("\r", "<cr>")
                _LOGGER.info(f"LOGOUT status:{response.status} content: {content}")
                self.auth_cookies = None

    async def read_value(self, tag: EcotouchTag):
        """Read a value from Tag"""
        res = await self.read_values([tag])
        if tag in res:
            return res[tag]
        return None

    async def read_values(self, tags: Sequence[EcotouchTag]):
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

        while len(tags) > self.tagsPerRequest:
            results, results_status = await self._read_tags(tags[:self.tagsPerRequest], results, results_status)
            tags = tags[self.tagsPerRequest:]

        args = {}
        args["n"] = len(tags)
        for i in range(len(tags)):
            args[f"t{(i + 1)}"] = tags[i]

        _LOGGER.info(f"going to request {args['n']} tags in a single call from waterkotte@{self.hostname}")

        async with aiohttp.ClientSession(cookies=self.auth_cookies) as session:
            async with session.get(f"http://{self.hostname}/cgi/readTags", params=args) as resp:
                response = await resp.text()
                if response.startswith("#E_NEED_LOGIN"):
                    try:
                        await self.login(self.username, self.password)
                        return await self._read_tags(tags=tags, results=results, results_status=results_status)
                    except StatusException as status_exec:
                        _LOGGER.warning(f"StatusException (_read_tags) while trying to login {status_exec}")
                        return None, None

                if response.startswith("#E_TOO_MANY_USERS"):
                    return None

                for tag in tags:
                    match = re.search(
                        f"#{tag}\t(?P<status>[A-Z_]+)\n\d+\t(?P<value>\-?\d+)",
                        # pylint: disable=anomalous-backslash-in-string
                        response,
                        re.MULTILINE,
                    )
                    if match is None:
                        match = re.search(
                            # r"#%s\tE_INACTIVETAG" % tag,
                            f"#{tag}\tE_INACTIVETAG",
                            response,
                            re.MULTILINE,
                        )
                        # val_status = "E_INACTIVE"  # pylint: disable=possibly-unused-variable
                        if match is None:
                            # raise Exception(tag + " tag not found in response")
                            _LOGGER.warning("Tag: %s not found in response!", tag)
                            results_status[tag] = "E_NOTFOUND"
                        else:
                            # if val_status == "E_INACTIVE":
                            results_status[tag] = "E_INACTIVE"

                        results[tag] = None
                    else:
                        results_status[tag] = "E_OK"
                        results[tag] = match.group("value")

        return results, results_status

    async def write_value(self, tag, value):
        """Write a value"""
        return await self.write_values([(tag, value)])

    async def write_values(self, kv_pairs: Collection[Tuple[EcotouchTag, Any]]):
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
                    if e_status[a_tag] != "E_OK":
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
        args["rnd"] = str(datetime.timestamp(datetime.now()))
        # for i in range(len(tags)):
        #    args[f"t{(i + 1)}"] = tags[i]
        # for i in range(len(tag.tags)):
        #     et_values[tag.tags[i]] = vals[i]
        for i, tag in enumerate(tags):
            args[f"t{i + 1}"] = tag
            args[f"v{i + 1}"] = list(value)[i]

        # args = {
        #     "n": 1,
        #     "returnValue": "true",
        #     "t1": tag,
        #     "v1": value,
        #     'rnd': str(datetime.timestamp(datetime.now()))
        # }
        # result = {}
        results = {}
        results_status = {}
        # _LOGGER.info(f"requesting '{args}' [tags: {tags}, values: {value}]")

        async with aiohttp.ClientSession(cookies=self.auth_cookies) as session:
            async with session.get(f"http://{self.hostname}/cgi/writeTags", params=args) as resp:
                response = await resp.text()  # pylint: disable=invalid-name
                if response.startswith("#E_NEED_LOGIN"):
                    try:
                        await self.login(self.username, self.password)
                        return await self._write_tags(tags=tags, value=value)
                    except StatusException as status_exec:
                        _LOGGER.warning(f"StatusException (_write_tags) while trying to login {status_exec}")
                        return None
                if response.startswith("#E_TOO_MANY_USERS"):
                    return None

                ###
                for tag in tags:
                    match = re.search(
                        f"#{tag}\t(?P<status>[A-Z_]+)\n\d+\t(?P<value>\-?\d+)",
                        # pylint: disable=anomalous-backslash-in-string
                        response,
                        re.MULTILINE,
                    )
                    if match is None:
                        match = re.search(
                            # r"#%s\tE_INACTIVETAG" % tag,
                            f"#{tag}\tE_INACTIVETAG",
                            response,
                            re.MULTILINE,
                        )
                        # val_status = "E_INACTIVE"  # pylint: disable=possibly-unused-variable
                        if match is None:
                            # raise Exception(tag + " tag not found in response")
                            _LOGGER.warning("Tag: %s not found in response!", tag)
                            results_status[tag] = "E_NOTFOUND"
                        else:
                            # if val_status == "E_INACTIVE":
                            results_status[tag] = "E_INACTIVE"

                        results[tag] = None
                    else:
                        results_status[tag] = "E_OK"
                        results[tag] = match.group("value")

            return results, results_status
