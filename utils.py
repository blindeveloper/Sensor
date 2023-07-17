from datetime import datetime
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
