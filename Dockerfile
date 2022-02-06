# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /app
RUN mkdir /app/logs

RUN apt-get update \
    && apt-get -y install libpq-dev gcc

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "bot.py" ]
