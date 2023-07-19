# Sensor measurements API

You can run this application with or without docker.

### SETUP WITH NO DOCKER

1. install all packages using `pip install --no-cache-dir --upgrade -r requirements.txt`
2. run `uvicorn app.main:app --reload` in root of project
3. visit `http://127.0.0.1:8000/docs` to test API

### SETUP WITH DOCKER

1. run `docker-compose build`
2. run `docker-compose up`
3. go to `http://0.0.0.0:8000/docs` to test API

### API DESCRIPTION

API is calculating all the results based on latest record timestamp

DATA POPULATION
There 2 ways for data population

- call POST method `/weather` with body as `[{<JsonMeteoData>}, {<JsonMeteoData>}, {<JsonMeteoData>}]`
- call POST `/day-of-weather` with `{ "month": "may", "day": "01"}` in body, where _month_ is the name of folded of days and _day_ is name of folder with JSON data. In this case you will load whole day with one request.

DATA EXPOSING

- for `exposing the _latest_ weather conditions` use GET method `/weather`
- for `exposing the development of the weather parameters over the last 24h in 15 min increments` use GET method `/weather?range_h=24&segment_h=0.25`
- for `exposing the average for each of the weather parameters for the last 24h` use GET method `/weather?range_h=25&is_average=true&weather_param=radiation_sum_j_cm2`
- for `exposing the average of the weather parameters over the last 7 days` use GET method `/weather?range_h=168&is_average=true`

endpoint below is not working correctly with `segment_h=24` range, only with minutes increments, I was doing my best to fix it but had no time anymore. You can run it with `segment_h=0.25` increment to test it

- for `exposing the development of the weather parameters over the last 7 days in 1 day increments (average per day)` use GET method `/weather?range_h=168&segment_h=24&is_average=true`
