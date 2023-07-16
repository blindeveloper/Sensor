def convert_tuples_to_strings(tuple_list):
    string_list = [str(item[0]) for item in tuple_list]
    return string_list


def is_integer_num(n):
    if isinstance(n, int) or isinstance(n, float):
        return True
    return False
