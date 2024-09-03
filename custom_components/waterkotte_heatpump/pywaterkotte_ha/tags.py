import logging
import math
import struct
from datetime import datetime, timedelta, time
from enum import Enum
from typing import (
    NamedTuple,
    Callable,
    List,
    Collection
)

from custom_components.waterkotte_heatpump.pywaterkotte_ha.const import (
    SERIES,
    SYSTEM_IDS,
    SIX_STEPS_MODES,
    # SCHEDULE_DAY_LIST,
    # SCHEDULE_SENSOR_TYPES_LIST
)
from custom_components.waterkotte_heatpump.pywaterkotte_ha.error import (
    InvalidValueException,
)

# from aenum import Enum, extend_enum

_LOGGER: logging.Logger = logging.getLogger(__package__)


class DataTag(NamedTuple):

    def _decode_value_default(self, str_vals: List[str]):
        return self.__decode_value_default(str_vals, factor=10.0)

    def _decode_value_analog(self, str_vals: List[str]):
        return self.__decode_value_default(str_vals, factor=-1.0)

    def __decode_value_default(self, str_vals: List[str], factor: float):
        if str_vals is None:
            return None

        first_val = str_vals[0]
        if first_val is None:
            # do not check any further if for what ever reason the first value of the str_vals is None
            return None

        first_tag = self.tags[0]
        assert first_tag[0] in ["A", "I", "D", "3"]

        if first_tag[0] == "A":
            if len(self.tags) == 1:
                # SIM VENT OperatingHour Sensors...
                # if self.tags[0] == "A4498":
                #    return float('180.000000')
                # if self.tags[0] == "A4504":
                #    return float('19')

                if factor > -1.0:
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

            elif first_tag[0:6] == "3:HREG":
                # currently only supporting integers from HERG registers (only in use for manual vent speeds)
                return int(first_val)

            else:
                raise InvalidValueException(
                    # "%s is not a valid value for %s" % (val, ecotouch_tag)
                    f"{first_val} is not a valid value for {first_tag}"
                )

        return None

    def _encode_value_default(self, value, encoded_values):
        self.__encode_value_default(value, encoded_values, factor=10)

    def _encode_value_analog(self, value, encoded_values):
        self.__encode_value_default(value, encoded_values, factor=-1)

    def __encode_value_default(self, value, encoded_values, factor: int):
        assert len(self.tags) == 1
        ecotouch_tag = self.tags[0]
        assert ecotouch_tag[0] in ["A", "I", "D", "3"]

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
        elif ecotouch_tag[0:6] == "3:HREG":
            # we force INT values for 3:HREG (only in use for 'manual vent speed' anyhow)
            encoded_values[ecotouch_tag] = str(int(value))

    def _decode_alarms(self, str_vals: List[str], lang_map: dict):
        if str_vals is None:
            return None

        error_tag_index = 0
        final_value = ""
        for a_val in str_vals:
            if a_val is not None and isinstance(a_val, int):
                if self.tags[error_tag_index] in lang_map:
                    if error_tag_index+1 == len(str_vals):
                        # the last error field [I2614] only contain 13 bits
                        bits = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
                    elif error_tag_index == 0:
                        # the bit13 (= "-") & bit14(= "Kommunikationstrigger") of I52 are NO alarms
                        bits = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 15]
                    else:
                        bits = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]

                    for idx in range(len(bits)):
                        if (int(a_val) & (1 << bits[idx])) > 0:
                            final_value = final_value + ", " + str(lang_map[self.tags[error_tag_index]][idx])

                    #_LOGGER.error(f"{self.tags[error_tag_index]} {a_val} -> '{final_value}'")
                error_tag_index = error_tag_index + 1

        # we need to trim the firsts initial added ', '
        if len(final_value) > 0:
            return final_value[2:]
        else:
            return final_value

    def _decode_datetime(self, str_vals: List[str]):
        if str_vals is None:
            return None

        int_vals = list(map(int, str_vals))
        if int_vals[0] < 2000:
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
        if str_vals is None:
            return None

        int_vals = list(map(int, str_vals))
        if int_vals[0] > 23:
            int_vals[0] = 0
        if int_vals[1] > 59:
            int_vals[1] = 0
        dt = time(hour=int_vals[0], minute=int_vals[1])
        return dt

    def _encode_time_hhmm(self, value, encoded_values):
        assert isinstance(value, time)
        if value == time.max:
            vals = ["24", "0"]
        else:
            vals = [str(val) for val in [value.hour, value.minute]]

        for i, tags in enumerate(self.tags):
            encoded_values[tags] = vals[i]

    def _decode_state(self, str_vals: List[str]):
        if str_vals is None:
            return None

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
        if str_vals is None:
            return None

        assert len(self.tags) == 1
        if str_vals[0] is not None:
            int_val = int(str_vals[0])
            if 0 <= int_val <= len(SIX_STEPS_MODES):
                return SIX_STEPS_MODES[int_val]
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
        if str_vals is None:
            return None

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
        if str_vals is None:
            return None

        if str_vals[0]:
            if isinstance(str_vals[0], int):
                idx = int(str_vals[0])
                if len(SERIES) > idx:
                    return SERIES[idx]
                else:
                    return f"UNKNOWN_SERIES_{idx}"
        else:
            return "UNKNOWN_SERIES"

    def _decode_ro_id(self, str_vals: List[str]):
        if str_vals is None:
            return None

        assert len(self.tags) == 1
        if str_vals[0]:
            if isinstance(str_vals[0], int):
                idx = int(str_vals[0])
                if len(SYSTEM_IDS) > idx:
                    return SYSTEM_IDS[idx]
                else:
                    return f"UNKNOWN_SYSTEM_{idx}"
        else:
            return "UNKNOWN_SYSTEM"


    def _decode_ro_bios(self, str_vals: List[str]):
        if str_vals is None:
            return None

        assert len(self.tags) == 1
        str_val = str_vals[0]
        if len(str_val) > 2:
            return f"{str_val[:-2]}.{str_val[-2:]}"
        else:
            return str_val

    def _decode_ro_fw(self, str_vals: List[str]):
        if str_vals is None:
            return None

        assert len(self.tags) == 2
        str_val1 = str_vals[0]
        str_val2 = str_vals[1]
        try:
            # str fw2 = f"{str_val1[:-4]:0>2}.{str_val1[-4:-2]}.{str_val1[-2:]}"
            return f"0{str_val1[0]}.{str_val1[1:3]}.{str_val1[3:]}-{str_val2}"
        except Exception as ex:
            _LOGGER.warning("could not decode FW",ex)
            return f"FW_{str_val1}-{str_val2}"

    def _decode_ro_sn(self, str_vals: List[str]):
        if str_vals is None:
            return None

        assert len(self.tags) == 2
        sn1 = int(str_vals[0])
        sn2 = int(str_vals[1])
        try:
            s1 = "WE" if math.floor(sn1 / 1000) > 0 else "00"  # pylint: disable=invalid-name
            s2 = (sn1 - 1000 if math.floor(sn1 / 1000) > 0 else sn1)  # pylint: disable=invalid-name
            s2 = "0" + str(s2) if s2 < 10 else s2  # pylint: disable=invalid-name
            return str(s1) + str(s2) + str(sn2)
        except Exception as ex:
            _LOGGER.warning("could not decode Serial",ex)
            return f"Serial_{sn1}-{sn2}"

    def _decode_year(self, str_vals: List[str]):
        if str_vals is None:
            return None

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


class WKHPTag(DataTag, Enum):
    def __hash__(self) -> int:
        return hash(self.name)

    #################################################
    # waterkotte DATE/time stuff

    # #use set date...
    # #I1758	S_OK
    # 192	08
    # #I1759	S_OK
    # 192	03
    # #I1760	S_OK
    # 192	2024
    # #I1761	S_OK
    # 192	17
    # #I1762	S_OK
    # 192	09
    # #D801	S_OK
    # 192	1
    #
    # second request...
    # #I1758	S_OK
    # 192	8.03
    #
    # write data...
    # #D22	S_OK
    # 192	1

    # day: I5,       month: I6,      year: I7,       hour: I8,       minute: I9
    WATERKOTTE_BIOS_TIME = DataTag(
        ["I7", "I6", "I5", "I8", "I9"], decode_f=DataTag._decode_datetime
    )
    # day: I1758,    month: I1759,   year: I1760,    hour: I1761,    minute: I1762
    # WATERKOTTE_TIME_SET = DataTag(
    #    ["I1760", "I1759", "I1758", "I1761", "I1762"], writeable=True, decode_f=DataTag._decode_datetime,
    #    encode_f=DataTag._encode_datetime
    # )
    # WATERKOTTE_TIME_X1 = DataTag(["D801"], writeable=True)
    # WATERKOTTE_TIME_X2 = DataTag(["D22"], writeable=True)

    HOLIDAY_ENABLED = DataTag(["D420"], writeable=True)
    HOLIDAY_START_TIME = DataTag(
        ["I1254", "I1253", "I1252", "I1250", "I1251"], writeable=True, decode_f=DataTag._decode_datetime,
        encode_f=DataTag._encode_datetime
    )
    HOLIDAY_END_TIME = DataTag(
        ["I1259", "I1258", "I1257", "I1255", "I1256"], writeable=True, decode_f=DataTag._decode_datetime,
        encode_f=DataTag._encode_datetime
    )
    TEMPERATURE_OUTSIDE = DataTag(["A1"], "°C")
    TEMPERATURE_OUTSIDE_1H = DataTag(["A2"], "°C")
    TEMPERATURE_OUTSIDE_24H = DataTag(["A3"], "°C")
    TEMPERATURE_SOURCE_ENTRY = DataTag(["A4"], "°C")
    TEMPERATURE_SOURCE_EXIT = DataTag(["A5"], "°C")
    TEMPERATURE_EVAPORATION = DataTag(["A6"], "°C")
    TEMPERATURE_SUCTION_LINE = DataTag(["A7"], "°C")
    PRESSURE_EVAPORATION = DataTag(["A8"], "bar")
    TEMPERATURE_RETURN_SETPOINT = DataTag(["A10"], "°C")
    TEMPERATURE_RETURN = DataTag(["A11"], "°C")
    TEMPERATURE_FLOW = DataTag(["A12"], "°C")
    TEMPERATURE_CONDENSATION = DataTag(["A13"], "°C")
    TEMPERATURE_BUBBLEPOINT = DataTag(["A14"], "°C")
    PRESSURE_CONDENSATION = DataTag(["A15"], "bar")
    TEMPERATURE_BUFFERTANK = DataTag(["A16"], "°C")
    TEMPERATURE_ROOM = DataTag(["A17"], "°C")
    TEMPERATURE_ROOM_1H = DataTag(["A18"], "°C")

    TEMPERATURE_SOLAR = DataTag(["A21"], "°C")
    TEMPERATURE_SOLAR_EXIT = DataTag(["A22"], "°C")
    POSITION_EXPANSION_VALVE = DataTag(["A23"], "")
    SUCTION_GAS_OVERHEATING = DataTag(["A24"], "")

    POWER_ELECTRIC = DataTag(["A25"], "kW")
    POWER_HEATING = DataTag(["A26"], "kW")
    POWER_COOLING = DataTag(["A27"], "kW")
    COP_HEATING = DataTag(["A28"], "")
    COP_COOLING = DataTag(["A29"], "")

    # ENERGY-YEAR-BALANCE
    COP_HEATPUMP_YEAR = DataTag(["A460"], "")  # HEATPUMP_COP
    COP_HEATPUMP_ACTUAL_YEAR_INFO = DataTag(["I1261"], decode_f=DataTag._decode_year)  # HEATPUMP_COP_YEAR
    COP_TOTAL_SYSTEM_YEAR = DataTag(["A461"], "")
    COP_HEATING_YEAR = DataTag(["A695"])
    COP_HOT_WATER_YEAR = DataTag(["A697"])

    ENERGY_CONSUMPTION_TOTAL_YEAR = DataTag(["A450", "A451"], "kWh")
    COMPRESSOR_ELECTRIC_CONSUMPTION_YEAR = DataTag(["A444", "A445"], "kWh")  # ANUAL_CONSUMPTION_COMPRESSOR
    SOURCEPUMP_ELECTRIC_CONSUMPTION_YEAR = DataTag(["A446", "A447"], "kWh")  # ANUAL_CONSUMPTION_SOURCEPUMP
    ELECTRICAL_HEATER_ELECTRIC_CONSUMPTION_YEAR = DataTag(["A448", "A449"], "kWh")  # ANUAL_CONSUMPTION_EXTERNALHEATER
    ENERGY_PRODUCTION_TOTAL_YEAR = DataTag(["A458", "A459"], "kWh")
    HEATING_ENERGY_PRODUCTION_YEAR = DataTag(["A452", "A453"], "kWh")  # ANUAL_CONSUMPTION_HEATING
    HOT_WATER_ENERGY_PRODUCTION_YEAR = DataTag(["A454", "A455"], "kWh")  # ANUAL_CONSUMPTION_WATER
    POOL_ENERGY_PRODUCTION_YEAR = DataTag(["A456", "A457"], "kWh")  # ANUAL_CONSUMPTION_POOL
    COOLING_ENERGY_YEAR = DataTag(["A462", "A463"], "kWh")

    # The LAST12M values for ENERGY_CONSUMPTION_TOTAL (also the individual values for compressor, sourcepump & e-heater
    # will be calculated based on values for each month (and will be summarized in the FE))
    # The same applies to the ENERGY_PRODUCTION_TOTAL (with the individual values for heating, hot_water & pool)
    COP_TOTAL_SYSTEM_LAST12M = DataTag(["A435"])
    COOLING_ENERGY_LAST12M = DataTag(["A436"], "kWh")

    ENG_CONSUMPTION_COMPRESSOR01 = DataTag(["A782"])
    ENG_CONSUMPTION_COMPRESSOR02 = DataTag(["A783"])
    ENG_CONSUMPTION_COMPRESSOR03 = DataTag(["A784"])
    ENG_CONSUMPTION_COMPRESSOR04 = DataTag(["A785"])
    ENG_CONSUMPTION_COMPRESSOR05 = DataTag(["A786"])
    ENG_CONSUMPTION_COMPRESSOR06 = DataTag(["A787"])
    ENG_CONSUMPTION_COMPRESSOR07 = DataTag(["A788"])
    ENG_CONSUMPTION_COMPRESSOR08 = DataTag(["A789"])
    ENG_CONSUMPTION_COMPRESSOR09 = DataTag(["A790"])
    ENG_CONSUMPTION_COMPRESSOR10 = DataTag(["A791"])
    ENG_CONSUMPTION_COMPRESSOR11 = DataTag(["A792"])
    ENG_CONSUMPTION_COMPRESSOR12 = DataTag(["A793"])

    ENG_CONSUMPTION_SOURCEPUMP01 = DataTag(["A794"])
    ENG_CONSUMPTION_SOURCEPUMP02 = DataTag(["A795"])
    ENG_CONSUMPTION_SOURCEPUMP03 = DataTag(["A796"])
    ENG_CONSUMPTION_SOURCEPUMP04 = DataTag(["A797"])
    ENG_CONSUMPTION_SOURCEPUMP05 = DataTag(["A798"])
    ENG_CONSUMPTION_SOURCEPUMP06 = DataTag(["A799"])
    ENG_CONSUMPTION_SOURCEPUMP07 = DataTag(["A800"])
    ENG_CONSUMPTION_SOURCEPUMP08 = DataTag(["A802"])
    ENG_CONSUMPTION_SOURCEPUMP09 = DataTag(["A804"])
    ENG_CONSUMPTION_SOURCEPUMP10 = DataTag(["A805"])
    ENG_CONSUMPTION_SOURCEPUMP11 = DataTag(["A806"])
    ENG_CONSUMPTION_SOURCEPUMP12 = DataTag(["A807"])

    # Docs say it should start at 806 for external heater but there is an overlapp to source pump
    ENG_CONSUMPTION_EXTERNALHEATER01 = DataTag(["A808"])
    ENG_CONSUMPTION_EXTERNALHEATER02 = DataTag(["A809"])
    ENG_CONSUMPTION_EXTERNALHEATER03 = DataTag(["A810"])
    ENG_CONSUMPTION_EXTERNALHEATER04 = DataTag(["A811"])
    ENG_CONSUMPTION_EXTERNALHEATER05 = DataTag(["A812"])
    ENG_CONSUMPTION_EXTERNALHEATER06 = DataTag(["A813"])
    ENG_CONSUMPTION_EXTERNALHEATER07 = DataTag(["A814"])
    ENG_CONSUMPTION_EXTERNALHEATER08 = DataTag(["A815"])
    ENG_CONSUMPTION_EXTERNALHEATER09 = DataTag(["A816"])
    ENG_CONSUMPTION_EXTERNALHEATER10 = DataTag(["A817"])
    ENG_CONSUMPTION_EXTERNALHEATER11 = DataTag(["A818"])
    ENG_CONSUMPTION_EXTERNALHEATER12 = DataTag(["A819"])

    ENG_PRODUCTION_HEATING01 = DataTag(["A830"])
    ENG_PRODUCTION_HEATING02 = DataTag(["A831"])
    ENG_PRODUCTION_HEATING03 = DataTag(["A832"])
    ENG_PRODUCTION_HEATING04 = DataTag(["A833"])
    ENG_PRODUCTION_HEATING05 = DataTag(["A834"])
    ENG_PRODUCTION_HEATING06 = DataTag(["A835"])
    ENG_PRODUCTION_HEATING07 = DataTag(["A836"])
    ENG_PRODUCTION_HEATING08 = DataTag(["A837"])
    ENG_PRODUCTION_HEATING09 = DataTag(["A838"])
    ENG_PRODUCTION_HEATING10 = DataTag(["A839"])
    ENG_PRODUCTION_HEATING11 = DataTag(["A840"])
    ENG_PRODUCTION_HEATING12 = DataTag(["A841"])

    ENG_PRODUCTION_WARMWATER01 = DataTag(["A842"])
    ENG_PRODUCTION_WARMWATER02 = DataTag(["A843"])
    ENG_PRODUCTION_WARMWATER03 = DataTag(["A844"])
    ENG_PRODUCTION_WARMWATER04 = DataTag(["A845"])
    ENG_PRODUCTION_WARMWATER05 = DataTag(["A846"])
    ENG_PRODUCTION_WARMWATER06 = DataTag(["A847"])
    ENG_PRODUCTION_WARMWATER07 = DataTag(["A848"])
    ENG_PRODUCTION_WARMWATER08 = DataTag(["A849"])
    ENG_PRODUCTION_WARMWATER09 = DataTag(["A850"])
    ENG_PRODUCTION_WARMWATER10 = DataTag(["A851"])
    ENG_PRODUCTION_WARMWATER11 = DataTag(["A852"])
    ENG_PRODUCTION_WARMWATER12 = DataTag(["A853"])

    ENG_PRODUCTION_POOL01 = DataTag(["A854"])
    ENG_PRODUCTION_POOL02 = DataTag(["A855"])
    ENG_PRODUCTION_POOL03 = DataTag(["A856"])
    ENG_PRODUCTION_POOL04 = DataTag(["A857"])
    ENG_PRODUCTION_POOL05 = DataTag(["A858"])
    ENG_PRODUCTION_POOL06 = DataTag(["A859"])
    ENG_PRODUCTION_POOL07 = DataTag(["A860"])
    ENG_PRODUCTION_POOL08 = DataTag(["A861"])
    ENG_PRODUCTION_POOL09 = DataTag(["A862"])
    ENG_PRODUCTION_POOL10 = DataTag(["A863"])
    ENG_PRODUCTION_POOL11 = DataTag(["A864"])
    ENG_PRODUCTION_POOL12 = DataTag(["A865"])

    ENG_HEATPUMP_COP_MONTH01 = DataTag(["A924"])
    ENG_HEATPUMP_COP_MONTH02 = DataTag(["A925"])
    ENG_HEATPUMP_COP_MONTH03 = DataTag(["A926"])
    ENG_HEATPUMP_COP_MONTH04 = DataTag(["A927"])
    ENG_HEATPUMP_COP_MONTH05 = DataTag(["A928"])
    ENG_HEATPUMP_COP_MONTH06 = DataTag(["A929"])
    ENG_HEATPUMP_COP_MONTH07 = DataTag(["A930"])
    ENG_HEATPUMP_COP_MONTH08 = DataTag(["A930"])
    ENG_HEATPUMP_COP_MONTH09 = DataTag(["A931"])
    ENG_HEATPUMP_COP_MONTH10 = DataTag(["A932"])
    ENG_HEATPUMP_COP_MONTH11 = DataTag(["A933"])
    ENG_HEATPUMP_COP_MONTH12 = DataTag(["A934"])

    # Temperature stuff
    TEMPERATURE_HEATING = DataTag(["A30"], "°C")
    TEMPERATURE_HEATING_DEMAND = DataTag(["A31"], "°C")
    TEMPERATURE_HEATING_ADJUST = DataTag(["I263"], "K", writeable=True)
    TEMPERATURE_HEATING_HYSTERESIS = DataTag(["A61"], "K", writeable=True)
    TEMPERATURE_HEATING_PV_CHANGE = DataTag(["A682"], "K", writeable=True)
    TEMPERATURE_HEATING_HC_OUTDOOR_1H = DataTag(["A90"], "°C")
    TEMPERATURE_HEATING_HC_LIMIT = DataTag(["A93"], "°C", writeable=True)
    TEMPERATURE_HEATING_HC_TARGET = DataTag(["A94"], "°C", writeable=True)
    TEMPERATURE_HEATING_HC_OUTDOOR_NORM = DataTag(["A91"], "°C", writeable=True)
    TEMPERATURE_HEATING_HC_NORM = DataTag(["A92"], "°C", writeable=True)
    TEMPERATURE_HEATING_HC_RESULT = DataTag(["A96"], "°C")
    TEMPERATURE_HEATING_ANTIFREEZE = DataTag(["A1231"], "°C", writeable=True)
    TEMPERATURE_HEATING_SETPOINTLIMIT_MAX = DataTag(["A95"], "°C", writeable=True)
    TEMPERATURE_HEATING_SETPOINTLIMIT_MIN = DataTag(["A104"], "°C", writeable=True)
    TEMPERATURE_HEATING_POWLIMIT_MAX = DataTag(["A504"], "%", writeable=True)
    TEMPERATURE_HEATING_POWLIMIT_MIN = DataTag(["A505"], "%", writeable=True)
    TEMPERATURE_HEATING_SGREADY_STATUS4 = DataTag(["A967"], "°C", writeable=True)

    # TEMPERATURE_HEATING_BUFFERTANK_ROOM_SETPOINT = DataTag(["A413"], "°C", writeable=True)

    TEMPERATURE_HEATING_MODE = DataTag(
        ["I265"], writeable=True, decode_f=DataTag._decode_six_steps_mode, encode_f=DataTag._encode_six_steps_mode
    )
    # this A32 value is not visible in the GUI - and IMHO (marq24) there should
    # be no way to set the heating temperature directly - use the values of the
    # 'TEMPERATURE_HEATING_HC' instead (HC = HeatCurve)
    TEMPERATURE_HEATING_SETPOINT = DataTag(["A32"], "°C", writeable=True)
    # same as A32 ?!
    TEMPERATURE_HEATING_SETPOINT_FOR_SOLAR = DataTag(["A1710"], "°C", writeable=True)

    TEMPERATURE_COOLING = DataTag(["A33"], "°C")
    TEMPERATURE_COOLING_DEMAND = DataTag(["A34"], "°C")
    TEMPERATURE_COOLING_SETPOINT = DataTag(["A109"], "°C", writeable=True)
    TEMPERATURE_COOLING_OUTDOOR_LIMIT = DataTag(["A108"], "°C", writeable=True)
    TEMPERATURE_COOLING_FLOW_LIMIT = DataTag(["A110"], "°C", writeable=True)
    TEMPERATURE_COOLING_HYSTERESIS = DataTag(["A107"], "K", writeable=True)
    TEMPERATURE_COOLING_PV_CHANGE = DataTag(["A683"], "K", writeable=True)

    TEMPERATURE_WATER = DataTag(["A19"], "°C")
    TEMPERATURE_WATER_DEMAND = DataTag(["A37"], "°C")
    TEMPERATURE_WATER_SETPOINT = DataTag(["A38"], "°C", writeable=True)
    TEMPERATURE_WATER_HYSTERESIS = DataTag(["A139"], "K", writeable=True)
    TEMPERATURE_WATER_PV_CHANGE = DataTag(["A684"], "K", writeable=True)
    TEMPERATURE_WATER_DISINFECTION = DataTag(["A168"], "°C", writeable=True)
    SCHEDULE_WATER_DISINFECTION_START_TIME = DataTag(
        ["I505", "I506"], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    # SCHEDULE_WATER_DISINFECTION_START_HOUR = DataTag(["I505"], "", writeable=True)
    # SCHEDULE_WATER_DISINFECTION_START_MINUTE = DataTag(["I506"], "", writeable=True)
    SCHEDULE_WATER_DISINFECTION_DURATION = DataTag(["I507"], "h", writeable=True)
    SCHEDULE_WATER_DISINFECTION_1MO = DataTag(["D153"], "", writeable=True)
    SCHEDULE_WATER_DISINFECTION_2TU = DataTag(["D154"], "", writeable=True)
    SCHEDULE_WATER_DISINFECTION_3WE = DataTag(["D155"], "", writeable=True)
    SCHEDULE_WATER_DISINFECTION_4TH = DataTag(["D156"], "", writeable=True)
    SCHEDULE_WATER_DISINFECTION_5FR = DataTag(["D157"], "", writeable=True)
    SCHEDULE_WATER_DISINFECTION_6SA = DataTag(["D158"], "", writeable=True)
    SCHEDULE_WATER_DISINFECTION_7SU = DataTag(["D159"], "", writeable=True)

    TEMPERATURE_WATER_SETPOINT_FOR_SOLAR = DataTag(["A169"], "°C", writeable=True)
    # Changeover temperature to extern heating when exceeding T hot water
    # Umschalttemperatur ext. Waermeerzeuger bei Ueberschreitung der T Warmwasser
    TEMPERATURE_WATER_CHANGEOVER_EXT_HOTWATER = DataTag(["A1019"], "°C", writeable=True)
    # Changeover temperature to extern heating when exceeding T flow
    # Umschalttemperatur ext. Waermeerzeuger bei Ueberschreitung der T Vorlauf
    TEMPERATURE_WATER_CHANGEOVER_EXT_FLOW = DataTag(["A1249"], "°C", writeable=True)
    TEMPERATURE_WATER_POWLIMIT_MAX = DataTag(["A171"], "%", writeable=True)
    TEMPERATURE_WATER_POWLIMIT_MIN = DataTag(["A172"], "%", writeable=True)

    TEMPERATURE_POOL = DataTag(["A20"], "°C")
    TEMPERATURE_POOL_DEMAND = DataTag(["A40"], "°C")
    TEMPERATURE_POOL_ADJUST = DataTag(["I1740"], "K", writeable=True)
    TEMPERATURE_POOL_SETPOINT = DataTag(["A41"], "°C", writeable=True)
    TEMPERATURE_POOL_HYSTERESIS = DataTag(["A174"], "K", writeable=True)
    TEMPERATURE_POOL_PV_CHANGE = DataTag(["A685"], "K", writeable=True)
    TEMPERATURE_POOL_HC_OUTDOOR_1H = DataTag(["A746"], "°C")
    TEMPERATURE_POOL_HC_LIMIT = DataTag(["A749"], "°C", writeable=True)
    TEMPERATURE_POOL_HC_TARGET = DataTag(["A750"], "°C", writeable=True)
    TEMPERATURE_POOL_HC_OUTDOOR_NORM = DataTag(["A747"], "°C", writeable=True)
    TEMPERATURE_POOL_HC_NORM = DataTag(["A748"], "°C", writeable=True)
    TEMPERATURE_POOL_HC_RESULT = DataTag(["A752"], "°C")

    TEMPERATURE_MIX1 = DataTag(["A44"], "°C")  # TEMPERATURE_MIXING1_CURRENT
    TEMPERATURE_MIX1_DEMAND = DataTag(["A45"], "°C")  # TEMPERATURE_MIXING1_SET
    TEMPERATURE_MIX1_ADJUST = DataTag(["I776"], "K", writeable=True)  # ADAPT_MIXING1
    TEMPERATURE_MIX1_PV_CHANGE = DataTag(["A1094"], "K", writeable=True)
    TEMPERATURE_MIX1_PERCENT = DataTag(["A510"], "%")
    TEMPERATURE_MIX1_HC_LIMIT = DataTag(["A276"], "°C", writeable=True)  # T_HEATING_LIMIT_MIXING1
    TEMPERATURE_MIX1_HC_TARGET = DataTag(["A277"], "°C", writeable=True)  # T_HEATING_LIMIT_TARGET_MIXING1
    TEMPERATURE_MIX1_HC_OUTDOOR_NORM = DataTag(["A274"], "°C", writeable=True)  # T_NORM_OUTDOOR_MIXING1
    TEMPERATURE_MIX1_HC_HEATING_NORM = DataTag(["A275"], "°C", writeable=True)  # T_NORM_HEATING_CICLE_MIXING1
    TEMPERATURE_MIX1_HC_MAX = DataTag(["A278"], "°C", writeable=True)  # MAX_TEMP_MIXING1

    TEMPERATURE_MIX2 = DataTag(["A46"], "°C")  # TEMPERATURE_MIXING2_CURRENT
    TEMPERATURE_MIX2_DEMAND = DataTag(["A47"], "°C")  # TEMPERATURE_MIXING2_SET
    TEMPERATURE_MIX2_ADJUST = DataTag(["I896"], "K", writeable=True)  # ADAPT_MIXING2
    TEMPERATURE_MIX2_PV_CHANGE = DataTag(["A1095"], "K", writeable=True)
    TEMPERATURE_MIX2_PERCENT = DataTag(["A512"], "%")
    TEMPERATURE_MIX2_HC_LIMIT = DataTag(["A322"], "°C", writeable=True)
    TEMPERATURE_MIX2_HC_TARGET = DataTag(["A323"], "°C", writeable=True)
    TEMPERATURE_MIX2_HC_OUTDOOR_NORM = DataTag(["A320"], "°C", writeable=True)
    TEMPERATURE_MIX2_HC_HEATING_NORM = DataTag(["A321"], "°C", writeable=True)
    TEMPERATURE_MIX2_HC_MAX = DataTag(["A324"], "°C", writeable=True)

    TEMPERATURE_MIX3 = DataTag(["A48"], "°C")  # TEMPERATURE_MIXING3_CURRENT
    TEMPERATURE_MIX3_DEMAND = DataTag(["A49"], "°C")  # TEMPERATURE_MIXING3_SET
    TEMPERATURE_MIX3_ADJUST = DataTag(["I1017"], "K", writeable=True)  # ADAPT_MIXING3
    TEMPERATURE_MIX3_PV_CHANGE = DataTag(["A1096"], "K", writeable=True)
    TEMPERATURE_MIX3_PERCENT = DataTag(["A514"], "%")
    TEMPERATURE_MIX3_HC_LIMIT = DataTag(["A368"], "°C", writeable=True)
    TEMPERATURE_MIX3_HC_TARGET = DataTag(["A369"], "°C", writeable=True)
    TEMPERATURE_MIX3_HC_OUTDOOR_NORM = DataTag(["A366"], "°C", writeable=True)
    TEMPERATURE_MIX3_HC_HEATING_NORM = DataTag(["A367"], "°C", writeable=True)
    TEMPERATURE_MIX3_HC_MAX = DataTag(["A370"], "°C", writeable=True)

    # no information found in <host>/easycon/js/dictionary.js
    # COMPRESSOR_POWER = DataTag(["A50"], "?°C")
    PERCENT_HEAT_CIRC_PUMP = DataTag(["A51"], "%")
    PERCENT_SOURCE_PUMP = DataTag(["A52"], "%")
    # A58 is listed as 'Power compressor' in <host>/easycon/js/dictionary.js
    # even if this value will not be displayed in the Waterkotte GUI - looks
    # like that this is really the same as the other two values (A51 & A52)
    # just a percentage value (from 0.0 - 100.0)
    PERCENT_COMPRESSOR_DEMAND = DataTag(["A50"], "%")
    PERCENT_COMPRESSOR = DataTag(["A58"], "%")
    PERCENT_COMPRESSOR2 = DataTag(["A703"], "%")
    PERCENT_COMPRESSOR3 = DataTag(["A704"], "%")
    PERCENT_COMPRESSOR4 = DataTag(["A705"], "%")

    # just found... Druckgastemperatur
    TEMPERATURE_DISCHARGE = DataTag(["A1462"], "°C")

    # implement https://github.com/marq24/ha-waterkotte/issues/3
    PRESSURE_WATER = DataTag(["A1669"], "bar")

    # I1264 -> Heizstab Leistung?! -> 6000

    # keep but not found in Waterkotte GUI
    TEMPERATURE_COLLECTOR = DataTag(["A42"], "°C")  # aktuelle Temperatur Kollektor
    TEMPERATURE_FLOW2 = DataTag(["A43"], "°C")  # aktuelle Temperatur Vorlauf

    VERSION_CONTROLLER = DataTag(["I1", "I2"], decode_f=DataTag._decode_ro_fw)
    # VERSION_CONTROLLER_BUILD = DataTag(["I2"])
    VERSION_BIOS = DataTag(["I3"], decode_f=DataTag._decode_ro_bios)
    DATE_DAY = DataTag(["I5"])
    DATE_MONTH = DataTag(["I6"])
    DATE_YEAR = DataTag(["I7"])
    TIME_HOUR = DataTag(["I8"])
    TIME_MINUTE = DataTag(["I9"])
    OPERATING_HOURS_COMPRESSOR_1 = DataTag(["I10"])
    OPERATING_HOURS_COMPRESSOR_2 = DataTag(["I14"])
    OPERATING_HOURS_CIRCULATION_PUMP = DataTag(["I18"])
    OPERATING_HOURS_SOURCE_PUMP = DataTag(["I20"])
    OPERATING_HOURS_SOLAR = DataTag(["I22"])
    ENABLE_HEATING = DataTag(["I30"], writeable=True, decode_f=DataTag._decode_state, encode_f=DataTag._encode_state)
    ENABLE_COOLING = DataTag(["I31"], writeable=True, decode_f=DataTag._decode_state, encode_f=DataTag._encode_state)
    ENABLE_WARMWATER = DataTag(["I32"], writeable=True, decode_f=DataTag._decode_state, encode_f=DataTag._encode_state)
    ENABLE_POOL = DataTag(["I33"], writeable=True, decode_f=DataTag._decode_state, encode_f=DataTag._encode_state)
    ENABLE_EXTERNAL_HEATER = DataTag(["I35"], writeable=True, decode_f=DataTag._decode_state, encode_f=DataTag._encode_state)
    ENABLE_MIXING1 = DataTag(["I37"], writeable=True, decode_f=DataTag._decode_state, encode_f=DataTag._encode_state)
    ENABLE_MIXING2 = DataTag(["I38"], writeable=True, decode_f=DataTag._decode_state, encode_f=DataTag._encode_state)
    ENABLE_MIXING3 = DataTag(["I39"], writeable=True, decode_f=DataTag._decode_state, encode_f=DataTag._encode_state)
    ENABLE_PV = DataTag(["I41"], writeable=True, decode_f=DataTag._decode_state, encode_f=DataTag._encode_state)

    # UNKNOWN OPERATION-ENABLE Switches!
    ENABLE_X1 = DataTag(["I34"], writeable=True, decode_f=DataTag._decode_state, encode_f=DataTag._encode_state)
    ENABLE_X2 = DataTag(["I36"], writeable=True, decode_f=DataTag._decode_state, encode_f=DataTag._encode_state)
    ENABLE_X4 = DataTag(["I40"], writeable=True, decode_f=DataTag._decode_state, encode_f=DataTag._encode_state)
    ENABLE_X5 = DataTag(["I42"], writeable=True, decode_f=DataTag._decode_state, encode_f=DataTag._encode_state)

    STATE_SOURCEPUMP = DataTag(["I51"], bit=0)
    STATE_HEATINGPUMP = DataTag(["I51"], bit=1)
    STATE_HEATINGPUMP2 = DataTag(["I54"], bit=5)
    STATE_HEATINGPUMP3 = DataTag(["I54"], bit=3)
    STATE_HEATINGPUMP4 = DataTag(["I54"], bit=4)
    STATE_EVD = DataTag(["I51"], bit=2)
    STATE_COMPRESSOR = DataTag(["I51"], bit=3)
    STATE_COMPRESSOR2 = DataTag(["I51"], bit=4)
    STATE_COMPRESSOR3 = DataTag(["I54"], bit=12)
    STATE_COMPRESSOR4 = DataTag(["I54"], bit=13)
    STATE_EXTERNAL_HEATER = DataTag(["I51"], bit=5)
    STATE_ALARM = DataTag(["I51"], bit=6)
    STATE_COOLING = DataTag(["I51"], bit=7)
    STATE_WATER = DataTag(["I51"], bit=8)
    STATE_POOL = DataTag(["I51"], bit=9)
    STATE_SOLAR = DataTag(["I51"], bit=10)
    STATE_SOLAR2 = DataTag(["I51"], bit=11)
    STATE_COOLING4WAY = DataTag(["I51"], bit=12)
    STATE_COOLING4WAY2 = DataTag(["I54"], bit=6)
    STATE_COOLING4WAY3 = DataTag(["I54"], bit=7)
    STATE_COOLING4WAY4 = DataTag(["I54"], bit=8)
    STATE_STORAGEPUMP =  DataTag(["I54"], bit=0)
    STATE_EMERGENCYOFF = DataTag(["I54"], bit=1)
    STATE_EMERGENCYOFF2 = DataTag(["I54"], bit=9)
    STATE_EMERGENCYOFF3 = DataTag(["I54"], bit=10)
    STATE_EMERGENCYOFF4 = DataTag(["I54"], bit=11)
    STATE_SILENTMODE = DataTag(["I54"], bit=2)
    STATE_MIX1_PUMP = DataTag(["I51"], bit=13)
    STATE_MIX1_MIXER_OPEN = DataTag(["I51"], bit=14)
    STATE_MIX1_MIXER_CLOSE = DataTag(["I51"], bit=15)
    STATE_ENGINEVENT = DataTag(["I54"], bit=14)

    # https://github.com/flautze/home_assistant_waterkotte/issues/1#issuecomment-1916288553
    INTERRUPTION_BITS = DataTag(["I53"], bits=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], translate=True)
    ALARM_BITS = DataTag(["I52", "I2608", "I2609", "I2610", "I2611", "I2612", "I2613", "I2614"], decode_f=DataTag._decode_alarms)

    # when we are logged in as ServiceOperator, then I135 return 1 -> in the FE this will be set the currentUserLevel
    # 1: Service
    # 2: Werksebene
    # 3: Entwickler
    STATE_SERVICE = DataTag(["I135"])

    STATUS_HEATING = DataTag(["I137"], decode_f=DataTag._decode_status)
    STATUS_COOLING = DataTag(["I138"], decode_f=DataTag._decode_status)
    STATUS_WATER = DataTag(["I139"], decode_f=DataTag._decode_status)
    STATUS_POOL = DataTag(["I140"], decode_f=DataTag._decode_status)
    STATUS_SOLAR = DataTag(["I141"], decode_f=DataTag._decode_status)
    # returned 2='disabled' (even if the pump is running) - could be, that this TAG has to be set to 1='on' in order
    # to allow manual enable/disable the pump??? So it's then better to rename this then operation_mode and move it to
    # the switch section [just like the 'ENABLE_*' tags]
    STATUS_HEATING_CIRCULATION_PUMP = DataTag(["I1270"], decode_f=DataTag._decode_status)
    MANUAL_SOURCEPUMP = DataTag(["I1281"])
    # see STATUS_HEATING_CIRCULATION_PUMP
    STATUS_SOLAR_CIRCULATION_PUMP = DataTag(["I1287"], decode_f=DataTag._decode_status)
    MANUAL_SOLARPUMP1 = DataTag(["I1287"])
    MANUAL_SOLARPUMP2 = DataTag(["I1289"])
    # see STATUS_HEATING_CIRCULATION_PUMP
    STATUS_BUFFER_TANK_CIRCULATION_PUMP = DataTag(["I1291"], decode_f=DataTag._decode_status)
    MANUAL_VALVE = DataTag(["I1293"])
    MANUAL_POOLVALVE = DataTag(["I1295"])
    MANUAL_COOLVALVE = DataTag(["I1297"])
    MANUAL_4WAYVALVE = DataTag(["I1299"])
    # see STATUS_HEATING_CIRCULATION_PUMP
    STATUS_COMPRESSOR = DataTag(["I1307"], decode_f=DataTag._decode_status)
    MANUAL_MULTIEXT = DataTag(["I1319"])

    INFO_SERIES = DataTag(["I105"], decode_f=DataTag._decode_ro_series)
    INFO_ID = DataTag(["I110"], decode_f=DataTag._decode_ro_id)
    INFO_SERIAL = DataTag(["I114", "I115"], decode_f=DataTag._decode_ro_sn)
    ADAPT_HEATING = DataTag(["I263"], writeable=True)

    STATE_BLOCKING_TIME = DataTag(["D71"])
    STATE_TEST_RUN = DataTag(["D581"])

    # SERVICE_HEATING = DataTag(["D251"])
    # SERVICE_COOLING = DataTag(["D252"])
    # SERVICE_WATER = DataTag(["D117"])
    # SERVICE_HEATING_D23 = DataTag(["D23"])
    # SERVICE_HEATING_SCHEDULE D24 = DataTag(["D24"])
    # SERVICE_WATER_D118 = DataTag(["D118"])
    # SERVICE_OPMODE = DataTag(["I136"])
    # RAW_D430 = DataTag(["D430"])  # animation
    # RAW_D28 = DataTag(["D28"])  # ?QE
    # RAW_D879 = DataTag(["D879"])  # ?RMH
    # MODE_HEATING_PUMP = DataTag(["A522"])
    # MODE_HEATING = DataTag(["A530"])
    # MODE_HEATING_EXTERNAL = DataTag(["A528"])
    # MODE_COOLING = DataTag(["A532"])
    # MODE_WATER = DataTag(["A534"])
    # MODE_POOL = DataTag(["A536"])
    # MODE_SOLAR = DataTag(["A538"])

    # found on the "extended" Tab in the Waterkotte WebGui
    # (all values can be read/write) - no clue about the unit yet
    # reading the values always returned '0' -> so I guess they have
    # no use for us?!
    # ENERGY_THERMAL_WORK_1 = DataTag("I1923")
    # ENERGY_THERMAL_WORK_2 = DataTag("I1924")
    # ENERGY_COOLING = DataTag("I1925")
    # ENERGY_HEATING = DataTag("I1926")
    # ENERGY_HOT_WATER = DataTag("I1927")
    # ENERGY_POOL_HEATER = DataTag("I1928")
    # ENERGY_COMPRESSOR = DataTag("I1929")
    # ENERGY_HEAT_SOURCE_PUMP = DataTag("I1930")
    # ENERGY_EXTERNAL_HEATER = DataTag("I1931")

    # D1273 "Heizungsumwäzpumpe ET 6900 Q" does not change it's value
    # HEATING_CIRCULATION_PUMP_D1273 = DataTag(["D1273"], writeable=True)
    STATE_HEATING_CIRCULATION_PUMP_D425 = DataTag(["D425"])
    STATE_BUFFERTANK_CIRCULATION_PUMP_D377 = DataTag(["D377"])
    STATE_POOL_CIRCULATION_PUMP_D549 = DataTag(["D549"])
    STATE_MIX1_CIRCULATION_PUMP_D248 = DataTag(["D248"])
    STATE_MIX2_CIRCULATION_PUMP_D291 = DataTag(["D291"])
    STATE_MIX3_CIRCULATION_PUMP_D334 = DataTag(["D334"])
    # alternative MIX pump tags...
    STATE_MIX1_CIRCULATION_PUMP_D563 = DataTag(["D563"])
    STATE_MIX2_CIRCULATION_PUMP_D564 = DataTag(["D564"])
    STATE_MIX3_CIRCULATION_PUMP_D565 = DataTag(["D565"])

    PERMANENT_HEATING_CIRCULATION_PUMP_WINTER_D1103 = DataTag(["D1103"], writeable=True)
    PERMANENT_HEATING_CIRCULATION_PUMP_SUMMER_D1104 = DataTag(["D1104"], writeable=True)

    # lngA520 = ["Vollbetriebsstunden", "Operating hours", "Heures activit\xe9"],

    # assuming that I1752 will be set to "Spreizung"=0 the A479 is a DELTA Temperature
    # lngA479 = ΔT Wärmequelle - ["T Wärmequelle", "T heat source", "T captage"],
    # REPLACED by PUMPSERVICE_SOURCEPUMP_HEATMODE_SOURCE_TEMPERATURE_A479
    # SOURCE_PUMP_CAPTURE_TEMPERATURE_A479 = DataTag(["A479"], writeable=True)

    SGREADY_SWITCH_D795 = DataTag(["D795"], writeable=True)
    # lngD796 = ["SG1: EVU-Sperre", "SG1: Extern switch off", "SG1: Coupure externe"],
    SGREADY_SG1_EXTERN_OFF_SWITCH_D796 = DataTag(["D796"])
    # lngD797 = ["SG2: Normalbetrieb", "SG2: Normal operation", "SG2: Fonction normal"],
    SGREADY_SG2_NORMAL_D797 = DataTag(["D797"])
    # lngD798 = ["SG3: Sollwerterh.", "SG3: Setpoint change", "SG3: Augment. consigne"],
    SGREADY_SG3_SETPOINT_CHANGE_D798 = DataTag(["D798"])
    # lngD799 = ["SG4: Zwangslauf", "SG4: Forced run", "SG4: Marche forc\xe9e"],
    SGREADY_SG4_FORCE_RUN_D799 = DataTag(["D799"])

    ##################################################################################
    # BASICVENT / ECOVENT Stuff...
    # PID-Regler: Proportional-Integral-Differenzial-Regler
    ##################################################################################
    # A4387: uom: '', 'Energieersparnis gesamt'
    BASICVENT_ENERGY_SAVE_TOTAL_A4387 = DataTag(["A4387"], decode_f=DataTag._decode_value_analog)
    # A4389: uom: '', 'Energieersparnis aktuell'
    BASICVENT_ENERGY_SAVE_CURRENT_A4389 = DataTag(["A4389"], decode_f=DataTag._decode_value_analog)
    # A4391: uom: '', 'Wärmerückgewinnungsgrad'
    BASICVENT_ENERGY_RECOVERY_RATE_A4391 = DataTag(["A4391"], decode_f=DataTag._decode_value_analog)
    # A4498: uom: 'Tage', 'Luftfilter Wechsel Betriebsstunden'
    BASICVENT_FILTER_CHANGE_OPERATING_DAYS_A4498 = DataTag(["A4498"], decode_f=DataTag._decode_value_analog)
    # A4504: uom: 'Tage', 'Luftfilter Wechsel Betriebsstunden Restlaufzeit dd'
    BASICVENT_FILTER_CHANGE_REMAINING_OPERATING_DAYS_A4504 = DataTag(["A4504"], decode_f=DataTag._decode_value_analog)
    # D1544: uom: '', 'Luftfilter Wechsel Betriebsstunden Reset'
    BASICVENT_FILTER_CHANGE_OPERATING_HOURS_RESET_D1544 = DataTag(["D1544"], writeable=True)
    # D1469: uom: '', 'Luftfilter Wechselanzeige'
    BASICVENT_FILTER_CHANGE_DISPLAY_D1469 = DataTag(["D1469"])
    # D1626: uom: '', 'Luftfilter Wechselanzeige Animation'
    # BASICVENT_FILTER_CHANGE_DISPLAY_ANIMATION_D1626 = DataTag(["D1626"])

    # A4506: uom: '', 'Hu Luftfeuchtigkeit PID'
    # BASICVENT_HUMIDITY_SETPOINT_A4506 = DataTag(["A4506"], writeable=True, decode_f=DataTag._decode_value_analog)
    # A4508: uom: '', 'Hu Luftfeuchtigkeit Sollwert'
    # BASICVENT_HUMIDITY_DEMAND_A4508 = DataTag(["A4508"], decode_f=DataTag._decode_value_analog)
    # A4510: uom: '', 'Hu Luftfeuchtigkeit'
    # BASICVENT_HUMIDITY_SECOND_VALUE_A4510 = DataTag(["A4510"], decode_f=DataTag._decode_value_analog)
    # A4990: uom: '', 'Luftfeuchtigkeit'
    BASICVENT_HUMIDITY_VALUE_A4990 = DataTag(["A4990"], decode_f=DataTag._decode_value_analog)

    # A4512: uom: '', 'CO2-Konzentration PID'
    # BASICVENT_CO2_SETPOINT_A4512 = DataTag(["A4512"], writeable=True, decode_f=DataTag._decode_value_analog)
    # A4514: uom: '', 'CO2-Konzentration Sollwert'
    # BASICVENT_CO2_DEMAND_A4514 = DataTag(["A4514"], decode_f=DataTag._decode_value_analog)
    # A4516: uom: '', 'CO2-Konzentration'
    # BASICVENT_CO2_SECOND_VALUE_A4516 = DataTag(["A4516"], decode_f=DataTag._decode_value_analog)
    # A4992: uom: '', 'CO2'
    BASICVENT_CO2_VALUE_A4992 = DataTag(["A4992"], decode_f=DataTag._decode_value_analog)

    # A4518: uom: '', 'VOC Kohlenwasserstoffverbindungen PID'
    # BASICVENT_VOC_SETPOINT_A4518 = DataTag(["A4518"], writeable=True, decode_f=DataTag._decode_value_analog)
    # A4520: uom: '', 'VOC Kohlenwasserstoffverbindungen Sollwert'
    # BASICVENT_VOC_DEMAND_A4520 = DataTag(["A4520"], decode_f=DataTag._decode_value_analog)
    # A4522: uom: '', 'VOC Kohlenwasserstoffverbindungen'
    BASICVENT_VOC_VALUE_A4522 = DataTag(["A4522"], decode_f=DataTag._decode_value_analog)

    # I4523: uom: '', 'Luftqualitaet Messung VOC CO2 Sensor'

    # I4582: uom: '', opts: { type:'select', options: ['Tag','Nacht','Zeitprogramm','Party','Urlaub','Bypass'] }, 'i_Mode'
    BASICVENT_OPERATION_MODE_I4582 = DataTag(
        ["I4582"], writeable=True, decode_f=DataTag._decode_six_steps_mode, encode_f=DataTag._encode_six_steps_mode)

    # mdi:air-filter
    # mdi:hvac
    # mdi:wind-power

    # A4549: uom: '', 'Luefter 1 Rueckmeldung'
    BASICVENT_INCOMING_FAN_FEEDBACK_A4549 = DataTag(["A4549"])
    # D1605: uom: '', 'Luefter 1 - Manuell Drehzahl'
    BASICVENT_INCOMING_FAN_MANUAL_MODE = DataTag(["3:HREG400447"], writeable=True)
    BASICVENT_INCOMING_FAN_MANUAL_SPEED_PERCENT = DataTag(["3:HREG400443"], writeable=True)
    # A4551: uom: 'U/min', 'Luefter 1 Umdrehungen pro Minute'
    BASICVENT_INCOMING_FAN_RPM_A4551 = DataTag(["A4551"], decode_f=DataTag._decode_value_analog)
    # A4986: uom: '%', 'Analogausgang Y1' - Rotation Incoming air drive percent
    BASICVENT_INCOMING_FAN_A4986 = DataTag(["A4986"], decode_f=DataTag._decode_value_analog)
    # A5000: uom: '', 'T1' - Außenluft/Frischluft - Outdoor air
    BASICVENT_TEMPERATURE_INCOMING_AIR_BEFORE_ODA_A5000 = DataTag(["A5000"], decode_f=DataTag._decode_value_analog)
    # A4996: uom: '', 'T3' - Zuluft - Supply air
    BASICVENT_TEMPERATURE_INCOMING_AIR_AFTER_SUP_A4996 = DataTag(["A4996"], decode_f=DataTag._decode_value_analog)

    # A4545: uom: '', 'Luefter 2 Rueckmeldung'
    BASICVENT_OUTGOING_FAN_FEEDBACK_A4545 = DataTag(["A4545"])
    # D1603: uom: '', 'Luefter 2 - Manuell Drehzahl'
    BASICVENT_OUTGOING_FAN_MANUAL_MODE = DataTag(["3:HREG400448"], writeable=True)
    BASICVENT_OUTGOING_FAN_MANUAL_SPEED_PERCENT = DataTag(["3:HREG400445"], writeable=True)
    # A4547: uom: 'U/min', 'Luefter 2 Umdrehungen pro Minute'
    BASICVENT_OUTGOING_FAN_RPM_A4547 = DataTag(["A4547"], decode_f=DataTag._decode_value_analog)
    # A4984: uom: '%', 'Analogausgang Y2' - Rotation Ongoing air drive percent
    BASICVENT_OUTGOING_FAN_A4984 = DataTag(["A4984"], decode_f=DataTag._decode_value_analog)
    # A4998: uom: '', 'T2' -> Abluft - Extract air
    BASICVENT_TEMPERATURE_OUTGOING_AIR_BEFORE_ETH_A4998 = DataTag(["A4998"], decode_f=DataTag._decode_value_analog)
    # A4994: uom: '', 'T4' -> Fortluft - Exhaust air
    BASICVENT_TEMPERATURE_OUTGOING_AIR_AFTER_EEH_A4994 = DataTag(["A4994"], decode_f=DataTag._decode_value_analog)

    # D1432: uom: '', 'Bypass Aktiv' -
    BASICVENT_STATUS_BYPASS_ACTIVE_D1432 = DataTag(["D1432"])
    # D1433: uom: '', 'HU En'
    BASICVENT_STATUS_HUMIDIFIER_ACTIVE_D1433 = DataTag(["D1433"])
    # D1465: uom: '', 'Comfort-Bypass'
    BASICVENT_STATUS_COMFORT_BYPASS_ACTIVE_D1465 = DataTag(["D1465"])
    # D1466: uom: '', 'Smartbypass'
    BASICVENT_STATUS_SMART_BYPASS_ACTIVE_D1466 = DataTag(["D1466"])
    # D1503: uom: '', 'Holiday enabled'
    BASICVENT_STATUS_HOLIDAY_ENABLED_D1503 = DataTag(["D1503"])

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

    ###############################
    ###############################
    #### from ioBroker impl... ####
    ###############################
    ###############################
    # ignore D74     coolingIndicatorState = getServiceIndicator('D74'); -> ['Kühlbetrieb'];
    # ignore D75     getIndicator(coolingStatus, 'D75')); -> Kühlbetrieb Zeitprogram
    # ignore D160    poolIndicatorState = getServiceIndicator('D160'); -> ['Pool-Heizbetrieb'];
    # ignore D196    solarIndicatorState = getServiceIndicator('D196'); -> ['Solarbetrieb'];
    # ignore D232    extHeaterIndicatorState = getServiceIndicator('D232'); -> ['Ext. Wärmeerzeuger'];
    # ignore D635    pvIndicatorState = getServiceIndicator('D635'); -> ['Photovoltaik'];

    # HEATING ROOM INFLUENCE Settings... MAIN question tag A101 - will it be witten as A101 or as I264 ???!
    # A98	    getReadOnlyState(heatingInfluence, 'A98', '°C')); -> ['Raumtemperatur Ø1h', 'T room 1h', 'T-pi\xe8ce 1h'];
    TEMPERATURE_ROOM_TARGET = DataTag(["A100"], "°C", writeable=True)  # from 15°C - 30°C
    ROOM_INFLUENCE = DataTag(["A101"], "%", writeable=True)  # not really writable?!
    # <select id="I264" class="form-control" style="width: 100px; color: rgb(85, 85, 85);">
    #    <option value="0">0%</option>
    #    <option value="1">50%</option>
    #    <option value="2">100%</option>
    #    <option value="3">150%</option>
    #    <option value="4">200%</option>
    # </select>
    # A102    getState(heatingInfluence, 'A102', '+/-30 K')); -> ['kleinster Wert'];
    # A103    getState(heatingInfluence, 'A103', '+/-30 K')); -> ['grösster Wert'];
    # ignore A99     getReadOnlyState(heatingInfluence, 'A99', 'K')); -> ['aktueller Wert'];

    # THERMAL DESINFECTION MODE: NONE, (selected) DAYs, ALL
    # ignore I508	getEnumState(waterThermalDis, 'I508', dict.noneDayAll)); -> ['Wochenprogramm', 'Schedule', 'Programme hebdomadaire'];

    # HOT WATER - SOLAR-SUPPORT Values
    # A169 -> TEMPERATURE_WATER_SETPOINT_FOR_SOLAR
    # ignore I517	getState(waterSolarSupp, 'I517', '')); -> ['Verzögerung Kompressorstart', 'Delay for compressor during solar heating', 'Temps de retard pour Start compresseur',
    # ignore I518	getReadOnlyState(waterSolarSupp, 'I518')); -> ['Zeit bis Kompressorstart', 'Compressor starting in...', 'Le compresseur d\xe9marre dans'];

    # SOLAR SUPPORT -> pgSolar.html
    # A205	getState(solarSettings, 'A205', 'K')); -> ['Einschalttemperaturdifferenz', 'Switch on temperature difference', "Diff\xe9rence de temp\xe9rature d'enclenchement",
    # A206	getState(solarSettings, 'A206', 'K')); -> ['Ausschalttemperaturdifferenz', 'Switch off temperature difference',"Diff\xe9rence de temp\xe9rature d'arr\xeat",
    # A207	getState(solarSettings, 'A207', 'K')); -> ['Maximale Kollektortemperatur', 'Maximum collector temperature','Temp\xe9rature maximale du collecteur',
    # A209	getReadOnlyState(solarSettings, 'A209', '°C')); -> ['geforderte Temperatur Vorlauf', 'Required temperature flow', 'Consigne d\xe9part'];
    # SOLAR SUPORT REGENERATION
    # A686	getReadOnlyState(solarRegen, 'A686', '°C')); -> ['Sondentemperatur'];
    # A687	getState(solarRegen, 'A687', '°C')); -> ['Max. Sonden Temperatur'];
    # A688	getState(solarRegen, 'A688', 'K')); -> ['Schaltdifferenz max. Temperatur'];
    # I2253	getEnumState(solarRegen, 'I2253', "OPEN" or "CLOSED")); -> ['Motorventil Warmwasser bei Sonden Regenerierung'];

    # PV SUPPORT (there is much much more!
    # A1223	getReadOnlyState(pvSettings, 'A1223', 'kW')); -> ['Photovoltaik Überschuss'];
    # A1194	getReadOnlyState(pvSettings, 'A1194', 'kW')); -> ['15 Min.-Mittelwert der Netzeinspeisung'];
    # A1224	getReadOnlyState(pvSettings, 'A1224', 'kW')); -> ['Einschaltgrenzwert für PV'];

    PREASSURE_P1_SUCTION_GAS_I2017 = DataTag(["I2017"], "bar")  # -> ['p1 Sauggas'];
    PREASSURE_P2_EXIT_I2018 = DataTag(["I2018"], "bar")  # -> ['p2 Austritt'];
    PREASSURE_P3_INTERMEDIATE_INJECTION_I2019 = DataTag(["I2019"], "bar")  # -> ['p3 Zwischeneinspritzung'];
    TEMPERATURE_T2_SURROUNDING_I2020 = DataTag(["I2020"], "°C")  # -> ['T2 Umgebung'];
    TEMPERATURE_T3_SUCTION_GAS_I2021 = DataTag(["I2021"], "°C")  # -> ['T3 Sauggas'];
    TEMPERATURE_T4_COMPRESSOR_I2022 = DataTag(["I2022"], "°C")  # -> ['T4 Verdichter'];
    TEMPERATURE_T5_EVI_I2025 = DataTag(["I2025"], "°C")  # -> ['T5 EVI'];
    TEMPERATURE_T6_FLUID_I2024 = DataTag(["I2024"], "°C")  # -> ['T6 Flüssig'];
    TEMPERATURE_T7_OIL_SUMP_I2023 = DataTag(["I2023"], "°C")  # -> ['T7 Ölsumpf'];
    TEMPERATURE_EVAPORATOR_I2032 = DataTag(["I2032"], "°C")  # -> ['T Verdampfer'];
    TEMPERATURE_OVERHEATING_I2033 = DataTag(["I2033"], "°K")  # -> ['Überhitzung'];
    TEMPERATURE_CONDENTATION_I2034 = DataTag(["I2034"], "°C")  # ['T Kondensation'];
    TEMPERATURE_COMPRESSED_GAS_I2039 = DataTag(["I2039"], "°C")  # -> ['T Druckgas'];
    FLOW_VORTEX_SENSOR_A1022 = DataTag(["A1022"], "l/s")  # -> ['Durchfluss (Vortex Sensor)'];
    TEMPERATURE_VORTEX_SENSOR_A1023 = DataTag(["A1023"], "°C")  # -> ['Temperatur (Vortex Sensor)'];

    # pgService_IO
    # D815	getIndicator(statusDI, 'D815')); -> ['SM Quellenseite'];
    # D816	getIndicator(statusDI, 'D816')); -> ['SM Heizungsseite'];
    # D817	getIndicator(statusDI, 'D817')); -> ['SG Ready-A/ EVU'];
    # D818	getIndicator(statusDI, 'D818')); -> ['SG Ready-B/ Sollwert'];
    # D821	getIndicator(statusDI, 'D821')); -> ['HD-Pressostat'];
    # D822	getIndicator(statusDI, 'D822')); -> ['ND-Pressostat'];
    # D823	getIndicator(statusDI, 'D823')); -> ['Motorschutz 1'];
    # D824	getIndicator(statusDI, 'D824')); -> ['Motorschutz 2'];
    # D1010	getIndicator(statusDI, 'D1010')); -> ['SM Phase/Drehf.'];

    # A699	getReadOnlyState(measurements, 'A699', '°C')); -> UNKNOWN
    # A700	getReadOnlyState(measurements, 'A700', '°C')); -> UNKNOWN
    # A701	getReadOnlyState(measurements, 'A701', '°C')); -> UNKNOWN
    # A702	getReadOnlyState(measurements, 'A702', '°C')); -> UNKNOWN
    # D701	getIndicator(status, 'D701')); -> UNKNOWN


    # pgService_Pump

    # Quellenpumpe
    PUMPSERVICE_SOURCEPUMP_I1281 = DataTag(['I1281'], writeable=True) # Select
    PUMPSERVICE_SOURCEPUMP_MODE_I1764 = DataTag(['I1764'], writeable=True) # Select
    PUMPSERVICE_SOURCEPUMP_CABLE_BREAK_MONITORING_D881 = DataTag(['D881'], writeable=True) # ON/OFF Switch
    PUMPSERVICE_SOURCEPUMP_PRE_RUNTIME_I1278 = DataTag(['I1278'], writeable=True) # Number select TIME Sec (min 25)
    PUMPSERVICE_SOURCEPUMP_POST_RUNTIME_I1279 = DataTag(['I1279'], writeable=True) # Number select TIME Sec
    PUMPSERVICE_SOURCEPUMP_ANTI_JAMMING_I1280 = DataTag(['I1280'], writeable=True) # Number select TIME Sec

    # Erweiterte Einstellungen für die Baureihe ET 6900
    # D1273 - Heizungsumw\xe4lzpumpe ET 6900 Q
    # <option value="0">Single</option>
    # <option value="1">Duo</option>
    # D1274 - Quellenpumpe ET 6900 Q
    # <option value="0">Single</option>
    # <option value="1">Duo</option>

    # Wärmequellenregeneration
    # D1294 - Quellenpumpe Regeneration
    PUMPSERVICE_SOURCEPUMP_REGENERATION_D1294 = DataTag(['D1294'], writeable=True) # Switch ON/OFF
    # A1539 - T Quelle ein < : -50.00 - +50.00 °C
    PUMPSERVICE_SOURCEPUMP_TEMP_ON_LOWER_A1539 = DataTag(['A1539'], writeable=True) # Number range -50/+50°C

    # Heizbetrieb
    PUMPSERVICE_SOURCEPUMP_HEATMODE_REGULATION_BY_I1752 = DataTag(['I1752'], writeable=True) # select
    PUMPSERVICE_SOURCEPUMP_HEATMODE_CONTROL_BEHAVIOUR_D789 = DataTag(['D789'], writeable=True) # select
    PUMPSERVICE_SOURCEPUMP_HEATMODE_REGULATION_START_D996 = DataTag(['D996'], writeable=True) # select
    PUMPSERVICE_SOURCEPUMP_HEATMODE_MINSPEED_A485 = DataTag(['A485'], writeable=True) # Number range 0-100%
    PUMPSERVICE_SOURCEPUMP_HEATMODE_MAXSPEED_A486 = DataTag(['A486'], writeable=True) # Number range 0-100%
    PUMPSERVICE_SOURCEPUMP_HEATMODE_SOURCE_TEMPERATURE_A479 = DataTag(['A479'], writeable=True) # Number range 0-50 °K

    # Kühlbetrieb
    PUMPSERVICE_SOURCEPUMP_COOLINGMODE_REGULATION_BY_I2102 = DataTag(['I2102'], writeable=True) # select
    PUMPSERVICE_SOURCEPUMP_COOLINGMODE_CONTROL_BEHAVIOUR_D995 = DataTag(['D995'], writeable=True) # select
    PUMPSERVICE_SOURCEPUMP_COOLINGMODE_REGULATION_START_D997 = DataTag(['D997'], writeable=True) # select
    PUMPSERVICE_SOURCEPUMP_COOLINGMODE_MINSPEED_A1032 = DataTag(['A1032'], writeable=True) # Number range 0-100%
    PUMPSERVICE_SOURCEPUMP_COOLINGMODE_MAXSPEED_A1033 = DataTag(['A1033'], writeable=True) # Number range 0-100%
    PUMPSERVICE_SOURCEPUMP_COOLINGMODE_SOURCE_TEMPERATURE_A1034 = DataTag(['A1034'], writeable=True) # Number range 0-50 °C

    # PID-Control...

    #####################################
    #####################################
    #####################################
    # TIME SCHEDULING (Thanks @flautze) #
    #####################################
    #####################################
    #####################################
    # _1MO, _2TU, _3WE, _4TH, _5FR, _6SA, _7SU
    SCHEDULE_HEATING_1MO_ENABLE = DataTag(['D42'], writeable=True)
    SCHEDULE_HEATING_1MO_START_TIME = DataTag(
        ['I151', 'I179'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_HEATING_1MO_END_TIME = DataTag(
        ['I207', 'I235'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_HEATING_1MO_ADJUST1_ENABLE = DataTag(['D43'], writeable=True)
    SCHEDULE_HEATING_1MO_ADJUST1_VALUE = DataTag(['A63'], writeable=True)
    SCHEDULE_HEATING_1MO_ADJUST1_START_TIME = DataTag(
        ['I152', 'I180'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_HEATING_1MO_ADJUST1_END_TIME = DataTag(
        ['I208', 'I236'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_HEATING_1MO_ADJUST2_ENABLE = DataTag(['D44'], writeable=True)
    SCHEDULE_HEATING_1MO_ADJUST2_VALUE = DataTag(['A64'], writeable=True)
    SCHEDULE_HEATING_1MO_ADJUST2_START_TIME = DataTag(
        ['I153', 'I181'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_HEATING_1MO_ADJUST2_END_TIME = DataTag(
        ['I209', 'I237'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_HEATING_2TU_ENABLE = DataTag(['D46'], writeable=True)
    SCHEDULE_HEATING_2TU_START_TIME = DataTag(
        ['I155', 'I183'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_HEATING_2TU_END_TIME = DataTag(
        ['I211', 'I239'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_HEATING_2TU_ADJUST1_ENABLE = DataTag(['D47'], writeable=True)
    SCHEDULE_HEATING_2TU_ADJUST1_VALUE = DataTag(['A67'], writeable=True)
    SCHEDULE_HEATING_2TU_ADJUST1_START_TIME = DataTag(
        ['I156', 'I184'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_HEATING_2TU_ADJUST1_END_TIME = DataTag(
        ['I212', 'I240'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_HEATING_2TU_ADJUST2_ENABLE = DataTag(['D48'], writeable=True)
    SCHEDULE_HEATING_2TU_ADJUST2_VALUE = DataTag(['A68'], writeable=True)
    SCHEDULE_HEATING_2TU_ADJUST2_START_TIME = DataTag(
        ['I157', 'I185'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_HEATING_2TU_ADJUST2_END_TIME = DataTag(
        ['I213', 'I241'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_HEATING_3WE_ENABLE = DataTag(['D50'], writeable=True)
    SCHEDULE_HEATING_3WE_START_TIME = DataTag(
        ['I159', 'I187'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_HEATING_3WE_END_TIME = DataTag(
        ['I215', 'I243'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_HEATING_3WE_ADJUST1_ENABLE = DataTag(['D51'], writeable=True)
    SCHEDULE_HEATING_3WE_ADJUST1_VALUE = DataTag(['A71'], writeable=True)
    SCHEDULE_HEATING_3WE_ADJUST1_START_TIME = DataTag(
        ['I160', 'I188'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_HEATING_3WE_ADJUST1_END_TIME = DataTag(
        ['I216', 'I244'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_HEATING_3WE_ADJUST2_ENABLE = DataTag(['D52'], writeable=True)
    SCHEDULE_HEATING_3WE_ADJUST2_VALUE = DataTag(['A72'], writeable=True)
    SCHEDULE_HEATING_3WE_ADJUST2_START_TIME = DataTag(
        ['I161', 'I189'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_HEATING_3WE_ADJUST2_END_TIME = DataTag(
        ['I217', 'I245'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_HEATING_4TH_ENABLE = DataTag(['D54'], writeable=True)
    SCHEDULE_HEATING_4TH_START_TIME = DataTag(
        ['I163', 'I191'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_HEATING_4TH_END_TIME = DataTag(
        ['I219', 'I247'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_HEATING_4TH_ADJUST1_ENABLE = DataTag(['D55'], writeable=True)
    SCHEDULE_HEATING_4TH_ADJUST1_VALUE = DataTag(['A75'], writeable=True)
    SCHEDULE_HEATING_4TH_ADJUST1_START_TIME = DataTag(
        ['I164', 'I192'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_HEATING_4TH_ADJUST1_END_TIME = DataTag(
        ['I220', 'I248'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_HEATING_4TH_ADJUST2_ENABLE = DataTag(['D56'], writeable=True)
    SCHEDULE_HEATING_4TH_ADJUST2_VALUE = DataTag(['A76'], writeable=True)
    SCHEDULE_HEATING_4TH_ADJUST2_START_TIME = DataTag(
        ['I165', 'I193'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_HEATING_4TH_ADJUST2_END_TIME = DataTag(
        ['I221', 'I249'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_HEATING_5FR_ENABLE = DataTag(['D58'], writeable=True)
    SCHEDULE_HEATING_5FR_START_TIME = DataTag(
        ['I167', 'I195'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_HEATING_5FR_END_TIME = DataTag(
        ['I223', 'I251'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_HEATING_5FR_ADJUST1_ENABLE = DataTag(['D59'], writeable=True)
    SCHEDULE_HEATING_5FR_ADJUST1_VALUE = DataTag(['A79'], writeable=True)
    SCHEDULE_HEATING_5FR_ADJUST1_START_TIME = DataTag(
        ['I168', 'I196'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_HEATING_5FR_ADJUST1_END_TIME = DataTag(
        ['I224', 'I252'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_HEATING_5FR_ADJUST2_ENABLE = DataTag(['D60'], writeable=True)
    SCHEDULE_HEATING_5FR_ADJUST2_VALUE = DataTag(['A80'], writeable=True)
    SCHEDULE_HEATING_5FR_ADJUST2_START_TIME = DataTag(
        ['I169', 'I197'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_HEATING_5FR_ADJUST2_END_TIME = DataTag(
        ['I225', 'I253'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_HEATING_6SA_ENABLE = DataTag(['D62'], writeable=True)
    SCHEDULE_HEATING_6SA_START_TIME = DataTag(
        ['I171', 'I199'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_HEATING_6SA_END_TIME = DataTag(
        ['I227', 'I255'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_HEATING_6SA_ADJUST1_ENABLE = DataTag(['D63'], writeable=True)
    SCHEDULE_HEATING_6SA_ADJUST1_VALUE = DataTag(['A83'], writeable=True)
    SCHEDULE_HEATING_6SA_ADJUST1_START_TIME = DataTag(
        ['I172', 'I200'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_HEATING_6SA_ADJUST1_END_TIME = DataTag(
        ['I228', 'I256'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_HEATING_6SA_ADJUST2_ENABLE = DataTag(['D64'], writeable=True)
    SCHEDULE_HEATING_6SA_ADJUST2_VALUE = DataTag(['A84'], writeable=True)
    SCHEDULE_HEATING_6SA_ADJUST2_START_TIME = DataTag(
        ['I173', 'I201'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_HEATING_6SA_ADJUST2_END_TIME = DataTag(
        ['I229', 'I257'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_HEATING_7SU_ENABLE = DataTag(['D66'], writeable=True)
    SCHEDULE_HEATING_7SU_START_TIME = DataTag(
        ['I175', 'I203'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_HEATING_7SU_END_TIME = DataTag(
        ['I231', 'I259'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_HEATING_7SU_ADJUST1_ENABLE = DataTag(['D67'], writeable=True)
    SCHEDULE_HEATING_7SU_ADJUST1_VALUE = DataTag(['A87'], writeable=True)
    SCHEDULE_HEATING_7SU_ADJUST1_START_TIME = DataTag(
        ['I176', 'I204'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_HEATING_7SU_ADJUST1_END_TIME = DataTag(
        ['I232', 'I260'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_HEATING_7SU_ADJUST2_ENABLE = DataTag(['D68'], writeable=True)
    SCHEDULE_HEATING_7SU_ADJUST2_VALUE = DataTag(['A88'], writeable=True)
    SCHEDULE_HEATING_7SU_ADJUST2_START_TIME = DataTag(
        ['I177', 'I205'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_HEATING_7SU_ADJUST2_END_TIME = DataTag(
        ['I233', 'I261'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_COOLING_1MO_ENABLE = DataTag(['D86'], writeable=True)
    SCHEDULE_COOLING_1MO_START_TIME = DataTag(
        ['I276', 'I304'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_COOLING_1MO_END_TIME = DataTag(
        ['I332', 'I360'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_COOLING_1MO_ADJUST1_ENABLE = DataTag(['D87'], writeable=True)
    SCHEDULE_COOLING_1MO_ADJUST1_VALUE = DataTag(['A112'], writeable=True)
    SCHEDULE_COOLING_1MO_ADJUST1_START_TIME = DataTag(
        ['I277', 'I305'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_COOLING_1MO_ADJUST1_END_TIME = DataTag(
        ['I333', 'I361'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_COOLING_1MO_ADJUST2_ENABLE = DataTag(['D88'], writeable=True)
    SCHEDULE_COOLING_1MO_ADJUST2_VALUE = DataTag(['A113'], writeable=True)
    SCHEDULE_COOLING_1MO_ADJUST2_START_TIME = DataTag(
        ['I278', 'I306'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_COOLING_1MO_ADJUST2_END_TIME = DataTag(
        ['I334', 'I362'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_COOLING_2TU_ENABLE = DataTag(['D90'], writeable=True)
    SCHEDULE_COOLING_2TU_START_TIME = DataTag(
        ['I280', 'I308'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_COOLING_2TU_END_TIME = DataTag(
        ['I336', 'I364'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_COOLING_2TU_ADJUST1_ENABLE = DataTag(['D91'], writeable=True)
    SCHEDULE_COOLING_2TU_ADJUST1_VALUE = DataTag(['A116'], writeable=True)
    SCHEDULE_COOLING_2TU_ADJUST1_START_TIME = DataTag(
        ['I281', 'I309'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_COOLING_2TU_ADJUST1_END_TIME = DataTag(
        ['I337', 'I365'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_COOLING_2TU_ADJUST2_ENABLE = DataTag(['D92'], writeable=True)
    SCHEDULE_COOLING_2TU_ADJUST2_VALUE = DataTag(['A117'], writeable=True)
    SCHEDULE_COOLING_2TU_ADJUST2_START_TIME = DataTag(
        ['I282', 'I310'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_COOLING_2TU_ADJUST2_END_TIME = DataTag(
        ['I338', 'I366'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_COOLING_3WE_ENABLE = DataTag(['D94'], writeable=True)
    SCHEDULE_COOLING_3WE_START_TIME = DataTag(
        ['I284', 'I312'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_COOLING_3WE_END_TIME = DataTag(
        ['I340', 'I368'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_COOLING_3WE_ADJUST1_ENABLE = DataTag(['D95'], writeable=True)
    SCHEDULE_COOLING_3WE_ADJUST1_VALUE = DataTag(['A120'], writeable=True)
    SCHEDULE_COOLING_3WE_ADJUST1_START_TIME = DataTag(
        ['I285', 'I313'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_COOLING_3WE_ADJUST1_END_TIME = DataTag(
        ['I341', 'I369'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_COOLING_3WE_ADJUST2_ENABLE = DataTag(['D96'], writeable=True)
    SCHEDULE_COOLING_3WE_ADJUST2_VALUE = DataTag(['A121'], writeable=True)
    SCHEDULE_COOLING_3WE_ADJUST2_START_TIME = DataTag(
        ['I286', 'I314'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_COOLING_3WE_ADJUST2_END_TIME = DataTag(
        ['I342', 'I370'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_COOLING_4TH_ENABLE = DataTag(['D98'], writeable=True)
    SCHEDULE_COOLING_4TH_START_TIME = DataTag(
        ['I288', 'I316'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_COOLING_4TH_END_TIME = DataTag(
        ['I344', 'I372'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_COOLING_4TH_ADJUST1_ENABLE = DataTag(['D99'], writeable=True)
    SCHEDULE_COOLING_4TH_ADJUST1_VALUE = DataTag(['A124'], writeable=True)
    SCHEDULE_COOLING_4TH_ADJUST1_START_TIME = DataTag(
        ['I289', 'I317'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_COOLING_4TH_ADJUST1_END_TIME = DataTag(
        ['I345', 'I373'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_COOLING_4TH_ADJUST2_ENABLE = DataTag(['D100'], writeable=True)
    SCHEDULE_COOLING_4TH_ADJUST2_VALUE = DataTag(['A125'], writeable=True)
    SCHEDULE_COOLING_4TH_ADJUST2_START_TIME = DataTag(
        ['I290', 'I318'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_COOLING_4TH_ADJUST2_END_TIME = DataTag(
        ['I346', 'I374'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_COOLING_5FR_ENABLE = DataTag(['D102'], writeable=True)
    SCHEDULE_COOLING_5FR_START_TIME = DataTag(
        ['I292', 'I320'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_COOLING_5FR_END_TIME = DataTag(
        ['I348', 'I376'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_COOLING_5FR_ADJUST1_ENABLE = DataTag(['D103'], writeable=True)
    SCHEDULE_COOLING_5FR_ADJUST1_VALUE = DataTag(['A128'], writeable=True)
    SCHEDULE_COOLING_5FR_ADJUST1_START_TIME = DataTag(
        ['I293', 'I321'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_COOLING_5FR_ADJUST1_END_TIME = DataTag(
        ['I349', 'I377'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_COOLING_5FR_ADJUST2_ENABLE = DataTag(['D104'], writeable=True)
    SCHEDULE_COOLING_5FR_ADJUST2_VALUE = DataTag(['A129'], writeable=True)
    SCHEDULE_COOLING_5FR_ADJUST2_START_TIME = DataTag(
        ['I294', 'I322'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_COOLING_5FR_ADJUST2_END_TIME = DataTag(
        ['I350', 'I378'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_COOLING_6SA_ENABLE = DataTag(['D106'], writeable=True)
    SCHEDULE_COOLING_6SA_START_TIME = DataTag(
        ['I296', 'I324'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_COOLING_6SA_END_TIME = DataTag(
        ['I352', 'I380'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_COOLING_6SA_ADJUST1_ENABLE = DataTag(['D107'], writeable=True)
    SCHEDULE_COOLING_6SA_ADJUST1_VALUE = DataTag(['A132'], writeable=True)
    SCHEDULE_COOLING_6SA_ADJUST1_START_TIME = DataTag(
        ['I297', 'I325'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_COOLING_6SA_ADJUST1_END_TIME = DataTag(
        ['I353', 'I381'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_COOLING_6SA_ADJUST2_ENABLE = DataTag(['D108'], writeable=True)
    SCHEDULE_COOLING_6SA_ADJUST2_VALUE = DataTag(['A133'], writeable=True)
    SCHEDULE_COOLING_6SA_ADJUST2_START_TIME = DataTag(
        ['I298', 'I326'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_COOLING_6SA_ADJUST2_END_TIME = DataTag(
        ['I354', 'I382'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_COOLING_7SU_ENABLE = DataTag(['D110'], writeable=True)
    SCHEDULE_COOLING_7SU_START_TIME = DataTag(
        ['I300', 'I328'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_COOLING_7SU_END_TIME = DataTag(
        ['I356', 'I384'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_COOLING_7SU_ADJUST1_ENABLE = DataTag(['D111'], writeable=True)
    SCHEDULE_COOLING_7SU_ADJUST1_VALUE = DataTag(['A136'], writeable=True)
    SCHEDULE_COOLING_7SU_ADJUST1_START_TIME = DataTag(
        ['I301', 'I329'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_COOLING_7SU_ADJUST1_END_TIME = DataTag(
        ['I357', 'I385'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_COOLING_7SU_ADJUST2_ENABLE = DataTag(['D112'], writeable=True)
    SCHEDULE_COOLING_7SU_ADJUST2_VALUE = DataTag(['A137'], writeable=True)
    SCHEDULE_COOLING_7SU_ADJUST2_START_TIME = DataTag(
        ['I302', 'I330'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_COOLING_7SU_ADJUST2_END_TIME = DataTag(
        ['I358', 'I386'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_WATER_1MO_ENABLE = DataTag(['D125'], writeable=True)
    SCHEDULE_WATER_1MO_START_TIME = DataTag(
        ['I393', 'I421'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_WATER_1MO_END_TIME = DataTag(
        ['I449', 'I447'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_WATER_1MO_ADJUST1_ENABLE = DataTag(['D126'], writeable=True)
    SCHEDULE_WATER_1MO_ADJUST1_VALUE = DataTag(['A141'], writeable=True)
    SCHEDULE_WATER_1MO_ADJUST1_START_TIME = DataTag(
        ['I394', 'I422'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_WATER_1MO_ADJUST1_END_TIME = DataTag(
        ['I450', 'I448'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_WATER_1MO_ADJUST2_ENABLE = DataTag(['D127'], writeable=True)
    SCHEDULE_WATER_1MO_ADJUST2_VALUE = DataTag(['A142'], writeable=True)
    SCHEDULE_WATER_1MO_ADJUST2_START_TIME = DataTag(
        ['I395', 'I423'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_WATER_1MO_ADJUST2_END_TIME = DataTag(
        ['I451', 'I449'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_WATER_2TU_ENABLE = DataTag(['D129'], writeable=True)
    SCHEDULE_WATER_2TU_START_TIME = DataTag(
        ['I397', 'I425'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_WATER_2TU_END_TIME = DataTag(
        ['I453', 'I451'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_WATER_2TU_ADJUST1_ENABLE = DataTag(['D130'], writeable=True)
    SCHEDULE_WATER_2TU_ADJUST1_VALUE = DataTag(['A145'], writeable=True)
    SCHEDULE_WATER_2TU_ADJUST1_START_TIME = DataTag(
        ['I398', 'I426'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_WATER_2TU_ADJUST1_END_TIME = DataTag(
        ['I454', 'I452'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_WATER_2TU_ADJUST2_ENABLE = DataTag(['D131'], writeable=True)
    SCHEDULE_WATER_2TU_ADJUST2_VALUE = DataTag(['A146'], writeable=True)
    SCHEDULE_WATER_2TU_ADJUST2_START_TIME = DataTag(
        ['I399', 'I427'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_WATER_2TU_ADJUST2_END_TIME = DataTag(
        ['I455', 'I453'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_WATER_3WE_ENABLE = DataTag(['D133'], writeable=True)
    SCHEDULE_WATER_3WE_START_TIME = DataTag(
        ['I401', 'I429'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_WATER_3WE_END_TIME = DataTag(
        ['I457', 'I455'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_WATER_3WE_ADJUST1_ENABLE = DataTag(['D134'], writeable=True)
    SCHEDULE_WATER_3WE_ADJUST1_VALUE = DataTag(['A149'], writeable=True)
    SCHEDULE_WATER_3WE_ADJUST1_START_TIME = DataTag(
        ['I402', 'I430'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_WATER_3WE_ADJUST1_END_TIME = DataTag(
        ['I458', 'I456'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_WATER_3WE_ADJUST2_ENABLE = DataTag(['D135'], writeable=True)
    SCHEDULE_WATER_3WE_ADJUST2_VALUE = DataTag(['A150'], writeable=True)
    SCHEDULE_WATER_3WE_ADJUST2_START_TIME = DataTag(
        ['I403', 'I431'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_WATER_3WE_ADJUST2_END_TIME = DataTag(
        ['I459', 'I457'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_WATER_4TH_ENABLE = DataTag(['D137'], writeable=True)
    SCHEDULE_WATER_4TH_START_TIME = DataTag(
        ['I405', 'I433'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_WATER_4TH_END_TIME = DataTag(
        ['I461', 'I459'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_WATER_4TH_ADJUST1_ENABLE = DataTag(['D138'], writeable=True)
    SCHEDULE_WATER_4TH_ADJUST1_VALUE = DataTag(['A153'], writeable=True)
    SCHEDULE_WATER_4TH_ADJUST1_START_TIME = DataTag(
        ['I406', 'I434'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_WATER_4TH_ADJUST1_END_TIME = DataTag(
        ['I462', 'I460'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_WATER_4TH_ADJUST2_ENABLE = DataTag(['D139'], writeable=True)
    SCHEDULE_WATER_4TH_ADJUST2_VALUE = DataTag(['A154'], writeable=True)
    SCHEDULE_WATER_4TH_ADJUST2_START_TIME = DataTag(
        ['I407', 'I435'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_WATER_4TH_ADJUST2_END_TIME = DataTag(
        ['I463', 'I461'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_WATER_5FR_ENABLE = DataTag(['D141'], writeable=True)
    SCHEDULE_WATER_5FR_START_TIME = DataTag(
        ['I409', 'I437'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_WATER_5FR_END_TIME = DataTag(
        ['I465', 'I463'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_WATER_5FR_ADJUST1_ENABLE = DataTag(['D142'], writeable=True)
    SCHEDULE_WATER_5FR_ADJUST1_VALUE = DataTag(['A157'], writeable=True)
    SCHEDULE_WATER_5FR_ADJUST1_START_TIME = DataTag(
        ['I410', 'I438'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_WATER_5FR_ADJUST1_END_TIME = DataTag(
        ['I466', 'I464'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_WATER_5FR_ADJUST2_ENABLE = DataTag(['D143'], writeable=True)
    SCHEDULE_WATER_5FR_ADJUST2_VALUE = DataTag(['A158'], writeable=True)
    SCHEDULE_WATER_5FR_ADJUST2_START_TIME = DataTag(
        ['I411', 'I439'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_WATER_5FR_ADJUST2_END_TIME = DataTag(
        ['I467', 'I465'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_WATER_6SA_ENABLE = DataTag(['D145'], writeable=True)
    SCHEDULE_WATER_6SA_START_TIME = DataTag(
        ['I413', 'I441'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_WATER_6SA_END_TIME = DataTag(
        ['I469', 'I467'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_WATER_6SA_ADJUST1_ENABLE = DataTag(['D146'], writeable=True)
    SCHEDULE_WATER_6SA_ADJUST1_VALUE = DataTag(['A161'], writeable=True)
    SCHEDULE_WATER_6SA_ADJUST1_START_TIME = DataTag(
        ['I414', 'I442'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_WATER_6SA_ADJUST1_END_TIME = DataTag(
        ['I470', 'I468'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_WATER_6SA_ADJUST2_ENABLE = DataTag(['D147'], writeable=True)
    SCHEDULE_WATER_6SA_ADJUST2_VALUE = DataTag(['A162'], writeable=True)
    SCHEDULE_WATER_6SA_ADJUST2_START_TIME = DataTag(
        ['I415', 'I443'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_WATER_6SA_ADJUST2_END_TIME = DataTag(
        ['I471', 'I469'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_WATER_7SU_ENABLE = DataTag(['D149'], writeable=True)
    SCHEDULE_WATER_7SU_START_TIME = DataTag(
        ['I417', 'I445'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_WATER_7SU_END_TIME = DataTag(
        ['I473', 'I471'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_WATER_7SU_ADJUST1_ENABLE = DataTag(['D150'], writeable=True)
    SCHEDULE_WATER_7SU_ADJUST1_VALUE = DataTag(['A165'], writeable=True)
    SCHEDULE_WATER_7SU_ADJUST1_START_TIME = DataTag(
        ['I418', 'I446'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_WATER_7SU_ADJUST1_END_TIME = DataTag(
        ['I474', 'I472'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_WATER_7SU_ADJUST2_ENABLE = DataTag(['D151'], writeable=True)
    SCHEDULE_WATER_7SU_ADJUST2_VALUE = DataTag(['A166'], writeable=True)
    SCHEDULE_WATER_7SU_ADJUST2_START_TIME = DataTag(
        ['I419', 'I447'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_WATER_7SU_ADJUST2_END_TIME = DataTag(
        ['I475', 'I473'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_POOL_1MO_ENABLE = DataTag(['D168'], writeable=True)
    SCHEDULE_POOL_1MO_START_TIME = DataTag(
        ['I528', 'I556'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_POOL_1MO_END_TIME = DataTag(
        ['I584', 'I612'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_POOL_1MO_ADJUST1_ENABLE = DataTag(['D169'], writeable=True)
    SCHEDULE_POOL_1MO_ADJUST1_VALUE = DataTag(['A176'], writeable=True)
    SCHEDULE_POOL_1MO_ADJUST1_START_TIME = DataTag(
        ['I529', 'I557'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_POOL_1MO_ADJUST1_END_TIME = DataTag(
        ['I585', 'I613'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_POOL_1MO_ADJUST2_ENABLE = DataTag(['D170'], writeable=True)
    SCHEDULE_POOL_1MO_ADJUST2_VALUE = DataTag(['A177'], writeable=True)
    SCHEDULE_POOL_1MO_ADJUST2_START_TIME = DataTag(
        ['I530', 'I558'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_POOL_1MO_ADJUST2_END_TIME = DataTag(
        ['I586', 'I614'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_POOL_2TU_ENABLE = DataTag(['D172'], writeable=True)
    SCHEDULE_POOL_2TU_START_TIME = DataTag(
        ['I532', 'I560'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_POOL_2TU_END_TIME = DataTag(
        ['I588', 'I616'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_POOL_2TU_ADJUST1_ENABLE = DataTag(['D173'], writeable=True)
    SCHEDULE_POOL_2TU_ADJUST1_VALUE = DataTag(['A180'], writeable=True)
    SCHEDULE_POOL_2TU_ADJUST1_START_TIME = DataTag(
        ['I533', 'I561'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_POOL_2TU_ADJUST1_END_TIME = DataTag(
        ['I589', 'I617'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_POOL_2TU_ADJUST2_ENABLE = DataTag(['D174'], writeable=True)
    SCHEDULE_POOL_2TU_ADJUST2_VALUE = DataTag(['A181'], writeable=True)
    SCHEDULE_POOL_2TU_ADJUST2_START_TIME = DataTag(
        ['I534', 'I562'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_POOL_2TU_ADJUST2_END_TIME = DataTag(
        ['I590', 'I618'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_POOL_3WE_ENABLE = DataTag(['D176'], writeable=True)
    SCHEDULE_POOL_3WE_START_TIME = DataTag(
        ['I536', 'I564'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_POOL_3WE_END_TIME = DataTag(
        ['I592', 'I620'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_POOL_3WE_ADJUST1_ENABLE = DataTag(['D177'], writeable=True)
    SCHEDULE_POOL_3WE_ADJUST1_VALUE = DataTag(['A184'], writeable=True)
    SCHEDULE_POOL_3WE_ADJUST1_START_TIME = DataTag(
        ['I537', 'I565'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_POOL_3WE_ADJUST1_END_TIME = DataTag(
        ['I593', 'I621'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_POOL_3WE_ADJUST2_ENABLE = DataTag(['D178'], writeable=True)
    SCHEDULE_POOL_3WE_ADJUST2_VALUE = DataTag(['A185'], writeable=True)
    SCHEDULE_POOL_3WE_ADJUST2_START_TIME = DataTag(
        ['I538', 'I566'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_POOL_3WE_ADJUST2_END_TIME = DataTag(
        ['I594', 'I622'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_POOL_4TH_ENABLE = DataTag(['D180'], writeable=True)
    SCHEDULE_POOL_4TH_START_TIME = DataTag(
        ['I540', 'I568'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_POOL_4TH_END_TIME = DataTag(
        ['I596', 'I624'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_POOL_4TH_ADJUST1_ENABLE = DataTag(['D181'], writeable=True)
    SCHEDULE_POOL_4TH_ADJUST1_VALUE = DataTag(['A188'], writeable=True)
    SCHEDULE_POOL_4TH_ADJUST1_START_TIME = DataTag(
        ['I541', 'I569'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_POOL_4TH_ADJUST1_END_TIME = DataTag(
        ['I597', 'I625'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_POOL_4TH_ADJUST2_ENABLE = DataTag(['D182'], writeable=True)
    SCHEDULE_POOL_4TH_ADJUST2_VALUE = DataTag(['A189'], writeable=True)
    SCHEDULE_POOL_4TH_ADJUST2_START_TIME = DataTag(
        ['I542', 'I570'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_POOL_4TH_ADJUST2_END_TIME = DataTag(
        ['I598', 'I626'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_POOL_5FR_ENABLE = DataTag(['D184'], writeable=True)
    SCHEDULE_POOL_5FR_START_TIME = DataTag(
        ['I544', 'I572'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_POOL_5FR_END_TIME = DataTag(
        ['I600', 'I628'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_POOL_5FR_ADJUST1_ENABLE = DataTag(['D185'], writeable=True)
    SCHEDULE_POOL_5FR_ADJUST1_VALUE = DataTag(['A192'], writeable=True)
    SCHEDULE_POOL_5FR_ADJUST1_START_TIME = DataTag(
        ['I545', 'I573'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_POOL_5FR_ADJUST1_END_TIME = DataTag(
        ['I601', 'I629'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_POOL_5FR_ADJUST2_ENABLE = DataTag(['D186'], writeable=True)
    SCHEDULE_POOL_5FR_ADJUST2_VALUE = DataTag(['A193'], writeable=True)
    SCHEDULE_POOL_5FR_ADJUST2_START_TIME = DataTag(
        ['I546', 'I574'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_POOL_5FR_ADJUST2_END_TIME = DataTag(
        ['I602', 'I630'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_POOL_6SA_ENABLE = DataTag(['D188'], writeable=True)
    SCHEDULE_POOL_6SA_START_TIME = DataTag(
        ['I548', 'I576'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_POOL_6SA_END_TIME = DataTag(
        ['I604', 'I632'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_POOL_6SA_ADJUST1_ENABLE = DataTag(['D189'], writeable=True)
    SCHEDULE_POOL_6SA_ADJUST1_VALUE = DataTag(['A196'], writeable=True)
    SCHEDULE_POOL_6SA_ADJUST1_START_TIME = DataTag(
        ['I549', 'I577'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_POOL_6SA_ADJUST1_END_TIME = DataTag(
        ['I605', 'I633'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_POOL_6SA_ADJUST2_ENABLE = DataTag(['D190'], writeable=True)
    SCHEDULE_POOL_6SA_ADJUST2_VALUE = DataTag(['A197'], writeable=True)
    SCHEDULE_POOL_6SA_ADJUST2_START_TIME = DataTag(
        ['I550', 'I578'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_POOL_6SA_ADJUST2_END_TIME = DataTag(
        ['I606', 'I634'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_POOL_7SU_ENABLE = DataTag(['D192'], writeable=True)
    SCHEDULE_POOL_7SU_START_TIME = DataTag(
        ['I552', 'I580'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_POOL_7SU_END_TIME = DataTag(
        ['I608', 'I636'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_POOL_7SU_ADJUST1_ENABLE = DataTag(['D193'], writeable=True)
    SCHEDULE_POOL_7SU_ADJUST1_VALUE = DataTag(['A200'], writeable=True)
    SCHEDULE_POOL_7SU_ADJUST1_START_TIME = DataTag(
        ['I553', 'I581'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_POOL_7SU_ADJUST1_END_TIME = DataTag(
        ['I609', 'I637'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_POOL_7SU_ADJUST2_ENABLE = DataTag(['D194'], writeable=True)
    SCHEDULE_POOL_7SU_ADJUST2_VALUE = DataTag(['A201'], writeable=True)
    SCHEDULE_POOL_7SU_ADJUST2_START_TIME = DataTag(
        ['I554', 'I582'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_POOL_7SU_ADJUST2_END_TIME = DataTag(
        ['I610', 'I638'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX1_1MO_ENABLE = DataTag(['D259'], writeable=True)
    SCHEDULE_MIX1_1MO_START_TIME = DataTag(
        ['I777', 'I805'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX1_1MO_END_TIME = DataTag(
        ['I833', 'I861'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX1_1MO_ADJUST1_ENABLE = DataTag(['D260'], writeable=True)
    SCHEDULE_MIX1_1MO_ADJUST1_VALUE = DataTag(['A247'], writeable=True)
    SCHEDULE_MIX1_1MO_ADJUST1_START_TIME = DataTag(
        ['I778', 'I806'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX1_1MO_ADJUST1_END_TIME = DataTag(
        ['I834', 'I862'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX1_1MO_ADJUST2_ENABLE = DataTag(['D261'], writeable=True)
    SCHEDULE_MIX1_1MO_ADJUST2_VALUE = DataTag(['A248'], writeable=True)
    SCHEDULE_MIX1_1MO_ADJUST2_START_TIME = DataTag(
        ['I779', 'I807'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX1_1MO_ADJUST2_END_TIME = DataTag(
        ['I835', 'I863'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX1_2TU_ENABLE = DataTag(['D263'], writeable=True)
    SCHEDULE_MIX1_2TU_START_TIME = DataTag(
        ['I781', 'I809'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX1_2TU_END_TIME = DataTag(
        ['I837', 'I865'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX1_2TU_ADJUST1_ENABLE = DataTag(['D264'], writeable=True)
    SCHEDULE_MIX1_2TU_ADJUST1_VALUE = DataTag(['A251'], writeable=True)
    SCHEDULE_MIX1_2TU_ADJUST1_START_TIME = DataTag(
        ['I782', 'I810'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX1_2TU_ADJUST1_END_TIME = DataTag(
        ['I838', 'I866'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX1_2TU_ADJUST2_ENABLE = DataTag(['D265'], writeable=True)
    SCHEDULE_MIX1_2TU_ADJUST2_VALUE = DataTag(['A252'], writeable=True)
    SCHEDULE_MIX1_2TU_ADJUST2_START_TIME = DataTag(
        ['I783', 'I811'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX1_2TU_ADJUST2_END_TIME = DataTag(
        ['I839', 'I867'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX1_3WE_ENABLE = DataTag(['D267'], writeable=True)
    SCHEDULE_MIX1_3WE_START_TIME = DataTag(
        ['I785', 'I813'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX1_3WE_END_TIME = DataTag(
        ['I841', 'I869'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX1_3WE_ADJUST1_ENABLE = DataTag(['D268'], writeable=True)
    SCHEDULE_MIX1_3WE_ADJUST1_VALUE = DataTag(['A255'], writeable=True)
    SCHEDULE_MIX1_3WE_ADJUST1_START_TIME = DataTag(
        ['I786', 'I814'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX1_3WE_ADJUST1_END_TIME = DataTag(
        ['I842', 'I870'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX1_3WE_ADJUST2_ENABLE = DataTag(['D269'], writeable=True)
    SCHEDULE_MIX1_3WE_ADJUST2_VALUE = DataTag(['A256'], writeable=True)
    SCHEDULE_MIX1_3WE_ADJUST2_START_TIME = DataTag(
        ['I787', 'I815'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX1_3WE_ADJUST2_END_TIME = DataTag(
        ['I843', 'I871'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX1_4TH_ENABLE = DataTag(['D271'], writeable=True)
    SCHEDULE_MIX1_4TH_START_TIME = DataTag(
        ['I789', 'I817'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX1_4TH_END_TIME = DataTag(
        ['I845', 'I873'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX1_4TH_ADJUST1_ENABLE = DataTag(['D272'], writeable=True)
    SCHEDULE_MIX1_4TH_ADJUST1_VALUE = DataTag(['A259'], writeable=True)
    SCHEDULE_MIX1_4TH_ADJUST1_START_TIME = DataTag(
        ['I790', 'I818'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX1_4TH_ADJUST1_END_TIME = DataTag(
        ['I846', 'I874'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX1_4TH_ADJUST2_ENABLE = DataTag(['D273'], writeable=True)
    SCHEDULE_MIX1_4TH_ADJUST2_VALUE = DataTag(['A260'], writeable=True)
    SCHEDULE_MIX1_4TH_ADJUST2_START_TIME = DataTag(
        ['I791', 'I819'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX1_4TH_ADJUST2_END_TIME = DataTag(
        ['I847', 'I875'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX1_5FR_ENABLE = DataTag(['D275'], writeable=True)
    SCHEDULE_MIX1_5FR_START_TIME = DataTag(
        ['I793', 'I821'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX1_5FR_END_TIME = DataTag(
        ['I849', 'I877'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX1_5FR_ADJUST1_ENABLE = DataTag(['D276'], writeable=True)
    SCHEDULE_MIX1_5FR_ADJUST1_VALUE = DataTag(['A263'], writeable=True)
    SCHEDULE_MIX1_5FR_ADJUST1_START_TIME = DataTag(
        ['I794', 'I822'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX1_5FR_ADJUST1_END_TIME = DataTag(
        ['I850', 'I878'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX1_5FR_ADJUST2_ENABLE = DataTag(['D277'], writeable=True)
    SCHEDULE_MIX1_5FR_ADJUST2_VALUE = DataTag(['A264'], writeable=True)
    SCHEDULE_MIX1_5FR_ADJUST2_START_TIME = DataTag(
        ['I795', 'I823'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX1_5FR_ADJUST2_END_TIME = DataTag(
        ['I851', 'I879'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX1_6SA_ENABLE = DataTag(['D279'], writeable=True)
    SCHEDULE_MIX1_6SA_START_TIME = DataTag(
        ['I797', 'I825'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX1_6SA_END_TIME = DataTag(
        ['I853', 'I881'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX1_6SA_ADJUST1_ENABLE = DataTag(['D280'], writeable=True)
    SCHEDULE_MIX1_6SA_ADJUST1_VALUE = DataTag(['A267'], writeable=True)
    SCHEDULE_MIX1_6SA_ADJUST1_START_TIME = DataTag(
        ['I798', 'I826'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX1_6SA_ADJUST1_END_TIME = DataTag(
        ['I854', 'I882'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX1_6SA_ADJUST2_ENABLE = DataTag(['D281'], writeable=True)
    SCHEDULE_MIX1_6SA_ADJUST2_VALUE = DataTag(['A268'], writeable=True)
    SCHEDULE_MIX1_6SA_ADJUST2_START_TIME = DataTag(
        ['I799', 'I827'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX1_6SA_ADJUST2_END_TIME = DataTag(
        ['I855', 'I883'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX1_7SU_ENABLE = DataTag(['D283'], writeable=True)
    SCHEDULE_MIX1_7SU_START_TIME = DataTag(
        ['I801', 'I829'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX1_7SU_END_TIME = DataTag(
        ['I857', 'I885'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX1_7SU_ADJUST1_ENABLE = DataTag(['D284'], writeable=True)
    SCHEDULE_MIX1_7SU_ADJUST1_VALUE = DataTag(['A271'], writeable=True)
    SCHEDULE_MIX1_7SU_ADJUST1_START_TIME = DataTag(
        ['I802', 'I830'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX1_7SU_ADJUST1_END_TIME = DataTag(
        ['I858', 'I886'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX1_7SU_ADJUST2_ENABLE = DataTag(['D285'], writeable=True)
    SCHEDULE_MIX1_7SU_ADJUST2_VALUE = DataTag(['A272'], writeable=True)
    SCHEDULE_MIX1_7SU_ADJUST2_START_TIME = DataTag(
        ['I803', 'I831'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX1_7SU_ADJUST2_END_TIME = DataTag(
        ['I859', 'I887'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX2_1MO_ENABLE = DataTag(['D302'], writeable=True)
    SCHEDULE_MIX2_1MO_START_TIME = DataTag(
        ['I897', 'I925'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX2_1MO_END_TIME = DataTag(
        ['I953', 'I981'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX2_1MO_ADJUST1_ENABLE = DataTag(['D303'], writeable=True)
    SCHEDULE_MIX2_1MO_ADJUST1_VALUE = DataTag(['A293'], writeable=True)
    SCHEDULE_MIX2_1MO_ADJUST1_START_TIME = DataTag(
        ['I898', 'I926'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX2_1MO_ADJUST1_END_TIME = DataTag(
        ['I954', 'I982'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX2_1MO_ADJUST2_ENABLE = DataTag(['D304'], writeable=True)
    SCHEDULE_MIX2_1MO_ADJUST2_VALUE = DataTag(['A294'], writeable=True)
    SCHEDULE_MIX2_1MO_ADJUST2_START_TIME = DataTag(
        ['I899', 'I927'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX2_1MO_ADJUST2_END_TIME = DataTag(
        ['I955', 'I983'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX2_2TU_ENABLE = DataTag(['D306'], writeable=True)
    SCHEDULE_MIX2_2TU_START_TIME = DataTag(
        ['I901', 'I929'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX2_2TU_END_TIME = DataTag(
        ['I957', 'I985'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX2_2TU_ADJUST1_ENABLE = DataTag(['D307'], writeable=True)
    SCHEDULE_MIX2_2TU_ADJUST1_VALUE = DataTag(['A297'], writeable=True)
    SCHEDULE_MIX2_2TU_ADJUST1_START_TIME = DataTag(
        ['I902', 'I930'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX2_2TU_ADJUST1_END_TIME = DataTag(
        ['I958', 'I986'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX2_2TU_ADJUST2_ENABLE = DataTag(['D308'], writeable=True)
    SCHEDULE_MIX2_2TU_ADJUST2_VALUE = DataTag(['A298'], writeable=True)
    SCHEDULE_MIX2_2TU_ADJUST2_START_TIME = DataTag(
        ['I903', 'I931'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX2_2TU_ADJUST2_END_TIME = DataTag(
        ['I959', 'I987'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX2_3WE_ENABLE = DataTag(['D310'], writeable=True)
    SCHEDULE_MIX2_3WE_START_TIME = DataTag(
        ['I905', 'I933'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX2_3WE_END_TIME = DataTag(
        ['I961', 'I989'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX2_3WE_ADJUST1_ENABLE = DataTag(['D311'], writeable=True)
    SCHEDULE_MIX2_3WE_ADJUST1_VALUE = DataTag(['A301'], writeable=True)
    SCHEDULE_MIX2_3WE_ADJUST1_START_TIME = DataTag(
        ['I906', 'I934'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX2_3WE_ADJUST1_END_TIME = DataTag(
        ['I962', 'I990'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX2_3WE_ADJUST2_ENABLE = DataTag(['D312'], writeable=True)
    SCHEDULE_MIX2_3WE_ADJUST2_VALUE = DataTag(['A302'], writeable=True)
    SCHEDULE_MIX2_3WE_ADJUST2_START_TIME = DataTag(
        ['I907', 'I935'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX2_3WE_ADJUST2_END_TIME = DataTag(
        ['I963', 'I991'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX2_4TH_ENABLE = DataTag(['D314'], writeable=True)
    SCHEDULE_MIX2_4TH_START_TIME = DataTag(
        ['I909', 'I937'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX2_4TH_END_TIME = DataTag(
        ['I965', 'I993'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX2_4TH_ADJUST1_ENABLE = DataTag(['D315'], writeable=True)
    SCHEDULE_MIX2_4TH_ADJUST1_VALUE = DataTag(['A305'], writeable=True)
    SCHEDULE_MIX2_4TH_ADJUST1_START_TIME = DataTag(
        ['I910', 'I938'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX2_4TH_ADJUST1_END_TIME = DataTag(
        ['I966', 'I994'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX2_4TH_ADJUST2_ENABLE = DataTag(['D316'], writeable=True)
    SCHEDULE_MIX2_4TH_ADJUST2_VALUE = DataTag(['A306'], writeable=True)
    SCHEDULE_MIX2_4TH_ADJUST2_START_TIME = DataTag(
        ['I911', 'I939'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX2_4TH_ADJUST2_END_TIME = DataTag(
        ['I967', 'I995'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX2_5FR_ENABLE = DataTag(['D318'], writeable=True)
    SCHEDULE_MIX2_5FR_START_TIME = DataTag(
        ['I913', 'I941'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX2_5FR_END_TIME = DataTag(
        ['I969', 'I997'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX2_5FR_ADJUST1_ENABLE = DataTag(['D319'], writeable=True)
    SCHEDULE_MIX2_5FR_ADJUST1_VALUE = DataTag(['A309'], writeable=True)
    SCHEDULE_MIX2_5FR_ADJUST1_START_TIME = DataTag(
        ['I914', 'I942'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX2_5FR_ADJUST1_END_TIME = DataTag(
        ['I970', 'I998'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX2_5FR_ADJUST2_ENABLE = DataTag(['D320'], writeable=True)
    SCHEDULE_MIX2_5FR_ADJUST2_VALUE = DataTag(['A310'], writeable=True)
    SCHEDULE_MIX2_5FR_ADJUST2_START_TIME = DataTag(
        ['I915', 'I943'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX2_5FR_ADJUST2_END_TIME = DataTag(
        ['I971', 'I999'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX2_6SA_ENABLE = DataTag(['D322'], writeable=True)
    SCHEDULE_MIX2_6SA_START_TIME = DataTag(
        ['I917', 'I945'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX2_6SA_END_TIME = DataTag(
        ['I973', 'I1001'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX2_6SA_ADJUST1_ENABLE = DataTag(['D323'], writeable=True)
    SCHEDULE_MIX2_6SA_ADJUST1_VALUE = DataTag(['A313'], writeable=True)
    SCHEDULE_MIX2_6SA_ADJUST1_START_TIME = DataTag(
        ['I918', 'I946'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX2_6SA_ADJUST1_END_TIME = DataTag(
        ['I974', 'I1002'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX2_6SA_ADJUST2_ENABLE = DataTag(['D324'], writeable=True)
    SCHEDULE_MIX2_6SA_ADJUST2_VALUE = DataTag(['A314'], writeable=True)
    SCHEDULE_MIX2_6SA_ADJUST2_START_TIME = DataTag(
        ['I919', 'I947'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX2_6SA_ADJUST2_END_TIME = DataTag(
        ['I975', 'I1003'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX2_7SU_ENABLE = DataTag(['D326'], writeable=True)
    SCHEDULE_MIX2_7SU_START_TIME = DataTag(
        ['I921', 'I949'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX2_7SU_END_TIME = DataTag(
        ['I977', 'I1005'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX2_7SU_ADJUST1_ENABLE = DataTag(['D327'], writeable=True)
    SCHEDULE_MIX2_7SU_ADJUST1_VALUE = DataTag(['A317'], writeable=True)
    SCHEDULE_MIX2_7SU_ADJUST1_START_TIME = DataTag(
        ['I922', 'I950'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX2_7SU_ADJUST1_END_TIME = DataTag(
        ['I978', 'I1006'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX2_7SU_ADJUST2_ENABLE = DataTag(['D328'], writeable=True)
    SCHEDULE_MIX2_7SU_ADJUST2_VALUE = DataTag(['A318'], writeable=True)
    SCHEDULE_MIX2_7SU_ADJUST2_START_TIME = DataTag(
        ['I923', 'I951'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX2_7SU_ADJUST2_END_TIME = DataTag(
        ['I979', 'I1007'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX3_1MO_ENABLE = DataTag(['D345'], writeable=True)
    SCHEDULE_MIX3_1MO_START_TIME = DataTag(
        ['I1018', 'I1046'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX3_1MO_END_TIME = DataTag(
        ['I1074', 'I1102'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX3_1MO_ADJUST1_ENABLE = DataTag(['D346'], writeable=True)
    SCHEDULE_MIX3_1MO_ADJUST1_VALUE = DataTag(['A339'], writeable=True)
    SCHEDULE_MIX3_1MO_ADJUST1_START_TIME = DataTag(
        ['I1019', 'I1047'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX3_1MO_ADJUST1_END_TIME = DataTag(
        ['I1075', 'I1103'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX3_1MO_ADJUST2_ENABLE = DataTag(['D347'], writeable=True)
    SCHEDULE_MIX3_1MO_ADJUST2_VALUE = DataTag(['A340'], writeable=True)
    SCHEDULE_MIX3_1MO_ADJUST2_START_TIME = DataTag(
        ['I1020', 'I1048'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX3_1MO_ADJUST2_END_TIME = DataTag(
        ['I1076', 'I1104'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX3_2TU_ENABLE = DataTag(['D349'], writeable=True)
    SCHEDULE_MIX3_2TU_START_TIME = DataTag(
        ['I1022', 'I1050'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX3_2TU_END_TIME = DataTag(
        ['I1078', 'I1106'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX3_2TU_ADJUST1_ENABLE = DataTag(['D350'], writeable=True)
    SCHEDULE_MIX3_2TU_ADJUST1_VALUE = DataTag(['A343'], writeable=True)
    SCHEDULE_MIX3_2TU_ADJUST1_START_TIME = DataTag(
        ['I1023', 'I1051'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX3_2TU_ADJUST1_END_TIME = DataTag(
        ['I1079', 'I1107'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX3_2TU_ADJUST2_ENABLE = DataTag(['D351'], writeable=True)
    SCHEDULE_MIX3_2TU_ADJUST2_VALUE = DataTag(['A344'], writeable=True)
    SCHEDULE_MIX3_2TU_ADJUST2_START_TIME = DataTag(
        ['I1024', 'I1052'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX3_2TU_ADJUST2_END_TIME = DataTag(
        ['I1080', 'I1108'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX3_3WE_ENABLE = DataTag(['D353'], writeable=True)
    SCHEDULE_MIX3_3WE_START_TIME = DataTag(
        ['I1026', 'I1054'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX3_3WE_END_TIME = DataTag(
        ['I1082', 'I1110'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX3_3WE_ADJUST1_ENABLE = DataTag(['D354'], writeable=True)
    SCHEDULE_MIX3_3WE_ADJUST1_VALUE = DataTag(['A347'], writeable=True)
    SCHEDULE_MIX3_3WE_ADJUST1_START_TIME = DataTag(
        ['I1027', 'I1055'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX3_3WE_ADJUST1_END_TIME = DataTag(
        ['I1083', 'I1111'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX3_3WE_ADJUST2_ENABLE = DataTag(['D355'], writeable=True)
    SCHEDULE_MIX3_3WE_ADJUST2_VALUE = DataTag(['A348'], writeable=True)
    SCHEDULE_MIX3_3WE_ADJUST2_START_TIME = DataTag(
        ['I1028', 'I1056'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX3_3WE_ADJUST2_END_TIME = DataTag(
        ['I1084', 'I1112'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX3_4TH_ENABLE = DataTag(['D357'], writeable=True)
    SCHEDULE_MIX3_4TH_START_TIME = DataTag(
        ['I1030', 'I1058'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX3_4TH_END_TIME = DataTag(
        ['I1086', 'I1114'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX3_4TH_ADJUST1_ENABLE = DataTag(['D358'], writeable=True)
    SCHEDULE_MIX3_4TH_ADJUST1_VALUE = DataTag(['A351'], writeable=True)
    SCHEDULE_MIX3_4TH_ADJUST1_START_TIME = DataTag(
        ['I1031', 'I1059'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX3_4TH_ADJUST1_END_TIME = DataTag(
        ['I1087', 'I1115'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX3_4TH_ADJUST2_ENABLE = DataTag(['D359'], writeable=True)
    SCHEDULE_MIX3_4TH_ADJUST2_VALUE = DataTag(['A352'], writeable=True)
    SCHEDULE_MIX3_4TH_ADJUST2_START_TIME = DataTag(
        ['I1032', 'I1060'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX3_4TH_ADJUST2_END_TIME = DataTag(
        ['I1088', 'I1116'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX3_5FR_ENABLE = DataTag(['D361'], writeable=True)
    SCHEDULE_MIX3_5FR_START_TIME = DataTag(
        ['I1034', 'I1062'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX3_5FR_END_TIME = DataTag(
        ['I1090', 'I1118'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX3_5FR_ADJUST1_ENABLE = DataTag(['D362'], writeable=True)
    SCHEDULE_MIX3_5FR_ADJUST1_VALUE = DataTag(['A355'], writeable=True)
    SCHEDULE_MIX3_5FR_ADJUST1_START_TIME = DataTag(
        ['I1035', 'I1063'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX3_5FR_ADJUST1_END_TIME = DataTag(
        ['I1091', 'I1119'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX3_5FR_ADJUST2_ENABLE = DataTag(['D363'], writeable=True)
    SCHEDULE_MIX3_5FR_ADJUST2_VALUE = DataTag(['A356'], writeable=True)
    SCHEDULE_MIX3_5FR_ADJUST2_START_TIME = DataTag(
        ['I1036', 'I1064'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX3_5FR_ADJUST2_END_TIME = DataTag(
        ['I1092', 'I1120'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX3_6SA_ENABLE = DataTag(['D365'], writeable=True)
    SCHEDULE_MIX3_6SA_START_TIME = DataTag(
        ['I1038', 'I1066'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX3_6SA_END_TIME = DataTag(
        ['I1094', 'I1122'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX3_6SA_ADJUST1_ENABLE = DataTag(['D366'], writeable=True)
    SCHEDULE_MIX3_6SA_ADJUST1_VALUE = DataTag(['A359'], writeable=True)
    SCHEDULE_MIX3_6SA_ADJUST1_START_TIME = DataTag(
        ['I1039', 'I1067'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX3_6SA_ADJUST1_END_TIME = DataTag(
        ['I1095', 'I1123'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX3_6SA_ADJUST2_ENABLE = DataTag(['D367'], writeable=True)
    SCHEDULE_MIX3_6SA_ADJUST2_VALUE = DataTag(['A360'], writeable=True)
    SCHEDULE_MIX3_6SA_ADJUST2_START_TIME = DataTag(
        ['I1040', 'I1068'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX3_6SA_ADJUST2_END_TIME = DataTag(
        ['I1096', 'I1124'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX3_7SU_ENABLE = DataTag(['D369'], writeable=True)
    SCHEDULE_MIX3_7SU_START_TIME = DataTag(
        ['I1042', 'I1070'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX3_7SU_END_TIME = DataTag(
        ['I1098', 'I1126'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX3_7SU_ADJUST1_ENABLE = DataTag(['D370'], writeable=True)
    SCHEDULE_MIX3_7SU_ADJUST1_VALUE = DataTag(['A363'], writeable=True)
    SCHEDULE_MIX3_7SU_ADJUST1_START_TIME = DataTag(
        ['I1043', 'I1071'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX3_7SU_ADJUST1_END_TIME = DataTag(
        ['I1099', 'I1127'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX3_7SU_ADJUST2_ENABLE = DataTag(['D371'], writeable=True)
    SCHEDULE_MIX3_7SU_ADJUST2_VALUE = DataTag(['A364'], writeable=True)
    SCHEDULE_MIX3_7SU_ADJUST2_START_TIME = DataTag(
        ['I1044', 'I1072'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_MIX3_7SU_ADJUST2_END_TIME = DataTag(
        ['I1100', 'I1128'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_1MO_ENABLE = DataTag(['D388'], writeable=True)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_1MO_START_TIME = DataTag(
        ['I1139', 'I1167'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_1MO_END_TIME = DataTag(
        ['I1195', 'I1223'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_1MO_ADJUST1_ENABLE = DataTag(['D389'], writeable=True)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_1MO_ADJUST1_VALUE = DataTag(['A385'], writeable=True)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_1MO_ADJUST1_START_TIME = DataTag(
        ['I1140', 'I1168'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_1MO_ADJUST1_END_TIME = DataTag(
        ['I1196', 'I1224'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_1MO_ADJUST2_ENABLE = DataTag(['D390'], writeable=True)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_1MO_ADJUST2_VALUE = DataTag(['A386'], writeable=True)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_1MO_ADJUST2_START_TIME = DataTag(
        ['I1141', 'I1169'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_1MO_ADJUST2_END_TIME = DataTag(
        ['I1197', 'I1225'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_2TU_ENABLE = DataTag(['D392'], writeable=True)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_2TU_START_TIME = DataTag(
        ['I1143', 'I1171'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_2TU_END_TIME = DataTag(
        ['I1199', 'I1227'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_2TU_ADJUST1_ENABLE = DataTag(['D393'], writeable=True)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_2TU_ADJUST1_VALUE = DataTag(['A389'], writeable=True)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_2TU_ADJUST1_START_TIME = DataTag(
        ['I1144', 'I1172'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_2TU_ADJUST1_END_TIME = DataTag(
        ['I1200', 'I1228'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_2TU_ADJUST2_ENABLE = DataTag(['D394'], writeable=True)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_2TU_ADJUST2_VALUE = DataTag(['A390'], writeable=True)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_2TU_ADJUST2_START_TIME = DataTag(
        ['I1145', 'I1173'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_2TU_ADJUST2_END_TIME = DataTag(
        ['I1201', 'I1229'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_3WE_ENABLE = DataTag(['D396'], writeable=True)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_3WE_START_TIME = DataTag(
        ['I1147', 'I1175'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_3WE_END_TIME = DataTag(
        ['I1203', 'I1231'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_3WE_ADJUST1_ENABLE = DataTag(['D397'], writeable=True)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_3WE_ADJUST1_VALUE = DataTag(['A393'], writeable=True)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_3WE_ADJUST1_START_TIME = DataTag(
        ['I1148', 'I1176'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_3WE_ADJUST1_END_TIME = DataTag(
        ['I1204', 'I1232'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_3WE_ADJUST2_ENABLE = DataTag(['D398'], writeable=True)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_3WE_ADJUST2_VALUE = DataTag(['A394'], writeable=True)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_3WE_ADJUST2_START_TIME = DataTag(
        ['I1149', 'I1177'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_3WE_ADJUST2_END_TIME = DataTag(
        ['I1205', 'I1233'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_4TH_ENABLE = DataTag(['D400'], writeable=True)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_4TH_START_TIME = DataTag(
        ['I1151', 'I1179'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_4TH_END_TIME = DataTag(
        ['I1207', 'I1235'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_4TH_ADJUST1_ENABLE = DataTag(['D401'], writeable=True)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_4TH_ADJUST1_VALUE = DataTag(['A397'], writeable=True)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_4TH_ADJUST1_START_TIME = DataTag(
        ['I1152', 'I1180'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_4TH_ADJUST1_END_TIME = DataTag(
        ['I1208', 'I1236'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_4TH_ADJUST2_ENABLE = DataTag(['D402'], writeable=True)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_4TH_ADJUST2_VALUE = DataTag(['A398'], writeable=True)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_4TH_ADJUST2_START_TIME = DataTag(
        ['I1153', 'I1181'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_4TH_ADJUST2_END_TIME = DataTag(
        ['I1209', 'I1237'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_5FR_ENABLE = DataTag(['D404'], writeable=True)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_5FR_START_TIME = DataTag(
        ['I1155', 'I1183'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_5FR_END_TIME = DataTag(
        ['I1211', 'I1239'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_5FR_ADJUST1_ENABLE = DataTag(['D405'], writeable=True)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_5FR_ADJUST1_VALUE = DataTag(['A401'], writeable=True)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_5FR_ADJUST1_START_TIME = DataTag(
        ['I1156', 'I1184'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_5FR_ADJUST1_END_TIME = DataTag(
        ['I1212', 'I1240'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_5FR_ADJUST2_ENABLE = DataTag(['D406'], writeable=True)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_5FR_ADJUST2_VALUE = DataTag(['A402'], writeable=True)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_5FR_ADJUST2_START_TIME = DataTag(
        ['I1157', 'I1185'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_5FR_ADJUST2_END_TIME = DataTag(
        ['I1213', 'I1241'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_6SA_ENABLE = DataTag(['D408'], writeable=True)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_6SA_START_TIME = DataTag(
        ['I1159', 'I1187'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_6SA_END_TIME = DataTag(
        ['I1215', 'I1243'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_6SA_ADJUST1_ENABLE = DataTag(['D409'], writeable=True)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_6SA_ADJUST1_VALUE = DataTag(['A405'], writeable=True)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_6SA_ADJUST1_START_TIME = DataTag(
        ['I1160', 'I1188'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_6SA_ADJUST1_END_TIME = DataTag(
        ['I1216', 'I1244'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_6SA_ADJUST2_ENABLE = DataTag(['D410'], writeable=True)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_6SA_ADJUST2_VALUE = DataTag(['A406'], writeable=True)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_6SA_ADJUST2_START_TIME = DataTag(
        ['I1161', 'I1189'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_6SA_ADJUST2_END_TIME = DataTag(
        ['I1217', 'I1245'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_7SU_ENABLE = DataTag(['D412'], writeable=True)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_7SU_START_TIME = DataTag(
        ['I1163', 'I1191'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_7SU_END_TIME = DataTag(
        ['I1219', 'I1247'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_7SU_ADJUST1_ENABLE = DataTag(['D413'], writeable=True)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_7SU_ADJUST1_VALUE = DataTag(['A409'], writeable=True)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_7SU_ADJUST1_START_TIME = DataTag(
        ['I1164', 'I1192'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_7SU_ADJUST1_END_TIME = DataTag(
        ['I1220', 'I1248'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_7SU_ADJUST2_ENABLE = DataTag(['D414'], writeable=True)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_7SU_ADJUST2_VALUE = DataTag(['A410'], writeable=True)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_7SU_ADJUST2_START_TIME = DataTag(
        ['I1165', 'I1193'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP_7SU_ADJUST2_END_TIME = DataTag(
        ['I1221', 'I1249'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_SOLAR_1MO_ENABLE = DataTag(['D204'], writeable=True)
    SCHEDULE_SOLAR_1MO_START_TIME = DataTag(
        ['I648', 'I676'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_SOLAR_1MO_END_TIME = DataTag(
        ['I704', 'I732'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_SOLAR_2TU_ENABLE = DataTag(['D208'], writeable=True)
    SCHEDULE_SOLAR_2TU_START_TIME = DataTag(
        ['I652', 'I680'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_SOLAR_2TU_END_TIME = DataTag(
        ['I708', 'I736'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_SOLAR_3WE_ENABLE = DataTag(['D212'], writeable=True)
    SCHEDULE_SOLAR_3WE_START_TIME = DataTag(
        ['I656', 'I684'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_SOLAR_3WE_END_TIME = DataTag(
        ['I712', 'I740'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_SOLAR_4TH_ENABLE = DataTag(['D216'], writeable=True)
    SCHEDULE_SOLAR_4TH_START_TIME = DataTag(
        ['I660', 'I688'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_SOLAR_4TH_END_TIME = DataTag(
        ['I716', 'I744'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_SOLAR_5FR_ENABLE = DataTag(['D220'], writeable=True)
    SCHEDULE_SOLAR_5FR_START_TIME = DataTag(
        ['I664', 'I692'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_SOLAR_5FR_END_TIME = DataTag(
        ['I720', 'I748'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_SOLAR_6SA_ENABLE = DataTag(['D224'], writeable=True)
    SCHEDULE_SOLAR_6SA_START_TIME = DataTag(
        ['I668', 'I696'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_SOLAR_6SA_END_TIME = DataTag(
        ['I724', 'I752'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_SOLAR_7SU_ENABLE = DataTag(['D228'], writeable=True)
    SCHEDULE_SOLAR_7SU_START_TIME = DataTag(
        ['I672', 'I700'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_SOLAR_7SU_END_TIME = DataTag(
        ['I728', 'I756'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_PV_1MO_ENABLE = DataTag(['D642'], writeable=True)
    SCHEDULE_PV_1MO_START_TIME = DataTag(
        ['I1483', 'I1511'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_PV_1MO_END_TIME = DataTag(
        ['I1539', 'I1567'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_PV_2TU_ENABLE = DataTag(['D646'], writeable=True)
    SCHEDULE_PV_2TU_START_TIME = DataTag(
        ['I1487', 'I1515'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_PV_2TU_END_TIME = DataTag(
        ['I1543', 'I1571'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_PV_3WE_ENABLE = DataTag(['D650'], writeable=True)
    SCHEDULE_PV_3WE_START_TIME = DataTag(
        ['I1491', 'I1519'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_PV_3WE_END_TIME = DataTag(
        ['I1547', 'I1575'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_PV_4TH_ENABLE = DataTag(['D654'], writeable=True)
    SCHEDULE_PV_4TH_START_TIME = DataTag(
        ['I1495', 'I1523'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_PV_4TH_END_TIME = DataTag(
        ['I1551', 'I1579'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_PV_5FR_ENABLE = DataTag(['D658'], writeable=True)
    SCHEDULE_PV_5FR_START_TIME = DataTag(
        ['I1499', 'I1527'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_PV_5FR_END_TIME = DataTag(
        ['I1555', 'I1583'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_PV_6SA_ENABLE = DataTag(['D662'], writeable=True)
    SCHEDULE_PV_6SA_START_TIME = DataTag(
        ['I1503', 'I1531'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_PV_6SA_END_TIME = DataTag(
        ['I1559', 'I1587'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_PV_7SU_ENABLE = DataTag(['D666'], writeable=True)
    SCHEDULE_PV_7SU_START_TIME = DataTag(
        ['I1507', 'I1535'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
    SCHEDULE_PV_7SU_END_TIME = DataTag(
        ['I1563', 'I1591'], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)

# values = [
#     ["SCHEDULE_HEATING", 42, 63, 151, 179, 207, 235],
#     ["SCHEDULE_COOLING", 86, 112, 276, 304, 332, 360],
#     ["SCHEDULE_WATER", 125, 141, 393, 421, 449, 447]
# ]
#
# for a_value in values:
#     day_addon = 0
#     for a_day in SCHEDULE_DAY_LIST:
#         enable_idx = a_value[1] + day_addon
#         value_idx = a_value[2] + day_addon
#         start_hh_idx = a_value[3] + day_addon
#         start_mm_idx = a_value[4] + day_addon
#         end_hh_idx = a_value[5] + day_addon
#         end_mm_idx = a_value[6] + day_addon
#
#         tags_v = [
#             [enable_idx], [start_hh_idx, start_mm_idx], [end_hh_idx, end_mm_idx],
#             [enable_idx + 1], [value_idx], [start_hh_idx + 1, start_mm_idx + 1], [end_hh_idx + 1, end_mm_idx + 1],
#             [enable_idx + 2], [value_idx + 1], [start_hh_idx + 2, start_mm_idx + 2], [end_hh_idx + 2, end_mm_idx + 2],
#         ]
#
#         for idx in range(len(SCHEDULE_SENSOR_TYPES_LIST)):
#             a_type = SCHEDULE_SENSOR_TYPES_LIST[idx]
#             a_tag_base = tags_v[idx]
#
#             a_tag_list = []
#             for a_int in a_tag_base:
#                 if a_type.endswith("_ENABLE"):
#                     a_tag_list.append(f"D{(a_int)}")
#                 elif a_type.endswith("_VALUE"):
#                     a_tag_list.append(f"A{(a_int)}")
#                 else:
#                     a_tag_list.append(f"I{(a_int)}")
#
#             name = f"{a_value[0]}_{a_day}{a_type}"
#             if len(a_tag_list) == 1:
#                 data_tag = DataTag(tags=a_tag_list, writeable=True)
#             else:
#                 data_tag = DataTag(
#                     tags=a_tag_list, writeable=True, decode_f=DataTag._decode_time_hhmm,
#                     encode_f=DataTag._encode_time_hhmm
#                 )
#             extend_enum(WKHPTag, name, data_tag)
#             # print(f"{name} {data_tag.tags}")
#
#         day_addon = day_addon + 4
