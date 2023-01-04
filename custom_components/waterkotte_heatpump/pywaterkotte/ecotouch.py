""" pyecotouch main module"""
from typing import Any, Callable, Collection, NamedTuple, Sequence, Tuple  # , List

# from unittest import case
import re
import math
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


def _parse_series(self, e_vals, *other_args):  # pylint: disable=unused-argument
    # pylint: disable=invalid-name,line-too-long
    aI105 = ["Custom", "Ai1", "Ai1+", "AiQE", "DS 5023", "DS 5027Ai", "DS 5051", "DS 5050T", "DS 5110T", "DS 5240", "DS 6500", "DS 502xAi", "DS 505x", "DS 505xT", "DS 51xxT", "DS 509x", "DS 51xx", "EcoTouch Ai1 Geo", "EcoTouch DS 5027 Ai", "EnergyDock", "Basic Line Ai1 Geo", "EcoTouch DS 5018 Ai", "EcoTouch DS 5050T", "EcoTouch DS 5112.5 DT", "EcoTouch 5029 Ai", "DS 6500 D (Duo)", "ET 6900 Q", "EcoTouch Geo Inverter", "EcoTouch 5110TWR", "EcoTouch 5240TWR", "EcoTouch 5240T", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "Ai QL / WP QL", "WPQL-K", "EcoTouch Ai1 Air", "EcoTouch Ai1 Air", "EcoTouch MB 7010", "EcoTouch DA 5018 Ai", "EcoTouch Air LCI", "EcoTouch Ai1 Air K1.1", "EcoTouch DA 5018 Ai K1.1", "EcoTouch Ai1 Air K2", "EcoTouch DA 5018 Ai K2", "EcoTouch Ai1 Air 2018", "Basic Line Ai1 Air", "Basic Line Split", "Basic Line Split W", "EcoTouch Ai1 Air LC S", "EcoTouch Air Kaskade", "EcoTouch Ai1 Air K1.2", "EcoTouch DA 5018 Ai K1.2", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""]
    return aI105[int(e_vals["I105"])] if e_vals["I105"] else ""


def _parse_bios(self, e_vals, *other_args):  # pylint: disable=unused-argument
    return f"{str(e_vals['I3'])[0]}.{str(e_vals['I3'])[1:3]}"


def _parse_fw(self, e_vals, *other_args):  # pylint: disable=unused-argument
    return f"0{str(e_vals['I1'])[0]}.{str(e_vals['I1'])[1:3]}.{str(e_vals['I1'])[3:]}-{str(e_vals['I2'])}"


def _parse_id(self, e_vals, *other_args):  # pylint: disable=unused-argument
    # pylint: disable=invalid-name,line-too-long
    aI110 = ["Ai1 5005.4", "Ai1 5006.4", "Ai1 5007.4", "Ai1 5008.4", "Ai1+ 5006.3", "Ai1+ 5007.3", "Ai1+ 5009.3", "Ai1+ 5011.3", "Ai1+ 5006.3 (1x230V)",
             "Ai1+ 5007.3 (1x230V)", "Ai1+ 5009.3 (1x230V)", "Ai1+ 5011.3 (1x230V)", "DS 5006.3", "DS 5008.3", "DS 5009.3", "DS 5011.3", "DS 5014.3", "DS 5017.3",
             "DS 5020.3", "DS 5023.3", "DS 5006.3 (1x230V)", "DS 5008.3 (1x230V)", "DS 5009.3 (1x230V)", "DS 5011.3 (1x230V)", "DS 5014.3 (1x230V)",
             "DS 5017.3 (1x230V)", "DS 5006.4", "DS 5008.4", "DS 5009.4", "DS 5011.4", "DS 5014.4", "DS 5017.4", "DS 5020.4", "DS 5023.4", "DS 5007.3 Ai",
             "DS 5009.3 Ai", "DS 5010.3 Ai", "DS 5012.3 Ai", "DS 5015.3 Ai", "DS 5019.3 Ai", "DS 5022.3 Ai", "DS 5025.3 Ai", "DS 5007.3 Ai (1x230V)",
             "DS 5009.3 Ai (1x230V)", "DS 5010.3 Ai (1x230V)", "DS 5012.3 Ai (1x230V)", "DS 5015.3 Ai (1x230V)", "DS 5019.3 Ai (1x230V)", "DS 5007.4 Ai",
             "DS 5009.4 Ai", "DS 5010.4 Ai", "DS 5012.4 Ai", "DS 5015.4 Ai", "DS 5019.4 Ai", "DS 5022.4 Ai", "DS 5025.4 Ai", "DS 5007.4 Ai (1x230V)",
             "DS 5009.4 Ai (1x230V)", "DS 5010.4 Ai (1x230V)", "DS 5012.4 Ai (1x230V)", "DS 5015.4 Ai (1x230V)", "DS 5030.3", "DS 5034.3", "DS 5043.3",
             "DS 5051.3", "DS 5030.4", "DS 5034.4", "DS 5043.4", "DS 5051.4", "DS 5030.3 T", "DS 5037.3 T", "DS 5044.3 T", "DS 5050.3 T", "DS 5030.4 T",
             "DS 5037.4 T", "DS 5044.4 T", "DS 5050.4 T", "DS 5062.3 T", "DS 5072.3 T", "DS 5089.3 T", "DS 5109.3 T", "DS 5062.4 T", "DS 5072.4 T", "DS 5089.4 T",
             "DS 5109.4 T", "DS 5118.3", "DS 5136.3", "DS 5161.3", "DS 5162.3", "DS 5193.3", "DS 5194.3", "DS 5231.3", "DS 5118.4", "DS 5136.4", "DS 5161.4",
             "DS 5162.4", "DS 5194.4", "DS 6237.3", "DS 6271.3", "DS 6299.3", "DS 6388.3", "DS 6438.3", "DS 6485.3", "DS 6237.4", "DS 6271.4", "DS 6299.4",
             "DS 6388.4", "DS 6438.4", "DS 6485.4", "Ai1QE 5006.5", "Ai1QE 5007.5", "Ai1QE 5009.5", "Ai1QE 5010.5", "Ai1QE 5006.5 (1x230V)", "Ai1QE 5007.5 (1x230V)",
             "Ai1QE 5009.5 (1x230V)", "Ai1QE 5010.5 (1x230V)", "DS 5008.5AI", "DS 5009.5AI", "DS 5012.5AI", "DS 5014.5AI", "DS 5017.5AI", "DS 5020.5AI",
             "DS 5023.5AI", "DS 5026.5AI", "DS 5008.5AI (1x230V)", "DS 5009.5AI (1x230V)", "DS 5012.5AI (1x230V)", "DS 5014.5AI (1x230V)", "DS 5017.5AI (1x230V)",
             "DS 5029.5", "DS 5033.5", "DS 5040.5", "DS 5045.5", "DS 5050.5", "DS 5059.5", "DS 5028.5 T", "DS 5034.5 T", "DS 5040.5 T", "DS 5046.5 T", "DS 5052.5 T",
             "DS 5058.5 T", "DS 5063.5 T", "DS 5075.5 T", "DS 5085.5 T", "DS 5095.5 T", "DS 5112.5 T", "DS 5076.5", "DS 5095.5", "DS 5123.5", "DS 5158.5", "Ai QL",
             "Ai QL Kaskade", "DS 5013.5AI", "DS 5013.5AI (1x230V)", "DS 5036.4T", "DS 5049.4T", "DS 5063.4T", "DS 5077.4T", "DS 5007.5AI HT", "DS 5008.5AI HT",
             "DS 5010.5AI HT", "DS 5014.5AI HT", "DS 5018.5AI HT", "DS 5023.5AI HT", "DS 5007.5AI HT (1x230V)", "DS 5008.5AI HT (1x230V)", "DS 5010.5AI HT (1x230V)",
             "DS 5014.5AI HT (1x230V)", "DS 5018.5AI HT (1x230V)", "DS 5005.4Ai HT", "DS 5007.4Ai HT", "DS 5009.4Ai HT", "DS 5010.4Ai HT", "DS 5012.4Ai HT",
             "DS 5015.4Ai HT", "DS 5005.4Ai HT (1x230V)", "DS 5007.4Ai HT (1x230V)", "DS 5009.4Ai HT (1x230V)", "DS 5010.4Ai HT (1x230V)", "5006.5", "5008.5",
             "5010.5", "5013.5", "5006.5(1x230V)", "5008.5(1x230V)", "5010.5(1x230V)", "5013.5(1x230V)", "EcoTouch Ai1 QL ", "5018.5", "5010.5", "5010.5",
             "DS 5008.5AI", "DS 5010.5AI", "DS 5012.5AI", "DS 5014.5AI", "DS 5017.5AI", "DS 5020.5AI", "DS 5023.5AI", "DS 5027.5AI", "DS 5008.5AI (1x230V)",
             "DS 5010.5AI (1x230V)", "DS 5012.5AI (1x230V)", "DS 5014.5AI (1x230V)", "DS 5017.5AI (1x230V)", "Power+", "DS 5145.5 Tandem", "DS 5150.5",
             "DS 5182.5 Tandem", "DS 5226.5", "DS 5235.5 Tandem", "DS 6272.5 Trio", "DS 6300.5 Tandem", "DS 6352.5 Trio", "DS 6450.5 Trio", "5005.5", "5006.5",
             "5007.5", "5008.5", "5010.5", "5005.5 (1x230V)", "5006.5 (1x230V)", "5008.5 (1x230V)", "5010.5 (1x230V)", "DS 5006.5Ai Split", "DS 5007.5Ai Split",
             "DS 5009.5Ai Split", "DS 5012.5Ai Split", "DS 5015.5Ai Split", "DS 5020.5Ai Split", "DS 5025.5Ai Split", "DS 5006.3Ai Split", "DS 5007.3Ai Split",
             "DS 5008.3Ai Split", "DS 5010.3Ai Split", "DS 5012.3Ai Split", "DS 5015.3Ai Split", "DS 5018.3Ai Split", "DS 5020.3Ai Split", "5008.5", "5011.5",
             "5014.5", "5018.5", "5008.5 (230V)", "5011.5 (230V)", "5014.5 (230V)", "5018.5 (230V)", "5018.5", "5010.5", "5034.5T", "5045.5T", "5056.5T", "5009.3",
             "5068.5 DT", "5090.5 DT", "5112.5 DT", "5007.3", "5011.3", "EcoTouch 5007.5Ai", "EcoTouch 5008.5Ai", "EcoTouch 5010.5Ai", "EcoTouch 5014.5Ai",
             "EcoTouch 5018.5Ai", "EcoTouch 5023.5Ai", "EcoTouch 5029.5Ai", "EcoTouch 5007.5Ai", "EcoTouch 5008.5Ai", "EcoTouch 5010.5Ai", "EcoTouch 5014.5Ai",
             "EcoTouch 5018.5Ai", "DS 5028.4T HT", "EcoTouch compact 5004.5", "5010.5", "5010.5", "DS 6450.5 D", "5028.5T", "ET 6600.5 Q", "ET 6750.5 Q",
             "ET 6900.5 Q", "5015.5 Ai", "5010.5 Ai", "5010.5", "5018.5", "5010.5(1x230V)", "5018.5(1x230V)", "5010.5", "5018.5", "5010.5(1x230V)", "5018.5(1x230V)",
             "50xx.5", "5003.5 Ai", "5004.5(1x230V)", "", "5008.5(1x230V)", "5011.5(1x230V)", "5012.5(1x230V)", "", "5011.5", "5012.5", "5015.5", "5003.5 Ai NX",
             "5004.5(1x230V)", "", "5008.5(1x230V)", "5011.5(1x230V)", "5012.5(1x230V)", "", "5011.5", "5012.5", "5015.5", "5004.5(1x230V)", "", "5008.5(1x230V)",
             "5011.5(1x230V)", "5012.5(1x230V)", "", "5011.5", "5012.5", "5015.5", "5004.5(1x230V)", "", "5008.5(1x230V)", "5011.5(1x230V)", "5012.5(1x230V)", "",
             "5011.5", "5012.5", "5015.5", "EcoTouch Air Kaskade", "5003.6 Ai NX", "5003.5 Ai SNB", "5003.6 Ai SVB", "5010.5-18 (230V)", "5010.5-18 (230V)",
             "5018.5", "5018.5(1x230V)", "5018.5", "5018.5(1x230V)", "EcoTouch 5007.5Ai Split", "EcoTouch 5008.5Ai Split", "EcoTouch 5010.5Ai Split",
             "EcoTouch 5014.5Ai Split", "EcoTouch 5018.5Ai Split", "EcoTouch 5023.5Ai Split", "EcoTouch 5029.5Ai Split", "ET 5063.4 Tandem WR",
             "ET 5072.4 Tandem WR", "ET 5090.4 Tandem WR", "ET 5108.4 Tandem WR", "ET 5144.4 Tandem WR", "ET 5179.4 Tandem WR", "ET 5222.4 Tandem WR",
             "ET 5144.4 Tandem", "ET 5179.4 Tandem", "ET 5222.4 Tandem", None]
    return aI110[int(e_vals["I110"])] if e_vals["I110"] else ""


def _parse_sn(self, e_vals, *other_args):  # pylint: disable=unused-argument
    sn1 = int(e_vals['I114'])
    sn2 = int(e_vals['I115'])
    s1 = 'WE' if math.floor(sn1 / 1000) > 0 else '00'  # pylint: disable=invalid-name
    s2 = sn1 - 1000 if math.floor(sn1 / 1000) > 0 else sn1  # pylint: disable=invalid-name
    s2 = '0' + s2 if s2 < 10 else s2  # pylint: disable=invalid-name
    return str(s1) + str(s2) + str(sn2)


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
    VERSION_CONTROLLER = TagData(["I1", "I2"],
                                 writeable=False,
                                 read_function=_parse_fw,)
    # VERSION_CONTROLLER_BUILD = TagData(["I2"])
    VERSION_BIOS = TagData(["I3"], writeable=False, read_function=_parse_bios)
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
    INFO_SERIES = TagData(["I105"], read_function=_parse_series)
    INFO_ID = TagData(["I110"], read_function=_parse_id)
    INFO_SERIAL = TagData(
        ["I114", "I115"],
        writeable=False,
        read_function=_parse_sn,
    )
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
