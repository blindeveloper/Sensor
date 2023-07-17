# Sensor measurements API

Provide detailed information on your product and how to run it here

1. run `docker-compose build`
2. run `docker-compose up`
3. go to http://0.0.0.0:8000/docs to test API
4. call POST /day-of-weather call with `{ "month": "may", "day": "01"}` in body to load full day of data
5. call GET /weather with no params to get latest record
6. call GET /weather with no range_h = 1 to get records for the last hour
7. call GET /weather with no range_h = 1 and segment_h = 0.25 to get records for the last hour in 15 min increment
