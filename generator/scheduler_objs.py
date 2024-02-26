import asyncio
from typing import Final

SCHEDULE_LIST: Final = [
    "SCHEDULE_HEATING",
    "SCHEDULE_COOLING",
    "SCHEDULE_WATER",
    "SCHEDULE_POOL",
    "SCHEDULE_MIX1",
    "SCHEDULE_MIX2",
    "SCHEDULE_MIX3",
    "SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP",
    "SCHEDULE_SOLAR",
    "SCHEDULE_PV"
]
SCHEDULE_DAY_LIST: Final = ["1MO", "2TU", "3WE", "4TH", "5FR", "6SA", "7SU"]
SCHEDULE_SENSOR_TYPES_LIST: Final = ["_ENABLE", "_START_TIME", "_END_TIME",
                                     "_ADJUST1_ENABLE", "_ADJUST1_VALUE", "_ADJUST1_START_TIME", "_ADJUST1_END_TIME",
                                     "_ADJUST2_ENABLE", "_ADJUST2_VALUE", "_ADJUST2_START_TIME", "_ADJUST2_END_TIME"]


def generateTags():
    with open("gen_TAGS.txt", 'w+') as out:
        values = [
            ["SCHEDULE_HEATING", 42, 63, 151, 179, 207, 235],
            ["SCHEDULE_COOLING", 86, 112, 276, 304, 332, 360],
            ["SCHEDULE_WATER", 125, 141, 393, 421, 449, 447],
            ["SCHEDULE_POOL", 168, 176, 528, 556, 584, 612],
            ["SCHEDULE_MIX1", 259, 247, 777, 805, 833, 861],
            ["SCHEDULE_MIX2", 302, 293, 897, 925, 953, 981],
            ["SCHEDULE_MIX3", 345, 339, 1018, 1046, 1074, 1102],
            ["SCHEDULE_BUFFER_TANK_CIRCULATION_PUMP", 388, 385, 1139, 1167, 1195, 1223],
            ["SCHEDULE_SOLAR", 204, -1, 648, 676, 704, 732],
            ["SCHEDULE_PV", 642, -1, 1483, 1511, 1539, 1567]
        ]

        for a_value in values:
            day_addon = 0
            no_adj_values = a_value[2] == -1

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
                    [enable_idx + 2], [value_idx + 1], [start_hh_idx + 2, start_mm_idx + 2],
                    [end_hh_idx + 2, end_mm_idx + 2],
                ]

                for idx in range(len(SCHEDULE_SENSOR_TYPES_LIST)):
                    a_type = SCHEDULE_SENSOR_TYPES_LIST[idx]
                    a_tag_base = tags_v[idx]

                    if no_adj_values and ("_VALUE" in a_type or "_ADJUST" in a_type):
                        pass
                    else:
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
                            out.write(f"    {name} = DataTag({a_tag_list}, writeable=True)\r")
                        else:
                            out.write(f"    {name} = DataTag(\r")
                            out.write(f"        {a_tag_list}, writeable=True, decode_f=DataTag._decode_time_hhmm, encode_f=DataTag._encode_time_hhmm)\r")

                day_addon = day_addon + 4

        out.flush()

def generateEntityDesc():
    files = {"S": "gen_switch.txt", "N": "gen_number.txt", "D": "gen_sensor.txt"}
    outfiles = {}
    with open(files["S"], 'w+') as outfiles["S"], open(files["N"], 'w+') as outfiles["N"], open(files["D"], 'w+') as outfiles["D"]:
        outfiles["S"].write('    ############################################\r')
        outfiles["S"].write('    # GENERATED                                #\r')
        outfiles["S"].write('    ############################################\r')

        outfiles["N"].write('    ############################################\r')
        outfiles["N"].write('    # GENERATED                                #\r')
        outfiles["N"].write('    ############################################\r')

        outfiles["D"].write('    ############################################\r')
        outfiles["D"].write('    # GENERATED                                #\r')
        outfiles["D"].write('    ############################################\r')

        for a_value in SCHEDULE_LIST:
            no_adj_values = a_value == "SCHEDULE_SOLAR" or a_value == "SCHEDULE_PV"
            for a_day in SCHEDULE_DAY_LIST:
                for a_type in SCHEDULE_SENSOR_TYPES_LIST:
                    if no_adj_values and ("_VALUE" in a_type or "_ADJUST" in a_type):
                        pass
                    else:
                        a_key = f"{a_value}_{a_day}{a_type}"
                        if a_type.endswith("_ENABLE"):
                            outfiles["S"].write('    ExtSwitchEntityDescription(\r')
                            outfiles["S"].write(f'        key="{a_key}",\r')
                            outfiles["S"].write(f'        tag=WKHPTag.{a_key},\r')
                            outfiles["S"].write('        icon="mdi:calendar-today",\r')
                            outfiles["S"].write('        entity_registry_enabled_default=False,\r')
                            outfiles["S"].write('        feature=FEATURE_CODE_GEN\r')
                            outfiles["S"].write('    ),\r')
                        elif a_type.endswith("_VALUE"):
                            outfiles["N"].write('    ExtNumberEntityDescription(\r')
                            outfiles["N"].write(f'        key="{a_key}",\r')
                            outfiles["N"].write(f'        tag=WKHPTag.{a_key},\r')
                            outfiles["N"].write('        device_class=NumberDeviceClass.TEMPERATURE,\r')
                            outfiles["N"].write('        icon="mdi:thermometer",\r')
                            outfiles["N"].write('        entity_registry_enabled_default=False,\r')
                            outfiles["N"].write('        native_min_value=-10,\r')
                            outfiles["N"].write('        native_max_value=10,\r')
                            outfiles["N"].write('        native_step=TENTH_STEP,\r')
                            outfiles["N"].write('        mode=NumberMode.BOX,\r')
                            outfiles["N"].write('        native_unit_of_measurement=UnitOfTemperature.KELVIN,\r')
                            outfiles["N"].write('        feature=FEATURE_CODE_GEN\r')
                            outfiles["N"].write('    ),\r')
                        else:
                            # time sensor...
                            outfiles["D"].write('    ExtSensorEntityDescription(\r')
                            outfiles["D"].write(f'        key="{a_key}",\r')
                            outfiles["D"].write(f'        tag=WKHPTag.{a_key},\r')
                            outfiles["D"].write('        device_class=SensorDeviceClass.DATE,\r')
                            outfiles["D"].write('        native_unit_of_measurement=None,\r')
                            outfiles["D"].write('        icon="mdi:clock-digital",\r')
                            outfiles["D"].write('        entity_registry_enabled_default=False,\r')
                            outfiles["D"].write('        feature=FEATURE_CODE_GEN\r')
                            outfiles["D"].write('    ),\r')

        outfiles["S"].flush()
        outfiles["N"].flush()
        outfiles["D"].flush()

    #with open(files["S"], 'r') as f:
    #    data = f.read()
    #    print(data)
    #with open(files["N"], 'r') as f:
    #    data = f.read()
    #    print(data)
    #with open(files["D"], 'r') as f:
    #    data = f.read()
    #    print(data)


generateTags()
generateEntityDesc()
