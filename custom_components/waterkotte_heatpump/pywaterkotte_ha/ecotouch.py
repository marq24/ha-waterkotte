""" ecotouch main module"""
import logging
import math
import struct
from datetime import timedelta, time

from enum import Enum

from datetime import datetime

from typing import (
    NamedTuple,
    Callable,
    List,
    Collection
)

from custom_components.waterkotte_heatpump.pywaterkotte_ha.const import (
    SERIES,
    SYSTEM_IDS,
    SIX_STEPS_MODES
)

from custom_components.waterkotte_heatpump.pywaterkotte_ha.error import (
    InvalidValueException,
)

_LOGGER: logging.Logger = logging.getLogger(__package__)


class DTag(NamedTuple):

    def _decode_value_default(self, str_vals: List[str]):
        return self.__decode_value_default(str_vals, 10.0)

    def _decode_value_analog(self, str_vals: List[str]):
        return self.__decode_value_default(str_vals, -1)

    def __decode_value_default(self, str_vals: List[str], factor: float):
        first_val = str_vals[0]
        if first_val is None:
            # do not check any further if for what ever reason the first value of the str_vals is None
            return None

        first_tag = self.tags[0]
        assert first_tag[0] in ["A", "I", "D"]

        if first_tag[0] == "A":
            if len(self.tags) == 1:
                # SIM VENT OperatingHour Sensors...
                # if self.tags[0] == "A4498":
                #    return float('180.000000')
                # if self.tags[0] == "A4504":
                #    return float('19')

                if factor > -1:
                    return float(first_val) / factor
                else:
                    return float(first_val)
            else:
                i_vals = [int(xxl) & 0xFFFF for xxl in str_vals]
                hex_string = f"{i_vals[0]:04x}{i_vals[1]:04x}"
                return struct.unpack("!f", bytes.fromhex(hex_string))[0]

        else:
            assert len(self.tags) == 1
            if first_tag[0] == "I":
                # single bit field
                if self.bit is not None:
                    return (int(first_val) & (1 << self.bit)) > 0

                # a bit array?
                elif self.bits is not None:
                    ret = [False] * len(self.bits)
                    for idx in range(len(self.bits)):
                        ret[idx] = (int(first_val) & (1 << self.bits[idx])) > 0
                    # _LOGGER.debug(f"BITS: {first_tag} ({first_val}) -> {ret}")
                    return ret

                # default implementation
                else:
                    return int(first_val)

            elif first_tag[0] == "D":
                if first_val == "1":
                    return True
                elif first_val == "0":
                    return False
            else:
                raise InvalidValueException(
                    # "%s is not a valid value for %s" % (val, ecotouch_tag)
                    f"{first_val} is not a valid value for {first_tag}"
                )

        return None

    def _encode_value_default(self, value, encoded_values):
        self.__encode_value_default(value, encoded_values, 10)

    def _encode_value_analog(self, value, encoded_values):
        self.__encode_value_default(value, encoded_values, -1)

    def __encode_value_default(self, value, encoded_values, factor: int):
        assert len(self.tags) == 1
        ecotouch_tag = self.tags[0]
        assert ecotouch_tag[0] in ["A", "I", "D"]

        if ecotouch_tag[0] == "I":
            assert isinstance(value, int)
            encoded_values[ecotouch_tag] = str(value)
        elif ecotouch_tag[0] == "D":
            assert isinstance(value, bool)
            encoded_values[ecotouch_tag] = "1" if value else "0"
        elif ecotouch_tag[0] == "A":
            assert isinstance(value, float)
            if factor > -1:
                encoded_values[ecotouch_tag] = str(int(value * factor))
            else:
                encoded_values[ecotouch_tag] = str(float(value))

    def _decode_datetime(self, str_vals: List[str]):
        int_vals = list(map(int, str_vals))
        int_vals[0] = int_vals[0] + 2000
        next_day = False
        if int_vals[3] == 24:
            int_vals[3] = 0
            next_day = True

        dt_val = datetime(*int_vals)
        return dt_val + timedelta(days=1) if next_day else dt_val

    def _encode_datetime(self, value, encoded_values):
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
        # check if result is the same
        # for i in range(len(tag.tags)):
        #     et_values[tag.tags[i]] = vals[i]
        for i, tags in enumerate(self.tags):
            encoded_values[tags] = vals[i]

    def _decode_time_hhmm(self, str_vals: List[str]):
        int_vals = list(map(int, str_vals))
        dt = time(hour=int_vals[0], minute=int_vals[1])
        return dt

    def _encode_time_hhmm(self, value, encoded_values):
        assert isinstance(value, time)
        vals = [
            str(val)
            for val in [
                value.hour,
                value.minute,
            ]
        ]
        for i, tags in enumerate(self.tags):
            encoded_values[tags] = vals[i]

    def _decode_state(self, str_vals: List[str]):
        assert len(self.tags) == 1
        if str_vals[0] == "0":
            return "off"
        elif str_vals[0] == "1":
            return "auto"
        elif str_vals[0] == "2":
            return "manual"
        else:
            return "Error"

    def _encode_state(self, value, encoded_values):
        assert len(self.tags) == 1
        ecotouch_tag = self.tags[0]
        assert ecotouch_tag[0] in ["I"]
        if value == "off":
            encoded_values[ecotouch_tag] = "0"
        elif value == "auto":
            encoded_values[ecotouch_tag] = "1"
        elif value == "manual":
            encoded_values[ecotouch_tag] = "2"

    def _decode_six_steps_mode(self, str_vals: List[str]):
        assert len(self.tags) == 1
        int_val = int(str_vals[0])
        if 0 <= int_val <= len(SIX_STEPS_MODES):
            return SIX_STEPS_MODES[int_val]
        else:
            return "Error"

    def _encode_six_steps_mode(self, value, encoded_values):
        assert len(self.tags) == 1
        ecotouch_tag = self.tags[0]
        assert ecotouch_tag[0] in ["I"]
        index = self._get_key_from_value(SIX_STEPS_MODES, value)
        if index is not None:
            encoded_values[ecotouch_tag] = str(index)

    @staticmethod
    def _get_key_from_value(a_dict: dict, value_to_find):
        # a very simple "find first key" of dict method...
        keys = [k for k, v in a_dict.items() if v == value_to_find]
        if keys:
            return keys[0]
        return None

    def _decode_status(self, str_vals: List[str]):
        assert len(self.tags) == 1
        if str_vals[0] == "0":
            return "off"
        elif str_vals[0] == "1":
            return "on"
        elif str_vals[0] == "2":
            return "disabled"
        else:
            return "Error"

    def _encode_status(self, value, encoded_values):
        assert len(self.tags) == 1
        ecotouch_tag = self.tags[0]
        assert ecotouch_tag[0] in ["I"]
        if value == "off":
            encoded_values[ecotouch_tag] = "0"
        elif value == "on":
            encoded_values[ecotouch_tag] = "1"
        elif value == "disabled":
            encoded_values[ecotouch_tag] = "2"

    def _decode_ro_series(self, str_vals: List[str]):
        return SERIES[int(str_vals[0])] if str_vals[0] else ""

    def _decode_ro_id(self, str_vals: List[str]):
        assert len(self.tags) == 1
        return SYSTEM_IDS[int(str_vals[0])] if str_vals[0] else ""

    def _decode_ro_bios(self, str_vals: List[str]):
        assert len(self.tags) == 1
        str_val = str_vals[0]
        return f"{str_val[:-2]}.{str_val[-2:]}"

    def _decode_ro_fw(self, str_vals: List[str]):
        assert len(self.tags) == 2
        str_val1 = str_vals[0]
        str_val2 = str_vals[1]
        # str fw2 = f"{str_val1[:-4]:0>2}.{str_val1[-4:-2]}.{str_val1[-2:]}"
        return f"0{str_val1[0]}.{str_val1[1:3]}.{str_val1[3:]}-{str_val2}"

    def _decode_ro_sn(self, str_vals: List[str]):
        assert len(self.tags) == 2
        sn1 = int(str_vals[0])
        sn2 = int(str_vals[1])
        s1 = "WE" if math.floor(sn1 / 1000) > 0 else "00"  # pylint: disable=invalid-name
        s2 = (sn1 - 1000 if math.floor(sn1 / 1000) > 0 else sn1)  # pylint: disable=invalid-name
        s2 = "0" + str(s2) if s2 < 10 else s2  # pylint: disable=invalid-name
        return str(s1) + str(s2) + str(sn2)

    def _decode_year(self, str_vals: List[str]):
        assert len(self.tags) == 1
        return int(str_vals[0]) + 2000

    tags: Collection[str]
    unit: str = None
    writeable: bool = False
    decode_f: Callable = _decode_value_default
    encode_f: Callable = _encode_value_default
    bit: int = None
    bits: list[int] = None
    translate: bool = False


class EcotouchTag(DTag, Enum):
    """EcotouchTag Class"""

    HOLIDAY_ENABLED = DTag(["D420"], writeable=True)
    HOLIDAY_START_TIME = DTag(
        ["I1254", "I1253", "I1252", "I1250", "I1251"], writeable=True,
        decode_f=DTag._decode_datetime, encode_f=DTag._encode_datetime)
    HOLIDAY_END_TIME = DTag(
        ["I1259", "I1258", "I1257", "I1255", "I1256"], writeable=True,
        decode_f=DTag._decode_datetime, encode_f=DTag._encode_datetime)
    TEMPERATURE_OUTSIDE = DTag(["A1"], "°C")
    TEMPERATURE_OUTSIDE_1H = DTag(["A2"], "°C")
    TEMPERATURE_OUTSIDE_24H = DTag(["A3"], "°C")
    TEMPERATURE_SOURCE_ENTRY = DTag(["A4"], "°C")
    TEMPERATURE_SOURCE_EXIT = DTag(["A5"], "°C")
    TEMPERATURE_EVAPORATION = DTag(["A6"], "°C")
    TEMPERATURE_SUCTION_LINE = DTag(["A7"], "°C")
    PRESSURE_EVAPORATION = DTag(["A8"], "bar")
    TEMPERATURE_RETURN_SETPOINT = DTag(["A10"], "°C")
    TEMPERATURE_RETURN = DTag(["A11"], "°C")
    TEMPERATURE_FLOW = DTag(["A12"], "°C")
    TEMPERATURE_CONDENSATION = DTag(["A13"], "°C")
    TEMPERATURE_BUBBLEPOINT = DTag(["A14"], "°C")
    PRESSURE_CONDENSATION = DTag(["A15"], "bar")
    TEMPERATURE_BUFFERTANK = DTag(["A16"], "°C")
    TEMPERATURE_ROOM = DTag(["A17"], "°C")
    TEMPERATURE_ROOM_1H = DTag(["A18"], "°C")
    # TODO - CHECK... [currently no Sensors based on these tags]
    TEMPERATURE_ROOM_TARGET = DTag(["A100"], "°C", writeable=True)
    ROOM_INFLUENCE = DTag(["A101"], "%", writeable=True)

    TEMPERATURE_SOLAR = DTag(["A21"], "°C")
    TEMPERATURE_SOLAR_EXIT = DTag(["A22"], "°C")
    POSITION_EXPANSION_VALVE = DTag(["A23"], "")
    SUCTION_GAS_OVERHEATING = DTag(["A24"], "")

    POWER_ELECTRIC = DTag(["A25"], "kW")
    POWER_HEATING = DTag(["A26"], "kW")
    POWER_COOLING = DTag(["A27"], "kW")
    COP_HEATING = DTag(["A28"], "")
    COP_COOLING = DTag(["A29"], "")

    # ENERGY-YEAR-BALANCE
    COP_HEATPUMP_YEAR = DTag(["A460"], "")  # HEATPUMP_COP
    COP_HEATPUMP_ACTUAL_YEAR_INFO = DTag(["I1261"], decode_f=DTag._decode_year)  # HEATPUMP_COP_YEAR
    COP_TOTAL_SYSTEM_YEAR = DTag(["A461"], "")
    COP_HEATING_YEAR = DTag(["A695"])
    COP_HOT_WATER_YEAR = DTag(["A697"])

    ENERGY_CONSUMPTION_TOTAL_YEAR = DTag(["A450", "A451"], "kWh")
    COMPRESSOR_ELECTRIC_CONSUMPTION_YEAR = DTag(["A444", "A445"], "kWh")  # ANUAL_CONSUMPTION_COMPRESSOR
    SOURCEPUMP_ELECTRIC_CONSUMPTION_YEAR = DTag(["A446", "A447"], "kWh")  # ANUAL_CONSUMPTION_SOURCEPUMP
    ELECTRICAL_HEATER_ELECTRIC_CONSUMPTION_YEAR = DTag(["A448", "A449"], "kWh")  # ANUAL_CONSUMPTION_EXTERNALHEATER
    ENERGY_PRODUCTION_TOTAL_YEAR = DTag(["A458", "A459"], "kWh")
    HEATING_ENERGY_PRODUCTION_YEAR = DTag(["A452", "A453"], "kWh")  # ANUAL_CONSUMPTION_HEATING
    HOT_WATER_ENERGY_PRODUCTION_YEAR = DTag(["A454", "A455"], "kWh")  # ANUAL_CONSUMPTION_WATER
    POOL_ENERGY_PRODUCTION_YEAR = DTag(["A456", "A457"], "kWh")  # ANUAL_CONSUMPTION_POOL
    COOLING_ENERGY_YEAR = DTag(["A462", "A463"], "kWh")

    # The LAST12M values for ENERGY_CONSUMPTION_TOTAL (also the individual values for compressor, sourcepump & e-heater
    # will be calculated based on values for each month (and will be summarized in the FE))
    # The same applies to the ENERGY_PRODUCTION_TOTAL (with the individual values for heating, hot_water & pool)
    COP_TOTAL_SYSTEM_LAST12M = DTag(["A435"])
    COOLING_ENERGY_LAST12M = DTag(["A436"], "kWh")

    ENG_CONSUMPTION_COMPRESSOR01 = DTag(["A782"])
    ENG_CONSUMPTION_COMPRESSOR02 = DTag(["A783"])
    ENG_CONSUMPTION_COMPRESSOR03 = DTag(["A784"])
    ENG_CONSUMPTION_COMPRESSOR04 = DTag(["A785"])
    ENG_CONSUMPTION_COMPRESSOR05 = DTag(["A786"])
    ENG_CONSUMPTION_COMPRESSOR06 = DTag(["A787"])
    ENG_CONSUMPTION_COMPRESSOR07 = DTag(["A788"])
    ENG_CONSUMPTION_COMPRESSOR08 = DTag(["A789"])
    ENG_CONSUMPTION_COMPRESSOR09 = DTag(["A790"])
    ENG_CONSUMPTION_COMPRESSOR10 = DTag(["A791"])
    ENG_CONSUMPTION_COMPRESSOR11 = DTag(["A792"])
    ENG_CONSUMPTION_COMPRESSOR12 = DTag(["A793"])

    ENG_CONSUMPTION_SOURCEPUMP01 = DTag(["A794"])
    ENG_CONSUMPTION_SOURCEPUMP02 = DTag(["A795"])
    ENG_CONSUMPTION_SOURCEPUMP03 = DTag(["A796"])
    ENG_CONSUMPTION_SOURCEPUMP04 = DTag(["A797"])
    ENG_CONSUMPTION_SOURCEPUMP05 = DTag(["A798"])
    ENG_CONSUMPTION_SOURCEPUMP06 = DTag(["A799"])
    ENG_CONSUMPTION_SOURCEPUMP07 = DTag(["A800"])
    ENG_CONSUMPTION_SOURCEPUMP08 = DTag(["A802"])
    ENG_CONSUMPTION_SOURCEPUMP09 = DTag(["A804"])
    ENG_CONSUMPTION_SOURCEPUMP10 = DTag(["A805"])
    ENG_CONSUMPTION_SOURCEPUMP11 = DTag(["A806"])
    ENG_CONSUMPTION_SOURCEPUMP12 = DTag(["A807"])

    # Docs say it should start at 806 for external heater but there is an overlapp to source pump
    ENG_CONSUMPTION_EXTERNALHEATER01 = DTag(["A808"])
    ENG_CONSUMPTION_EXTERNALHEATER02 = DTag(["A809"])
    ENG_CONSUMPTION_EXTERNALHEATER03 = DTag(["A810"])
    ENG_CONSUMPTION_EXTERNALHEATER04 = DTag(["A811"])
    ENG_CONSUMPTION_EXTERNALHEATER05 = DTag(["A812"])
    ENG_CONSUMPTION_EXTERNALHEATER06 = DTag(["A813"])
    ENG_CONSUMPTION_EXTERNALHEATER07 = DTag(["A814"])
    ENG_CONSUMPTION_EXTERNALHEATER08 = DTag(["A815"])
    ENG_CONSUMPTION_EXTERNALHEATER09 = DTag(["A816"])
    ENG_CONSUMPTION_EXTERNALHEATER10 = DTag(["A817"])
    ENG_CONSUMPTION_EXTERNALHEATER11 = DTag(["A818"])
    ENG_CONSUMPTION_EXTERNALHEATER12 = DTag(["A819"])

    ENG_PRODUCTION_HEATING01 = DTag(["A830"])
    ENG_PRODUCTION_HEATING02 = DTag(["A831"])
    ENG_PRODUCTION_HEATING03 = DTag(["A832"])
    ENG_PRODUCTION_HEATING04 = DTag(["A833"])
    ENG_PRODUCTION_HEATING05 = DTag(["A834"])
    ENG_PRODUCTION_HEATING06 = DTag(["A835"])
    ENG_PRODUCTION_HEATING07 = DTag(["A836"])
    ENG_PRODUCTION_HEATING08 = DTag(["A837"])
    ENG_PRODUCTION_HEATING09 = DTag(["A838"])
    ENG_PRODUCTION_HEATING10 = DTag(["A839"])
    ENG_PRODUCTION_HEATING11 = DTag(["A840"])
    ENG_PRODUCTION_HEATING12 = DTag(["A841"])

    ENG_PRODUCTION_WARMWATER01 = DTag(["A842"])
    ENG_PRODUCTION_WARMWATER02 = DTag(["A843"])
    ENG_PRODUCTION_WARMWATER03 = DTag(["A844"])
    ENG_PRODUCTION_WARMWATER04 = DTag(["A845"])
    ENG_PRODUCTION_WARMWATER05 = DTag(["A846"])
    ENG_PRODUCTION_WARMWATER06 = DTag(["A847"])
    ENG_PRODUCTION_WARMWATER07 = DTag(["A848"])
    ENG_PRODUCTION_WARMWATER08 = DTag(["A849"])
    ENG_PRODUCTION_WARMWATER09 = DTag(["A850"])
    ENG_PRODUCTION_WARMWATER10 = DTag(["A851"])
    ENG_PRODUCTION_WARMWATER11 = DTag(["A852"])
    ENG_PRODUCTION_WARMWATER12 = DTag(["A853"])

    ENG_PRODUCTION_POOL01 = DTag(["A854"])
    ENG_PRODUCTION_POOL02 = DTag(["A855"])
    ENG_PRODUCTION_POOL03 = DTag(["A856"])
    ENG_PRODUCTION_POOL04 = DTag(["A857"])
    ENG_PRODUCTION_POOL05 = DTag(["A858"])
    ENG_PRODUCTION_POOL06 = DTag(["A859"])
    ENG_PRODUCTION_POOL07 = DTag(["A860"])
    ENG_PRODUCTION_POOL08 = DTag(["A861"])
    ENG_PRODUCTION_POOL09 = DTag(["A862"])
    ENG_PRODUCTION_POOL10 = DTag(["A863"])
    ENG_PRODUCTION_POOL11 = DTag(["A864"])
    ENG_PRODUCTION_POOL12 = DTag(["A865"])

    ENG_HEATPUMP_COP_MONTH01 = DTag(["A924"])
    ENG_HEATPUMP_COP_MONTH02 = DTag(["A925"])
    ENG_HEATPUMP_COP_MONTH03 = DTag(["A926"])
    ENG_HEATPUMP_COP_MONTH04 = DTag(["A927"])
    ENG_HEATPUMP_COP_MONTH05 = DTag(["A928"])
    ENG_HEATPUMP_COP_MONTH06 = DTag(["A929"])
    ENG_HEATPUMP_COP_MONTH07 = DTag(["A930"])
    ENG_HEATPUMP_COP_MONTH08 = DTag(["A930"])
    ENG_HEATPUMP_COP_MONTH09 = DTag(["A931"])
    ENG_HEATPUMP_COP_MONTH10 = DTag(["A932"])
    ENG_HEATPUMP_COP_MONTH11 = DTag(["A933"])
    ENG_HEATPUMP_COP_MONTH12 = DTag(["A934"])

    # Temperature stuff
    TEMPERATURE_HEATING = DTag(["A30"], "°C")
    TEMPERATURE_HEATING_DEMAND = DTag(["A31"], "°C")
    TEMPERATURE_HEATING_ADJUST = DTag(["I263"], "K", writeable=True)
    TEMPERATURE_HEATING_HYSTERESIS = DTag(["A61"], "K", writeable=True)
    TEMPERATURE_HEATING_PV_CHANGE = DTag(["A682"], "K", writeable=True)
    TEMPERATURE_HEATING_HC_OUTDOOR_1H = DTag(["A90"], "°C")
    TEMPERATURE_HEATING_HC_LIMIT = DTag(["A93"], "°C", writeable=True)
    TEMPERATURE_HEATING_HC_TARGET = DTag(["A94"], "°C", writeable=True)
    TEMPERATURE_HEATING_HC_OUTDOOR_NORM = DTag(["A91"], "°C", writeable=True)
    TEMPERATURE_HEATING_HC_NORM = DTag(["A92"], "°C", writeable=True)
    TEMPERATURE_HEATING_HC_RESULT = DTag(["A96"], "°C")
    TEMPERATURE_HEATING_ANTIFREEZE = DTag(["A1231"], "°C", writeable=True)
    TEMPERATURE_HEATING_SETPOINTLIMIT_MAX = DTag(["A95"], "°C", writeable=True)
    TEMPERATURE_HEATING_SETPOINTLIMIT_MIN = DTag(["A104"], "°C", writeable=True)
    TEMPERATURE_HEATING_POWLIMIT_MAX = DTag(["A504"], "%", writeable=True)
    TEMPERATURE_HEATING_POWLIMIT_MIN = DTag(["A505"], "%", writeable=True)
    TEMPERATURE_HEATING_SGREADY_STATUS4 = DTag(["A967"], "°C", writeable=True)

    # TEMPERATURE_HEATING_BUFFERTANK_ROOM_SETPOINT = TagData(["A413"], "°C", writeable=True)

    TEMPERATURE_HEATING_MODE = DTag(
        ["I265"], writeable=True, decode_f=DTag._decode_six_steps_mode, encode_f=DTag._encode_six_steps_mode
    )
    # this A32 value is not visible in the GUI - and IMHO (marq24) there should
    # be no way to set the heating temperature directly - use the values of the
    # 'TEMPERATURE_HEATING_HC' instead (HC = HeatCurve)
    TEMPERATURE_HEATING_SETPOINT = DTag(["A32"], "°C", writeable=True)
    # same as A32 ?!
    TEMPERATURE_HEATING_SETPOINT_FOR_SOLAR = DTag(["A1710"], "°C", writeable=True)

    TEMPERATURE_COOLING = DTag(["A33"], "°C")
    TEMPERATURE_COOLING_DEMAND = DTag(["A34"], "°C")
    TEMPERATURE_COOLING_SETPOINT = DTag(["A109"], "°C", writeable=True)
    TEMPERATURE_COOLING_OUTDOOR_LIMIT = DTag(["A108"], "°C", writeable=True)
    TEMPERATURE_COOLING_HYSTERESIS = DTag(["A107"], "K", writeable=True)
    TEMPERATURE_COOLING_PV_CHANGE = DTag(["A683"], "K", writeable=True)

    TEMPERATURE_WATER = DTag(["A19"], "°C")
    TEMPERATURE_WATER_DEMAND = DTag(["A37"], "°C")
    TEMPERATURE_WATER_SETPOINT = DTag(["A38"], "°C", writeable=True)
    TEMPERATURE_WATER_HYSTERESIS = DTag(["A139"], "K", writeable=True)
    TEMPERATURE_WATER_PV_CHANGE = DTag(["A684"], "K", writeable=True)
    TEMPERATURE_WATER_DISINFECTION = DTag(["A168"], "°C", writeable=True)
    SCHEDULE_WATER_DISINFECTION_START_TIME = DTag(
        ["I505", "I506"], writeable=True, decode_f=DTag._decode_time_hhmm, encode_f=DTag._encode_time_hhmm)
    # SCHEDULE_WATER_DISINFECTION_START_HOUR = TagData(["I505"], "", writeable=True)
    # SCHEDULE_WATER_DISINFECTION_START_MINUTE = TagData(["I506"], "", writeable=True)
    SCHEDULE_WATER_DISINFECTION_DURATION = DTag(["I507"], "h", writeable=True)
    SCHEDULE_WATER_DISINFECTION_1MO = DTag(["D153"], "", writeable=True)
    SCHEDULE_WATER_DISINFECTION_2TU = DTag(["D154"], "", writeable=True)
    SCHEDULE_WATER_DISINFECTION_3WE = DTag(["D155"], "", writeable=True)
    SCHEDULE_WATER_DISINFECTION_4TH = DTag(["D156"], "", writeable=True)
    SCHEDULE_WATER_DISINFECTION_5FR = DTag(["D157"], "", writeable=True)
    SCHEDULE_WATER_DISINFECTION_6SA = DTag(["D158"], "", writeable=True)
    SCHEDULE_WATER_DISINFECTION_7SU = DTag(["D159"], "", writeable=True)

    TEMPERATURE_WATER_SETPOINT_FOR_SOLAR = DTag(["A169"], "°C", writeable=True)
    # Changeover temperature to extern heating when exceeding T hot water
    # Umschalttemperatur ext. Waermeerzeuger bei Ueberschreitung der T Warmwasser
    TEMPERATURE_WATER_CHANGEOVER_EXT_HOTWATER = DTag(["A1019"], "°C", writeable=True)
    # Changeover temperature to extern heating when exceeding T flow
    # Umschalttemperatur ext. Waermeerzeuger bei Ueberschreitung der T Vorlauf
    TEMPERATURE_WATER_CHANGEOVER_EXT_FLOW = DTag(["A1249"], "°C", writeable=True)
    TEMPERATURE_WATER_POWLIMIT_MAX = DTag(["A171"], "%", writeable=True)
    TEMPERATURE_WATER_POWLIMIT_MIN = DTag(["A172"], "%", writeable=True)

    TEMPERATURE_POOL = DTag(["A20"], "°C")
    TEMPERATURE_POOL_DEMAND = DTag(["A40"], "°C")
    TEMPERATURE_POOL_SETPOINT = DTag(["A41"], "°C", writeable=True)
    TEMPERATURE_POOL_HYSTERESIS = DTag(["A174"], "K", writeable=True)
    TEMPERATURE_POOL_PV_CHANGE = DTag(["A685"], "K", writeable=True)
    TEMPERATURE_POOL_HC_OUTDOOR_1H = DTag(["A746"], "°C")
    TEMPERATURE_POOL_HC_LIMIT = DTag(["A749"], "°C", writeable=True)
    TEMPERATURE_POOL_HC_TARGET = DTag(["A750"], "°C", writeable=True)
    TEMPERATURE_POOL_HC_OUTDOOR_NORM = DTag(["A747"], "°C", writeable=True)
    TEMPERATURE_POOL_HC_NORM = DTag(["A748"], "°C", writeable=True)
    TEMPERATURE_POOL_HC_RESULT = DTag(["A752"], "°C")

    TEMPERATURE_MIX1 = DTag(["A44"], "°C")  # TEMPERATURE_MIXING1_CURRENT
    TEMPERATURE_MIX1_DEMAND = DTag(["A45"], "°C")  # TEMPERATURE_MIXING1_SET
    TEMPERATURE_MIX1_ADJUST = DTag(["I776"], "K", writeable=True)  # ADAPT_MIXING1
    TEMPERATURE_MIX1_PV_CHANGE = DTag(["A1094"], "K", writeable=True)
    TEMPERATURE_MIX1_PERCENT = DTag(["A510"], "%")
    TEMPERATURE_MIX1_HC_LIMIT = DTag(["A276"], "°C", writeable=True)  # T_HEATING_LIMIT_MIXING1
    TEMPERATURE_MIX1_HC_TARGET = DTag(["A277"], "°C", writeable=True)  # T_HEATING_LIMIT_TARGET_MIXING1
    TEMPERATURE_MIX1_HC_OUTDOOR_NORM = DTag(["A274"], "°C", writeable=True)  # T_NORM_OUTDOOR_MIXING1
    TEMPERATURE_MIX1_HC_HEATING_NORM = DTag(["A275"], "°C", writeable=True)  # T_NORM_HEATING_CICLE_MIXING1
    TEMPERATURE_MIX1_HC_MAX = DTag(["A278"], "°C", writeable=True)  # MAX_TEMP_MIXING1

    TEMPERATURE_MIX2 = DTag(["A46"], "°C")  # TEMPERATURE_MIXING2_CURRENT
    TEMPERATURE_MIX2_DEMAND = DTag(["A47"], "°C")  # TEMPERATURE_MIXING2_SET
    TEMPERATURE_MIX2_ADJUST = DTag(["I896"], "K", writeable=True)  # ADAPT_MIXING2
    TEMPERATURE_MIX2_PV_CHANGE = DTag(["A1095"], "K", writeable=True)
    TEMPERATURE_MIX2_PERCENT = DTag(["A512"], "%")
    TEMPERATURE_MIX2_HC_LIMIT = DTag(["A322"], "°C", writeable=True)
    TEMPERATURE_MIX2_HC_TARGET = DTag(["A323"], "°C", writeable=True)
    TEMPERATURE_MIX2_HC_OUTDOOR_NORM = DTag(["A320"], "°C", writeable=True)
    TEMPERATURE_MIX2_HC_HEATING_NORM = DTag(["A321"], "°C", writeable=True)
    TEMPERATURE_MIX2_HC_MAX = DTag(["A324"], "°C", writeable=True)

    TEMPERATURE_MIX3 = DTag(["A48"], "°C")  # TEMPERATURE_MIXING3_CURRENT
    TEMPERATURE_MIX3_DEMAND = DTag(["A49"], "°C")  # TEMPERATURE_MIXING3_SET
    TEMPERATURE_MIX3_ADJUST = DTag(["I1017"], "K", writeable=True)  # ADAPT_MIXING3
    TEMPERATURE_MIX3_PV_CHANGE = DTag(["A1096"], "K", writeable=True)
    TEMPERATURE_MIX3_PERCENT = DTag(["A514"], "%")
    TEMPERATURE_MIX3_HC_LIMIT = DTag(["A368"], "°C", writeable=True)
    TEMPERATURE_MIX3_HC_TARGET = DTag(["A369"], "°C", writeable=True)
    TEMPERATURE_MIX3_HC_OUTDOOR_NORM = DTag(["A366"], "°C", writeable=True)
    TEMPERATURE_MIX3_HC_HEATING_NORM = DTag(["A367"], "°C", writeable=True)
    TEMPERATURE_MIX3_HC_MAX = DTag(["A370"], "°C", writeable=True)

    # no information found in <host>/easycon/js/dictionary.js
    # COMPRESSOR_POWER = TagData(["A50"], "?°C")
    PERCENT_HEAT_CIRC_PUMP = DTag(["A51"], "%")
    PERCENT_SOURCE_PUMP = DTag(["A52"], "%")
    # A58 is listed as 'Power compressor' in <host>/easycon/js/dictionary.js
    # even if this value will not be displayed in the Waterkotte GUI - looks
    # like that this is really the same as the other two values (A51 & A52)
    # just a percentage value (from 0.0 - 100.0)
    PERCENT_COMPRESSOR = DTag(["A58"], "%")

    # just found... Druckgastemperatur
    TEMPERATURE_DISCHARGE = DTag(["A1462"], "°C")

    # implement https://github.com/marq24/ha-waterkotte/issues/3
    PRESSURE_WATER = DTag(["A1669"], "bar")

    # I1264 -> Heizstab Leistung?! -> 6000

    # keep but not found in Waterkotte GUI
    TEMPERATURE_COLLECTOR = DTag(["A42"], "°C")  # aktuelle Temperatur Kollektor
    TEMPERATURE_FLOW2 = DTag(["A43"], "°C")  # aktuelle Temperatur Vorlauf

    VERSION_CONTROLLER = DTag(["I1", "I2"], decode_f=DTag._decode_ro_fw)
    # VERSION_CONTROLLER_BUILD = TagData(["I2"])
    VERSION_BIOS = DTag(["I3"], decode_f=DTag._decode_ro_bios)
    DATE_DAY = DTag(["I5"])
    DATE_MONTH = DTag(["I6"])
    DATE_YEAR = DTag(["I7"])
    TIME_HOUR = DTag(["I8"])
    TIME_MINUTE = DTag(["I9"])
    OPERATING_HOURS_COMPRESSOR_1 = DTag(["I10"])
    OPERATING_HOURS_COMPRESSOR_2 = DTag(["I14"])
    OPERATING_HOURS_CIRCULATION_PUMP = DTag(["I18"])
    OPERATING_HOURS_SOURCE_PUMP = DTag(["I20"])
    OPERATING_HOURS_SOLAR = DTag(["I22"])
    ENABLE_HEATING = DTag(["I30"], writeable=True, decode_f=DTag._decode_state, encode_f=DTag._encode_state)
    ENABLE_COOLING = DTag(["I31"], writeable=True, decode_f=DTag._decode_state, encode_f=DTag._encode_state)
    ENABLE_WARMWATER = DTag(["I32"], writeable=True, decode_f=DTag._decode_state, encode_f=DTag._encode_state)
    ENABLE_POOL = DTag(["I33"], writeable=True, decode_f=DTag._decode_state, encode_f=DTag._encode_state)
    ENABLE_EXTERNAL_HEATER = DTag(["I35"], writeable=True, decode_f=DTag._decode_state, encode_f=DTag._encode_state)
    ENABLE_MIXING1 = DTag(["I37"], writeable=True, decode_f=DTag._decode_state, encode_f=DTag._encode_state)
    ENABLE_MIXING2 = DTag(["I38"], writeable=True, decode_f=DTag._decode_state, encode_f=DTag._encode_state)
    ENABLE_MIXING3 = DTag(["I39"], writeable=True, decode_f=DTag._decode_state, encode_f=DTag._encode_state)
    ENABLE_PV = DTag(["I41"], writeable=True, decode_f=DTag._decode_state, encode_f=DTag._encode_state)

    # UNKNOWN OPERATION-ENABLE Switches!
    ENABLE_X1 = DTag(["I34"], writeable=True, decode_f=DTag._decode_state, encode_f=DTag._encode_state)
    ENABLE_X2 = DTag(["I36"], writeable=True, decode_f=DTag._decode_state, encode_f=DTag._encode_state)
    ENABLE_X4 = DTag(["I40"], writeable=True, decode_f=DTag._decode_state, encode_f=DTag._encode_state)
    ENABLE_X5 = DTag(["I42"], writeable=True, decode_f=DTag._decode_state, encode_f=DTag._encode_state)

    STATE_SOURCEPUMP = DTag(["I51"], bit=0)
    STATE_HEATINGPUMP = DTag(["I51"], bit=1)
    STATE_EVD = DTag(["I51"], bit=2)
    STATE_COMPRESSOR = DTag(["I51"], bit=3)
    STATE_COMPRESSOR2 = DTag(["I51"], bit=4)
    STATE_EXTERNAL_HEATER = DTag(["I51"], bit=5)
    STATE_ALARM = DTag(["I51"], bit=6)
    STATE_COOLING = DTag(["I51"], bit=7)
    STATE_WATER = DTag(["I51"], bit=8)
    STATE_POOL = DTag(["I51"], bit=9)
    STATE_SOLAR = DTag(["I51"], bit=10)
    STATE_COOLING4WAY = DTag(["I51"], bit=11)

    # we do not have any valid information about the meaning after the bit=8...
    # https://github.com/flautze/home_assistant_waterkotte/issues/1#issuecomment-1916288553
    # ALARM_BITS = TagData(["I52"], bits=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], translate=True)
    ALARM_BITS = DTag(["I52"], bits=[0, 1, 2, 3, 4, 5, 6, 7, 8], translate=True)
    INTERRUPTION_BITS = DTag(["I53"], bits=[0, 1, 2, 3, 4, 5, 6], translate=True)

    STATE_SERVICE = DTag(["I135"])

    STATUS_HEATING = DTag(["I137"], decode_f=DTag._decode_status)
    STATUS_COOLING = DTag(["I138"], decode_f=DTag._decode_status)
    STATUS_WATER = DTag(["I139"], decode_f=DTag._decode_status)
    STATUS_POOL = DTag(["I140"], decode_f=DTag._decode_status)
    STATUS_SOLAR = DTag(["I141"], decode_f=DTag._decode_status)
    # returned 2='disabled' (even if the pump is running) - could be, that this TAG has to be set to 1='on' in order
    # to allow manual enable/disable the pump??? So it's then better to rename this then operation_mode and move it to
    # the switch section [just like the 'ENABLE_*' tags]
    STATUS_HEATING_CIRCULATION_PUMP = DTag(["I1270"], decode_f=DTag._decode_status)
    MANUAL_SOURCEPUMP = DTag(["I1281"])
    # see STATUS_HEATING_CIRCULATION_PUMP
    STATUS_SOLAR_CIRCULATION_PUMP = DTag(["I1287"], decode_f=DTag._decode_status)
    MANUAL_SOLARPUMP1 = DTag(["I1287"])
    MANUAL_SOLARPUMP2 = DTag(["I1289"])
    # see STATUS_HEATING_CIRCULATION_PUMP
    STATUS_BUFFER_TANK_CIRCULATION_PUMP = DTag(["I1291"], decode_f=DTag._decode_status)
    MANUAL_VALVE = DTag(["I1293"])
    MANUAL_POOLVALVE = DTag(["I1295"])
    MANUAL_COOLVALVE = DTag(["I1297"])
    MANUAL_4WAYVALVE = DTag(["I1299"])
    # see STATUS_HEATING_CIRCULATION_PUMP
    STATUS_COMPRESSOR = DTag(["I1307"], decode_f=DTag._decode_status)
    MANUAL_MULTIEXT = DTag(["I1319"])

    INFO_SERIES = DTag(["I105"], decode_f=DTag._decode_ro_series)
    INFO_ID = DTag(["I110"], decode_f=DTag._decode_ro_id)
    INFO_SERIAL = DTag(["I114", "I115"], decode_f=DTag._decode_ro_sn)
    ADAPT_HEATING = DTag(["I263"], writeable=True)

    STATE_BLOCKING_TIME = DTag(["D71"])
    STATE_TEST_RUN = DTag(["D581"])

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

    # D1273 "Heizungsumwäzpumpe ET 6900 Q" does not change it's value
    # HEATING_CIRCULATION_PUMP_D1273 = TagData(["D1273"], writeable=True)
    STATE_HEATING_CIRCULATION_PUMP_D425 = DTag(["D425"])
    STATE_BUFFERTANK_CIRCULATION_PUMP_D377 = DTag(["D377"])
    STATE_POOL_CIRCULATION_PUMP_D549 = DTag(["D549"])
    STATE_MIX1_CIRCULATION_PUMP_D248 = DTag(["D248"])
    STATE_MIX2_CIRCULATION_PUMP_D291 = DTag(["D291"])
    STATE_MIX3_CIRCULATION_PUMP_D334 = DTag(["D334"])
    # alternative MIX pump tags...
    STATE_MIX1_CIRCULATION_PUMP_D563 = DTag(["D563"])
    STATE_MIX2_CIRCULATION_PUMP_D564 = DTag(["D564"])
    STATE_MIX3_CIRCULATION_PUMP_D565 = DTag(["D565"])

    PERMANENT_HEATING_CIRCULATION_PUMP_WINTER_D1103 = DTag(["D1103"], writeable=True)
    PERMANENT_HEATING_CIRCULATION_PUMP_SUMMER_D1104 = DTag(["D1104"], writeable=True)

    # lngA520 = ["Vollbetriebsstunden", "Operating hours", "Heures activit\xe9"],

    # assuming that I1752 will be set to "Spreizung"=0 the A479 is a DELTA Temperature
    # lngA479 = ΔT Wärmequelle - ["T Wärmequelle", "T heat source", "T captage"],
    SOURCE_PUMP_CAPTURE_TEMPERATURE_A479 = DTag(["A479"], writeable=True)

    SGREADY_SWITCH_D795 = DTag(["D795"], writeable=True)
    # lngD796 = ["SG1: EVU-Sperre", "SG1: Extern switch off", "SG1: Coupure externe"],
    SGREADY_SG1_EXTERN_OFF_SWITCH_D796 = DTag(["D796"])
    # lngD797 = ["SG2: Normalbetrieb", "SG2: Normal operation", "SG2: Fonction normal"],
    SGREADY_SG2_NORMAL_D797 = DTag(["D797"])
    # lngD798 = ["SG3: Sollwerterh.", "SG3: Setpoint change", "SG3: Augment. consigne"],
    SGREADY_SG3_SETPOINT_CHANGE_D798 = DTag(["D798"])
    # lngD799 = ["SG4: Zwangslauf", "SG4: Forced run", "SG4: Marche forc\xe9e"],
    SGREADY_SG4_FORCE_RUN_D799 = DTag(["D799"])

    ##################################################################################
    # BASICVENT / ECOVENT Stuff...
    # PID-Regler: Proportional-Integral-Differenzial-Regler
    ##################################################################################
    # A4387: uom: '', 'Energieersparnis gesamt'
    BASICVENT_ENERGY_SAVE_TOTAL_A4387 = DTag(["A4387"], decode_f=DTag._decode_value_analog)
    # A4389: uom: '', 'Energieersparnis aktuell'
    BASICVENT_ENERGY_SAVE_CURRENT_A4389 = DTag(["A4389"], decode_f=DTag._decode_value_analog)
    # A4391: uom: '', 'Wärmerückgewinnungsgrad'
    BASICVENT_ENERGY_RECOVERY_RATE_A4391 = DTag(["A4391"], decode_f=DTag._decode_value_analog)
    # A4498: uom: 'Tage', 'Luftfilter Wechsel Betriebsstunden'
    BASICVENT_FILTER_CHANGE_OPERATING_DAYS_A4498 = DTag(["A4498"], decode_f=DTag._decode_value_analog)
    # A4504: uom: 'Tage', 'Luftfilter Wechsel Betriebsstunden Restlaufzeit dd'
    BASICVENT_FILTER_CHANGE_REMAINING_OPERATING_DAYS_A4504 = DTag(["A4504"], decode_f=DTag._decode_value_analog)
    # D1544: uom: '', 'Luftfilter Wechsel Betriebsstunden Reset'
    BASICVENT_FILTER_CHANGE_OPERATING_HOURS_RESET_D1544 = DTag(["D1544"], writeable=True)
    # D1469: uom: '', 'Luftfilter Wechselanzeige'
    BASICVENT_FILTER_CHANGE_DISPLAY_D1469 = DTag(["D1469"])
    # D1626: uom: '', 'Luftfilter Wechselanzeige Animation'
    # BASICVENT_FILTER_CHANGE_DISPLAY_ANIMATION_D1626 = TagData(["D1626"])

    # A4506: uom: '', 'Hu Luftfeuchtigkeit PID'
    # BASICVENT_HUMIDITY_SETPOINT_A4506 = TagData(["A4506"], writeable=True, decode_f=TagData._decode_value_analog)
    # A4508: uom: '', 'Hu Luftfeuchtigkeit Sollwert'
    # BASICVENT_HUMIDITY_DEMAND_A4508 = TagData(["A4508"], decode_f=TagData._decode_value_analog)
    # A4510: uom: '', 'Hu Luftfeuchtigkeit'
    # BASICVENT_HUMIDITY_SECOND_VALUE_A4510 = TagData(["A4510"], decode_f=TagData._decode_value_analog)
    # A4990: uom: '', 'Luftfeuchtigkeit'
    BASICVENT_HUMIDITY_VALUE_A4990 = DTag(["A4990"], decode_f=DTag._decode_value_analog)

    # A4512: uom: '', 'CO2-Konzentration PID'
    # BASICVENT_CO2_SETPOINT_A4512 = TagData(["A4512"], writeable=True, decode_f=TagData._decode_value_analog)
    # A4514: uom: '', 'CO2-Konzentration Sollwert'
    # BASICVENT_CO2_DEMAND_A4514 = TagData(["A4514"], decode_f=TagData._decode_value_analog)
    # A4516: uom: '', 'CO2-Konzentration'
    # BASICVENT_CO2_SECOND_VALUE_A4516 = TagData(["A4516"], decode_f=TagData._decode_value_analog)
    # A4992: uom: '', 'CO2'
    BASICVENT_CO2_VALUE_A4992 = DTag(["A4992"], decode_f=DTag._decode_value_analog)

    # A4518: uom: '', 'VOC Kohlenwasserstoffverbindungen PID'
    # BASICVENT_VOC_SETPOINT_A4518 = TagData(["A4518"], writeable=True, decode_f=TagData._decode_value_analog)
    # A4520: uom: '', 'VOC Kohlenwasserstoffverbindungen Sollwert'
    # BASICVENT_VOC_DEMAND_A4520 = TagData(["A4520"], decode_f=TagData._decode_value_analog)
    # A4522: uom: '', 'VOC Kohlenwasserstoffverbindungen'
    BASICVENT_VOC_VALUE_A4522 = DTag(["A4522"], decode_f=DTag._decode_value_analog)

    # I4523: uom: '', 'Luftqualitaet Messung VOC CO2 Sensor'

    # I4582: uom: '', opts: { type:'select', options: ['Tag','Nacht','Zeitprogramm','Party','Urlaub','Bypass'] }, 'i_Mode'
    BASICVENT_OPERATION_MODE_I4582 = DTag(
        ["I4582"], writeable=True, decode_f=DTag._decode_six_steps_mode, encode_f=DTag._encode_six_steps_mode)

    # mdi:air-filter
    # mdi:hvac
    # mdi:wind-power

    # A4549: uom: '', 'Luefter 1 Rueckmeldung'
    # D1605: uom: '', 'Luefter 1 - Manuell Drehzahl'
    # A4551: uom: 'U/min', 'Luefter 1 Umdrehungen pro Minute'
    BASICVENT_INCOMING_FAN_RPM_A4551 = DTag(["A4551"], decode_f=DTag._decode_value_analog)
    # A4986: uom: '%', 'Analogausgang Y1' - Rotation Incoming air drive percent
    BASICVENT_INCOMING_FAN_A4986 = DTag(["A4986"], decode_f=DTag._decode_value_analog)
    # A5000: uom: '', 'T1' - Außenluft/Frischluft - Outdoor air
    BASICVENT_TEMPERATURE_INCOMING_AIR_BEFORE_ODA_A5000 = DTag(["A5000"], decode_f=DTag._decode_value_analog)
    # A4996: uom: '', 'T3' - Zuluft - Supply air
    BASICVENT_TEMPERATURE_INCOMING_AIR_AFTER_SUP_A4996 = DTag(["A4996"], decode_f=DTag._decode_value_analog)

    # A4545: uom: '', 'Luefter 2 Rueckmeldung'
    # D1603: uom: '', 'Luefter 2 - Manuell Drehzahl'
    # A4547: uom: 'U/min', 'Luefter 2 Umdrehungen pro Minute'
    BASICVENT_OUTGOING_FAN_RPM_A4547 = DTag(["A4547"], decode_f=DTag._decode_value_analog)
    # A4984: uom: '%', 'Analogausgang Y2' - Rotation Ongoing air drive percent
    BASICVENT_OUTGOING_FAN_A4984 = DTag(["A4984"], decode_f=DTag._decode_value_analog)
    # A4998: uom: '', 'T2' -> Abluft - Extract air
    BASICVENT_TEMPERATURE_OUTGOING_AIR_BEFORE_ETH_A4998 = DTag(["A4998"], decode_f=DTag._decode_value_analog)
    # A4994: uom: '', 'T4' -> Fortluft - Exhaust air
    BASICVENT_TEMPERATURE_OUTGOING_AIR_AFTER_EEH_A4994 = DTag(["A4994"], decode_f=DTag._decode_value_analog)

    # D1432: uom: '', 'Bypass Aktiv' -
    BASICVENT_STATUS_BYPASS_ACTIVE_D1432 = DTag(["D1432"])
    # D1433: uom: '', 'HU En'
    BASICVENT_STATUS_HUMIDIFIER_ACTIVE_D1433 = DTag(["D1433"])
    # D1465: uom: '', 'Comfort-Bypass'
    BASICVENT_STATUS_COMFORT_BYPASS_ACTIVE_D1465 = DTag(["D1465"])
    # D1466: uom: '', 'Smartbypass'
    BASICVENT_STATUS_SMART_BYPASS_ACTIVE_D1466 = DTag(["D1466"])
    # D1503: uom: '', 'Holiday enabled'
    BASICVENT_STATUS_HOLIDAY_ENABLED_D1503 = DTag(["D1503"])

    #############################
    # UNKNOWN BASIC VENT VALUES #
    #############################
    # A4420: uom: '', 'Luftmenge Stufe 2 - Nennlüftung NL'

    # A4525: uom: '', 'Schutzfunktion Ablufttemperatur Schaltdifferenz'
    # A4527: uom: '', 'Schutzfunktion Ablufttemperatur Unterbrechung'
    # A4529: uom: '', 'Schutzfunktion Ablufttemperatur Warnung'

    # A4531: uom: '', 'Frostschutzfunktion Fortluft EHH NotAus'
    # A4533: uom: '', 'Frostschutzfunktion Taktbetrieb High'
    # A4535: uom: '', 'Frostschutzfunktion Taktbetrieb Low'
    # A4537: uom: '', 'Frostschutzfunktion Schaltdifferenz'
    # A4539: uom: '', 'Frostschutzfunktion Fortluft EHH'
    # A4541: uom: '', 'Frostschutzfunktion Aussenluft ODA'

    # A4542: uom: '', 'Feuerstaetten Funktion FPF Betriebsmodus Abluft'
    # A4543: uom: '', 'Feuerstaetten Funktion FPF Betriebsmodus Aussenluft'

    # D1488: uom: '', 'Warnung Wxxx'
    # D1489: uom: '', 'Fehler Fxxx'
    # D1490: uom: '', 'Fehler Fxxx'
    # D1491: uom: '', 'Fehler Fxxx'

    # D1508: uom: '', 'Frostschutz Auskuehlschutz T1'
    # D1507: uom: '', 'Frostschutz Auskuehlschutz T2'

    # D1627: uom: '', 'Feuerstaetten Funktion FPF Animation'
    # D1628: uom: '', 'Rauchmelder Brandschutz Funktion SDF Animation'
    # D1629: uom: '', 'Frostschutzfunktion Aussenluft ODA FALSE OK'

    # D2035: uom: '', 'Anschlussseite Rechts TRUE oder Rechts FALSE'
    # D2036: uom: '', 'Anschlussseite Links TRUE oder Rechts FALSE'
    # I2331: uom: '', 'TT_b_enabled[5,6]'
    # I2484: uom: '', 'TT_b_enabled[5,2]'
    # I2889: uom: '', 'TT_b_enabled[6,5]'

    def __hash__(self) -> int:
        return hash(self.name)
