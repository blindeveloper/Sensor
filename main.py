from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from utils import convert_tuples_to_strings, is_integer_num, is_falsy, convert_ts_to_sqlite_format
import sqlite3
import json

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
    serialized_range = json.dumps(raw_climate_record.range)
    converted_ts = convert_ts_to_sqlite_format(raw_climate_record.ts)

    # add new event to Event table
    cur.execute(f"""
        INSERT INTO Event (name,range, ts, pt)
        VALUES('{raw_climate_record.name}','{serialized_range}', '{converted_ts}', '{raw_climate_record.pt}');
    """)
    event_id = cur.lastrowid
    con.commit()
    # load supporting parameters
    parameter_names_res = cur.execute('SELECT name FROM Parameter')
    supporting_parameters = convert_tuples_to_strings(
        parameter_names_res.fetchall())
    # add new parameters if needed to Parameter table
    for row in raw_climate_record.rows:
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
        # add all parameters values to EventData table
        numeric_value = row[1] if is_integer_num(row[1]) else None
        char_value = json.dumps(row[1]) if not is_integer_num(row[1]) else None

        cur.execute(f"""
            INSERT INTO EventData (value_numeric, value_char, parameter_id, event_id)
            VALUES('{numeric_value}','{char_value}', '{parameter_id[0]}', '{event_id}');
        """)

        con.commit()

    return {}


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
