FROM python:3.10.7-alpine3.16

WORKDIR /app

RUN python -m venv .venv
ENV PATH=/app/.venv/bin:${PATH}

RUN apk add postgresql-dev gcc python3-dev musl-dev
COPY ./requirements.txt /app/requirements.txt

RUN /app/.venv/bin/pip install --no-cache-dir --upgrade -r requirements.txt

COPY . /app

CMD ["/app/.venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]