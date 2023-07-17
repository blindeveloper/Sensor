from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from utils import is_falsy, get_list_of_json_data
from event_handler import process_new_event

import sqlite3

con = sqlite3.connect("climate_data_hub.db", check_same_thread=False)
cur = con.cursor()
cur.execute(
    """CREATE TABLE IF NOT EXISTS Event(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR,
        range VARCHAR, 
        ts VARCHAR, 
        pt INTEGER)""")

cur.execute(
    """CREATE TABLE IF NOT EXISTS Parameter(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR,
        value_type VARCHAR)""")

cur.execute(
    """CREATE TABLE IF NOT EXISTS EventData(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        value_numeric NUMERIC,
        value_char VARCHAR,
        parameter_id INTEGER,
        event_id INTEGER,
        FOREIGN KEY (parameter_id) REFERENCES Parameter (id),
        FOREIGN KEY (event_id) REFERENCES Event (id));
    """)


class RawClimateItem(BaseModel):
    name: str
    range: dict
    rows: list
    ts: str
    pt: int


class PathItem(BaseModel):
    month: str
    day: str


app = FastAPI()


def get_latest_weather(cur):
    latest_event_res = cur.execute(
        "SELECT * FROM Event ORDER BY ts DESC LIMIT 1")
    latest_event = latest_event_res.fetchone()
    latest_event_id = latest_event[0]
    event_data_res = cur.execute(
        f"SELECT * FROM EventData WHERE event_id = '{latest_event_id}'")
    event_data = event_data_res.fetchall()
    return {
        'event': latest_event,
        'event_data': event_data
    }


@app.post('/weather')
def add_weather_record(raw_climate_record: RawClimateItem):
    process_new_event(raw_climate_record, cur, con)
    return {}


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
    if is_falsy(last_record):
        raise HTTPException(status_code=404, detail='Item not found')

    return last_record
