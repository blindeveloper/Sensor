from app.utils import get_list_of_increments, add_hours_to_ts, get_fe_ready_record, convert_ts_to_sqlite_format, is_integer_num
from fastapi import HTTPException
import json


def get_increments(list):
    res = ''
    for idx, el in enumerate(list):
        if idx == 0:
            res += f"strftime('%M', ts) = '{el}'"
        else:
            res += f" OR strftime('%M', ts) = '{el}'"
    return res


def get_sql_events_in_range_segment(req):
    if req['segment_h']:
        list_of_increments = (get_list_of_increments(
            req['range_h'], req['segment_h'], req['count_from_record_ts']))

        return f"""
            SELECT * FROM Event 
            WHERE ts >= '{req['count_from_record_ts']}'
            AND ts <= datetime('{req['last_record_ts']}') 
            AND ({get_increments(list_of_increments)})
            ORDER BY ts DESC;
            """
    else:
        return f"""
            SELECT * FROM Event 
            WHERE ts >= '{req['count_from_record_ts']}'
            AND ts <= datetime('{req['last_record_ts']}')
            ORDER BY ts DESC;
            """


def get_event_data_in_range(cur, request_params):
    list_of_events_with_data = []
    search_string = get_sql_events_in_range_segment(request_params)
    event_list_res = cur.execute(search_string)
    try:
        event_list = event_list_res.fetchall()
        for event in event_list:
            single_event = get_data_for_single_event(cur, event)
            fe_ready_event = get_fe_ready_record(single_event)
            list_of_events_with_data.append(fe_ready_event)
        return list_of_events_with_data
    except:
        raise HTTPException(status_code=404, detail='Events not found')


def get_latest_weather(cur):
    latest_event_res = cur.execute(
        "SELECT * FROM Event ORDER BY ts DESC LIMIT 1")
    try:
        latest_event = latest_event_res.fetchone()
        return get_data_for_single_event(cur, latest_event)
    except:
        raise HTTPException(status_code=404, detail='Event not found')


def get_data_for_single_event(cur, event):
    event_data_res = cur.execute(
        f"""SELECT * FROM EventData 
            INNER JOIN Parameter ON Parameter.id = EventData.parameter_id
            WHERE event_id = '{event[0]}'
        """
    )

    try:
        event_data = event_data_res.fetchall()
        return {
            'event': event,
            'event_data': event_data
        }
    except:
        raise HTTPException(status_code=404, detail='Event data not found')


def get_names_of_parameters(cur):
    try:
        parameter_names_res = cur.execute('SELECT name FROM Parameter')
        return parameter_names_res.fetchall()
    except:
        raise HTTPException(
            status_code=404, detail='Parameter names not found')


def get_average_with_param(cur, req):
    try:
        wit_avg_res = cur.execute(
            f"""
                SELECT avg(value_numeric) FROM EventData
                INNER JOIN Parameter ON Parameter.id = EventData.parameter_id
                INNER JOIN Event ON Event.id = EventData.event_id
                WHERE Parameter.name = '{req['weather_param']}'
                AND Event.ts >= '{req['count_from_record_ts']}'
                AND Event.ts <= datetime('{req['last_record_ts']}')
                ORDER BY Event.ts DESC
            """)
        res = wit_avg_res.fetchone()
        return {
            f"{req['weather_param']}": res[0],
        }
    except:
        raise HTTPException(status_code=404, detail='Item not found')


def get_total_average(cur, req):
    try:
        total_avg_res = cur.execute(
            f"""
                SELECT Parameter.name, avg(EventData.value_numeric) FROM EventData
                INNER JOIN Parameter ON Parameter.id = EventData.parameter_id
                INNER JOIN Event ON Event.id = EventData.event_id
                WHERE Event.ts >= '{req['count_from_record_ts']}'
                AND Event.ts <= datetime('{req['last_record_ts']}')
                GROUP BY Parameter.name
            """)
        res = total_avg_res.fetchall()
        fe_ready_res = {}
        for el in res:
            fe_ready_res[f'{el[0]}'] = el[1]
        return fe_ready_res
    except:
        raise HTTPException(status_code=404, detail='Item not found')


def get_average_with_segment(cur, req):
    try:
        list_of_average_by_segment = []
        end_ts = req['last_record_ts']
        next_ts = req['count_from_record_ts']

        while next_ts < end_ts:
            next_ts = add_hours_to_ts(next_ts, req['segment_h'])
            req['last_record_ts'] = next_ts
            res = get_total_average(cur, req)

            list_of_average_by_segment.append(res)

        return list_of_average_by_segment

    except:
        raise HTTPException(status_code=404, detail='Item not found')


def add_new_event(cur, con, raw_climate_record):
    try:
        serialized_range = json.dumps(raw_climate_record['range'])
        converted_ts = convert_ts_to_sqlite_format(raw_climate_record['ts'])

        cur.execute(f"""
            INSERT INTO Event (name,range, ts, pt)
            VALUES('{raw_climate_record['name']}','{serialized_range}', '{converted_ts}', '{raw_climate_record['pt']}');
        """)
        con.commit()
        return cur.lastrowid
    except:
        raise HTTPException(
            status_code=500, detail='Internal server error')


def add_new_parameter(cur, con, row):
    try:
        type_of_parameter = 'numeric' if row[1] == int else 'char'
        cur.execute(f"""
            INSERT INTO Parameter (name,value_type)
            VALUES('{row[0]}','{type_of_parameter}');
        """)
        con.commit()
    except:
        raise HTTPException(
            status_code=500, detail='Internal server error')


def get_parameter_id(cur, row):
    try:
        parameter_id_res = cur.execute(
            f"SELECT id FROM Parameter WHERE name = '{row[0]}'")
        return parameter_id_res.fetchone()
    except:
        raise HTTPException(
            status_code=404, detail='Parameter not found')


def add_parameter_values_to_event_data(cur, con, row, parameter_id, event_id):
    try:
        numeric_value = row[1] if is_integer_num(row[1]) else None
        char_value = json.dumps(row[1]) if not is_integer_num(row[1]) else None
        cur.execute(f"""
            INSERT INTO EventData (value_numeric, value_char, parameter_id, event_id)
            VALUES('{numeric_value}','{char_value}', '{parameter_id[0]}', '{event_id}');
        """)

        con.commit()
    except:
        raise HTTPException(
            status_code=500, detail='Internal server error')