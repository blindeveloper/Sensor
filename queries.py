from utils import get_list_of_increments, is_falsy, get_fe_ready_record


def get_increments(list):
    res = ''
    for idx, el in enumerate(list):
        if idx == 0:
            res += f"strftime('%M', ts) = '{el}'"
        else:
            res += f" OR strftime('%M', ts) = '{el}'"
    return res


def get_sql_events_in_range_segment(req):
    if not is_falsy(req['segment_h']) and is_falsy(req['is_average']):
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


def get_event_data_in_range(request_params, cur):
    list_of_events_with_data = []
    search_string = get_sql_events_in_range_segment(request_params)
    event_list_res = cur.execute(search_string)
    event_list = event_list_res.fetchall()
    for event in event_list:
        single_event = get_data_for_single_event(event, cur)
        fe_ready_event = get_fe_ready_record(single_event)
        list_of_events_with_data.append(fe_ready_event)
    return list_of_events_with_data


def get_latest_weather(cur):
    latest_event_res = cur.execute(
        "SELECT * FROM Event ORDER BY ts DESC LIMIT 1")
    latest_event = latest_event_res.fetchone()
    return get_data_for_single_event(latest_event, cur)


def get_data_for_single_event(event, cur):
    event_data_res = cur.execute(
        f"SELECT * FROM EventData WHERE event_id = '{event[0]}'")
    event_data = event_data_res.fetchall()
    return {
        'event': event,
        'event_data': event_data
    }
