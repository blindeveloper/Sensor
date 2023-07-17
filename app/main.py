from fastapi import FastAPI, Query, HTTPException
from app.utils import is_falsy, get_list_of_json_data, get_request_params, get_fe_ready_record
from app.event_handler import process_new_event
from app.queries import get_latest_weather, get_event_data_in_range
from app.tables import build_tables
from app.data_structures import RawClimateItem, PathItem
import sqlite3

con = sqlite3.connect("climate_data_hub.db", check_same_thread=False)
cur = con.cursor()
build_tables(cur)
app = FastAPI()


@app.post('/weather')
def add_weather_record(raw_climate_record: RawClimateItem):
    process_new_event(raw_climate_record, cur, con)
    raise HTTPException(status_code=200, detail='Record added')


@app.post('/day-of-weather')
def load_day_of_weather_data(path_record: PathItem):
    # get list of json data for specific day
    list_of_events = get_list_of_json_data(path_record.month, path_record.day)
    if is_falsy(list_of_events):
        raise HTTPException(
            status_code=404, detail='Provided path is not found')
    else:
        for event in list_of_events:
            process_new_event(event, cur, con)
        raise HTTPException(status_code=200, detail='Database updated')


@app.get('/weather')
def get_weather_record(
    range_h: float = Query(None, description='Range of time in hours'),
    segment_h: float = Query(
        None, description='Segment of time in hours. 15 min = 0.25 h, 30 min = 0.5 h, 1 d = 24 h'),
    is_average: bool = Query(None, description='Average flag'),
    weather_param: str = Query(
        None, description='Weather parameter like or radiation_sum_j_cm2 wind_direction_degrees')
):
    last_record = get_latest_weather(cur)
    if is_falsy(range_h):
        return get_fe_ready_record(last_record)

    request_params = get_request_params(
        last_record, segment_h, range_h, is_average, weather_param)

    return get_event_data_in_range(request_params, cur)
