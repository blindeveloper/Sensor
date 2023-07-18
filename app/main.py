from fastapi import FastAPI, Query, HTTPException
from app.utils import get_list_of_json_data, get_request_params, get_fe_ready_record
from app.event_handler import process_new_event
from app.queries import get_latest_weather, get_event_data_in_range, get_average_with_param, get_total_average, get_average_with_segment
from app.tables import build_tables
from app.data_structures import PathItem, RawClimateList, RawClimateItem
import os
import psycopg2

connection = psycopg2.connect(user=os.os.environ("POSTGRES_USER"),
                                  password=os.os.environ("POSTGRES_PASSWORD"),
                                  host="127.0.0.1",
                                  port="5432",
                                  database=os.os.environ("POSTGRES_DB"))

    # Create a cursor to perform database operations
    cursor = connection.cursor()
build_tables(cur)
app = FastAPI()


@app.post('/weather')
def add_weather_record(raw_climate_record_list: RawClimateList):
    report = []
    for raw_climate_record in raw_climate_record_list.root:
        report.append(process_new_event(raw_climate_record, cur, con))
    return report


@app.post('/day-of-weather')
def load_day_of_weather_data(path_record: PathItem):
    # get list of json data for specific day
    list_of_events = get_list_of_json_data(path_record.month, path_record.day)
    if not list_of_events:
        raise HTTPException(
            status_code=404, detail='Provided path is not found')
    else:
        report = []
        for event in list_of_events:
            report.append(process_new_event(event, cur, con))
        return report


@app.get('/weather')
def get_weather_record(
    range_h: float = Query(None, description='Range of time in hours'),
    segment_h: float = Query(
        None, description='Segment of time in hours. 15 min = 0.25 h, 30 min = 0.5 h, 1 d = 24 h'),
    is_average: bool = Query(None, description='Average flag'),
    weather_param: str = Query(
        None, description='Weather parameter like radiation_sum_j_cm2 or wind_direction_degrees')
):
    last_record = get_latest_weather(cur)
    if not range_h:
        return get_fe_ready_record(last_record)

    request_params = get_request_params(
        last_record, segment_h, range_h, is_average, weather_param)

    if is_average:
        if not weather_param and not segment_h:
            return get_total_average(cur, request_params)
        if weather_param and not segment_h:
            return get_average_with_param(cur, request_params)
        if segment_h:
            return get_average_with_segment(cur, request_params)

    return get_event_data_in_range(cur, request_params)
