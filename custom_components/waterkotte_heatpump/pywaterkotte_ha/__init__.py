#import logging
import math
import struct
from datetime import datetime, timedelta, time
from typing import NamedTuple, List, Collection, Callable

from custom_components.waterkotte_heatpump.pywaterkotte_ha.const import HEATING_MODES, SERIES, SYSTEM_IDS

#_LOGGER: logging.Logger = logging.getLogger(__package__)

class InvalidValueException(Exception):
    """A InvalidValueException."""

    # pass


class TagData(NamedTuple):

    def _decode_value_default(self, str_vals: List[str], *other_args):
        first_val = str_vals[0]
        if first_val is None:
            # do not check any further if for what ever reason the first value of the str_vals is None
            return None

        first_tag = self.tags[0]
        assert first_tag[0] in ["A", "I", "D"]

        if first_tag[0] == "A":
            if len(self.tags) == 1:
                return float(first_val) / 10.0
            else:
                ivals = [int(xxl) & 0xFFFF for xxl in str_vals]
                hex_string = f"{ivals[0]:04x}{ivals[1]:04x}"
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
                    #_LOGGER.debug(f"BITS: {first_tag} ({first_val}) -> {ret}")
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
            encoded_values[ecotouch_tag] = str(int(value * 10))

    def _decode_datetime(self, str_vals: List[str], *other_args):  # pylint: disable=unused-argument
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

    def _decode_time_hhmm(self, str_vals: List[str], *other_args):  # pylint: disable=unused-argument
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

    def _decode_state(self, str_vals: List[str], *other_args):  # pylint: disable=unused-argument
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

    def _decode_heat_mode(self, str_vals: List[str], *other_args):  # pylint: disable=unused-argument
        assert len(self.tags) == 1
        intVal = int(str_vals[0])
        if intVal >= 0 and intVal <= len(HEATING_MODES):
            return HEATING_MODES[intVal]
        else:
            return "Error"

    def _encode_heat_mode(self, value, encoded_values):
        assert len(self.tags) == 1
        ecotouch_tag = self.tags[0]
        assert ecotouch_tag[0] in ["I"]
        index = self._get_key_from_value(HEATING_MODES, value)
        if index is not None:
            encoded_values[ecotouch_tag] = str(index)

    @staticmethod
    def _get_key_from_value(a_dict: dict, value_to_find):
        # a very simple "find first key" of dict method...
        keys = [k for k, v in a_dict.items() if v == value_to_find]
        if keys:
            return keys[0]
        return None

    def _decode_ro_status(self, str_vals: List[str], *other_args):  # pylint: disable=unused-argument
        assert len(self.tags) == 1
        if str_vals[0] == "0":
            return "off"
        elif str_vals[0] == "1":
            return "on"
        elif str_vals[0] == "2":
            return "disabled"
        else:
            return "Error"

    def _encode_ro_status(self, value, encoded_values):
        assert len(self.tags) == 1
        ecotouch_tag = self.tags[0]
        assert ecotouch_tag[0] in ["I"]
        if value == "off":
            encoded_values[ecotouch_tag] = "0"
        elif value == "on":
            encoded_values[ecotouch_tag] = "1"
        elif value == "disabled":
            encoded_values[ecotouch_tag] = "2"

    def _decode_ro_series(self, str_vals: List[str], *other_args):  # pylint: disable=unused-argument
        return SERIES[int(str_vals[0])] if str_vals[0] else ""

    def _decode_ro_id(self, str_vals: List[str], *other_args):  # pylint: disable=unused-argument
        assert len(self.tags) == 1
        return SYSTEM_IDS[int(str_vals[0])] if str_vals[0] else ""

    def _decode_ro_bios(self, str_vals: List[str], *other_args):  # pylint: disable=unused-argument
        assert len(self.tags) == 1
        str_val = str_vals[0]
        return f"{str_val[:-2]}.{str_val[-2:]}"

    def _decode_ro_fw(self, str_vals: List[str], *other_args):  # pylint: disable=unused-argument
        assert len(self.tags) == 2
        str_val1 = str_vals[0]
        str_val2 = str_vals[1]
        # str fw2 = f"{str_val1[:-4]:0>2}.{str_val1[-4:-2]}.{str_val1[-2:]}"
        return f"0{str_val1[0]}.{str_val1[1:3]}.{str_val1[3:]}-{str_val2}"

    def _decode_ro_sn(self, str_vals: List[str], *other_args):  # pylint: disable=unused-argument
        assert len(self.tags) == 2
        sn1 = int(str_vals[0])
        sn2 = int(str_vals[1])
        s1 = "WE" if math.floor(sn1 / 1000) > 0 else "00"  # pylint: disable=invalid-name
        s2 = (sn1 - 1000 if math.floor(sn1 / 1000) > 0 else sn1)  # pylint: disable=invalid-name
        s2 = "0" + str(s2) if s2 < 10 else s2  # pylint: disable=invalid-name
        return str(s1) + str(s2) + str(sn2)

    def _decode_year(self, str_vals: List[str], *other_args):  # pylint: disable=unused-argument
        assert len(self.tags) == 1
        return int(str_vals[0]) + 2000

    tags: Collection[str]
    unit: str = None
    writeable: bool = False
    decode_function: Callable = _decode_value_default
    encode_function: Callable = _encode_value_default
    bit: int = None
    bits: [int] = None
    translate: bool = False
