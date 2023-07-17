from datetime import datetime, timedelta
import json
import os
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


def extract_hours_from_ts(ts, h):
    dt = datetime.strptime(ts, TIME_FORMAT)
    return str(dt - timedelta(hours=h))


def get_request_params(last_record, segment_h, range_h, is_average, weather_param):
    last_record_ts = last_record['event'][3]
    count_from_record_ts = extract_hours_from_ts(
        last_record_ts, range_h)
    return {
        'count_from_record_ts': count_from_record_ts,
        'last_record_ts': last_record_ts,
        'segment_h': segment_h,
        'range_h': range_h,
        'is_average': is_average,
        'weather_param': weather_param,
    }


def get_minutes_from_ts(ts):
    dt = datetime.strptime(ts, TIME_FORMAT)
    return dt.minute


def extract_hours_from_ts(ts, h):
    dt = datetime.strptime(ts, TIME_FORMAT)
    return str(dt - timedelta(hours=h))


def add_hours_to_ts(ts, h):
    dt = datetime.strptime(ts, TIME_FORMAT)
    return str(dt + timedelta(hours=h))


def get_list_of_increments(range_h, segment_h, ts):
    list = []
    count = 0
    iterations = range_h/segment_h
    while count < iterations:
        minutes_from_ts = get_minutes_from_ts(ts)
        ts = add_hours_to_ts(ts, segment_h)
        count += 1
        if minutes_from_ts not in list:
            list.append(minutes_from_ts)

    return list


def get_fe_ready_record(record):
    parsed_item = {
        'ts': record['event'][3],
        'data': {}
    }
    for el in record['event_data']:
        value = el[1] if is_integer_num(el[1]) else json.loads(el[2])
        parsed_item['data'][el[3]] = value
    return parsed_item
