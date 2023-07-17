# Sensor measurements API

Provide detailed information on your product and how to run it here

1. run this command ro run fastapi UI for testing
   `uvicorn main:app --reload`
2. go to http://127.0.0.1:8000/docs to test API
3. call POST /day-of-weather call with `{ "month": "may", "day": "01"}` in body to load full day of data
4. call GET /weather with no params to get latest record
5. call GET /weather with no range_h = 1 to get records for the last hour
6. call GET /weather with no range_h = 1 and segment_h = 0.25 to get records for the last hour in 15 min increment
