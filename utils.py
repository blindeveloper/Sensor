import json
import os
from datetime import datetime
from glob import glob
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def convert_tuples_to_strings(tuple_list):
    string_list = [str(item[0]) for item in tuple_list]
    return string_list


def is_integer_num(n):
    if isinstance(n, int) or isinstance(n, float):
        return True
    return False


def is_falsy(value):
    return value == False or value == None


def convert_ts_to_sqlite_format(ts):
    dt = datetime.fromisoformat(ts)
    return f'{dt.strftime(TIME_FORMAT)}'


def get_list_of_json_data(month: str, day: str):
    if os.path.exists(f'./data/{month}/{day}/'):
        month_of_data_list = []
        for f_name in glob(f'./data/{month}/{day}/*.json'):
            f = open(f_name)
            raw_climate_record = json.load(f)
            month_of_data_list.append(raw_climate_record)
            f.close()
        return month_of_data_list
    else:
        return None
