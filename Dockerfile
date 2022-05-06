# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

ARG irc_server
ARG irc_port
ARG irc_nick
ARG oauth
ARG heroku_api_key
ARG app_name

ENV IRC_SERVER=$irc_server
ENV IRC_PORT=$irc_port
ENV IRC_NICK=$irc_nick
ENV OAUTH=$oauth
ENV HEROKU_API_KEY=$heroku_api_key
ENV APP_NAME=$app_name

WORKDIR /app
RUN mkdir /app/logs

RUN apt-get update \
    && apt-get -y install libpq-dev gcc

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "bot.py" ]
