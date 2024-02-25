import logging
import math
import struct
from datetime import timedelta, time

#from enum import Enum
from aenum import Enum, extend_enum

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
    SIX_STEPS_MODES,
    SCHEDULE_DAY_LIST,
    SCHEDULE_SENSOR_TYPES_LIST
)

from custom_components.waterkotte_heatpump.pywaterkotte_ha.error import (
    InvalidValueException,
)

_LOGGER: logging.Logger = logging.getLogger(__package__)


class DataTag(NamedTuple):

    def _decode_value_default(self, str_vals: List[str]):
        return self.__decode_value_default(str_vals, factor=10.0)

    def _decode_value_analog(self, str_vals: List[str]):
        return self.__decode_value_default(str_vals, factor=-1.0)

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
        if int_vals[0] > 23:
            int_vals[0] = 0
        if int_vals[1] > 59:
            int_vals[1] = 0
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


class WKHPTag(DataTag, Enum):
    def __hash__(self) -> int:
        return hash(self.name)

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
    # TODO - CHECK... [currently no Sensors based on these tags]
    TEMPERATURE_ROOM_TARGET = DataTag(["A100"], "°C", writeable=True)
    ROOM_INFLUENCE = DataTag(["A101"], "%", writeable=True)

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
    PERCENT_COMPRESSOR = DataTag(["A58"], "%")

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
    STATE_EVD = DataTag(["I51"], bit=2)
    STATE_COMPRESSOR = DataTag(["I51"], bit=3)
    STATE_COMPRESSOR2 = DataTag(["I51"], bit=4)
    STATE_EXTERNAL_HEATER = DataTag(["I51"], bit=5)
    STATE_ALARM = DataTag(["I51"], bit=6)
    STATE_COOLING = DataTag(["I51"], bit=7)
    STATE_WATER = DataTag(["I51"], bit=8)
    STATE_POOL = DataTag(["I51"], bit=9)
    STATE_SOLAR = DataTag(["I51"], bit=10)
    STATE_COOLING4WAY = DataTag(["I51"], bit=11)

    # we do not have any valid information about the meaning after the bit=8...
    # https://github.com/flautze/home_assistant_waterkotte/issues/1#issuecomment-1916288553
    # ALARM_BITS = DataTag(["I52"], bits=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], translate=True)
    ALARM_BITS = DataTag(["I52"], bits=[0, 1, 2, 3, 4, 5, 6, 7, 8], translate=True)
    INTERRUPTION_BITS = DataTag(["I53"], bits=[0, 1, 2, 3, 4, 5, 6], translate=True)

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
    # SERVICE_HEATING_D24 = DataTag(["D24"])
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
    SOURCE_PUMP_CAPTURE_TEMPERATURE_A479 = DataTag(["A479"], writeable=True)

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
    # D1605: uom: '', 'Luefter 1 - Manuell Drehzahl'
    # A4551: uom: 'U/min', 'Luefter 1 Umdrehungen pro Minute'
    BASICVENT_INCOMING_FAN_RPM_A4551 = DataTag(["A4551"], decode_f=DataTag._decode_value_analog)
    # A4986: uom: '%', 'Analogausgang Y1' - Rotation Incoming air drive percent
    BASICVENT_INCOMING_FAN_A4986 = DataTag(["A4986"], decode_f=DataTag._decode_value_analog)
    # A5000: uom: '', 'T1' - Außenluft/Frischluft - Outdoor air
    BASICVENT_TEMPERATURE_INCOMING_AIR_BEFORE_ODA_A5000 = DataTag(["A5000"], decode_f=DataTag._decode_value_analog)
    # A4996: uom: '', 'T3' - Zuluft - Supply air
    BASICVENT_TEMPERATURE_INCOMING_AIR_AFTER_SUP_A4996 = DataTag(["A4996"], decode_f=DataTag._decode_value_analog)

    # A4545: uom: '', 'Luefter 2 Rueckmeldung'
    # D1603: uom: '', 'Luefter 2 - Manuell Drehzahl'
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

     #####################################
     # TIME SCHEDULING (Thanks @flautze) #
     #####################################
     # _1MO, _2TU, _3WE, _4TH, _5FR, _6SA, _7SU
#     SCHEDULE_HEATING_1MO = DataTag(["D42"], writeable=True)
#     SCHEDULE_HEATING_1MO_START_TIME = DataTag(
#         ["I151", "I179"], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
#     SCHEDULE_HEATING_1MO_END_TIME = DataTag(
#         ["I207", "I235"], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
#     SCHEDULE_HEATING_1MO_ADJUST1 = DataTag(["D46"], writeable=True)
#     SCHEDULE_HEATING_1MO_ADJUST1_VALUE = DataTag(["A63"], writeable=True)
#     SCHEDULE_HEATING_1MO_ADJUST1_START_TIME = DataTag(
#         ["I152", "I180"], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
#     SCHEDULE_HEATING_1MO_ADJUST1_END_TIME = DataTag(
#         ["I208", "I236"], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
#     SCHEDULE_HEATING_1MO_ADJUST2 = DataTag(["D47"], writeable=True)
#     SCHEDULE_HEATING_1MO_ADJUST2_VALUE = DataTag(["A64"], writeable=True)
#     SCHEDULE_HEATING_1MO_ADJUST2_START_TIME = DataTag(
#         ["I153", "I181"], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)
#     SCHEDULE_HEATING_1MO_ADJUST2_END_TIME = DataTag(
#         ["I209", "I237"], writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)

values = [
    ["SCHEDULE_HEATING", 42, 63, 151, 179, 207, 235],
    ["SCHEDULE_COOLING", 86, 112, 276, 304, 332, 360],
    ["SCHEDULE_WATER", 125, 141, 393, 421, 449, 447]
]

for a_value in values:
    day_addon = 0
    for a_day in SCHEDULE_DAY_LIST:
        enable_idx = a_value[1] + day_addon
        value_idx = a_value[2] + day_addon
        start_hh_idx = a_value[3] + day_addon
        start_mm_idx = a_value[4] + day_addon
        end_hh_idx = a_value[5] + day_addon
        end_mm_idx = a_value[6] + day_addon

        tags_v = [
            [enable_idx], [start_hh_idx, start_mm_idx], [end_hh_idx, end_mm_idx],
            [enable_idx + 1], [value_idx], [start_hh_idx + 1, start_mm_idx + 1], [end_hh_idx + 1, end_mm_idx + 1],
            [enable_idx + 2], [value_idx + 1], [start_hh_idx + 2, start_mm_idx + 2], [end_hh_idx + 2, end_mm_idx + 2],
        ]

        for idx in range(len(SCHEDULE_SENSOR_TYPES_LIST)):
            a_type = SCHEDULE_SENSOR_TYPES_LIST[idx]
            a_tag_base = tags_v[idx]

            a_tag_list = []
            for a_int in a_tag_base:
                if a_type.endswith("_ENABLE"):
                    a_tag_list.append(f"D{(a_int)}")
                elif a_type.endswith("_VALUE"):
                    a_tag_list.append(f"A{(a_int)}")
                else:
                    a_tag_list.append(f"I{(a_int)}")

            name = f"{a_value[0]}_{a_day}{a_type}"
            if len(a_tag_list) == 1:
                data_tag = DataTag(tags=a_tag_list, writeable=True)
            else:
                data_tag = DataTag(
                    tags=a_tag_list, writeable=True, decode_f=DataTag._decode_time_hhmm,
                    encode_f=DataTag._encode_time_hhmm
                )
            extend_enum(WKHPTag, name, data_tag)
            # print(f"{name} {data_tag.tags}")

        day_addon = day_addon + 4
