
from utils import convert_tuples_to_strings, is_integer_num, convert_ts_to_sqlite_format
import json


def process_new_event(raw_climate_record, cur, con):
    serialized_range = json.dumps(raw_climate_record['range'])
    converted_ts = convert_ts_to_sqlite_format(raw_climate_record['ts'])

    # add new event to Event table
    cur.execute(f"""
        INSERT INTO Event (name,range, ts, pt)
        VALUES('{raw_climate_record['name']}','{serialized_range}', '{converted_ts}', '{raw_climate_record['pt']}');
    """)
    event_id = cur.lastrowid
    con.commit()
    # load supporting parameters
    parameter_names_res = cur.execute('SELECT name FROM Parameter')
    supporting_parameters = convert_tuples_to_strings(
        parameter_names_res.fetchall())
    # add new parameters if needed to Parameter table
    for row in raw_climate_record['rows']:
        if row[0] == 'Variable':
            continue
        if row[0] not in supporting_parameters:
            type_of_parameter = 'numeric' if row[1] == int else 'char'
            cur.execute(f"""
                INSERT INTO Parameter (name,value_type)
                VALUES('{row[0]}','{type_of_parameter}');
            """)
            con.commit()
        # get parameter id
        parameter_id_res = cur.execute(
            f"SELECT id FROM Parameter WHERE name = '{row[0]}'")
        parameter_id = parameter_id_res.fetchone()
        numeric_value = row[1] if is_integer_num(row[1]) else None
        char_value = json.dumps(row[1]) if not is_integer_num(row[1]) else None

        # add all parameters values to EventData table
        cur.execute(f"""
            INSERT INTO EventData (value_numeric, value_char, parameter_id, event_id)
            VALUES('{numeric_value}','{char_value}', '{parameter_id[0]}', '{event_id}');
        """)

        con.commit()
