# Twitch Villager Bot
## Setup
Create a heroku app, and create a Postgres database. The following environment variables are required, whether passed into the docker image, or running locally (`.env` file is supported).
```
IRC_SERVER=irc.chat.twitch.tv
IRC_PORT=6667
IRC_NICK=<bot nick/account name, lowercase>
OAUTH=<twitch oauth token>
HEROKU_API_KEY=<heroku API key>
APP_NAME=<heroku app name>
```
Run the bot locally with 
```
python3 bot.py
```

## Build
Build the docker image with the following command.
```
docker build \
-t villager-bot \
--build-arg irc_server=irc.chat.twitch.tv \
--build-arg irc_port=6667 \
--build-arg irc_nick=<>\
--build-arg oauth=<> \
--build-arg heroku_api_key=<> \
--build-arg app_name=<> \
.
```
## Deployment
Deploy the created docker image, and run it with the following commands.
```
docker tag <image id> registry.heroku.com/<app name>/worker
docker push registry.heroku.com/<app name>/worker
heroku container:release worker -a <app name>
# check status
heroku logs
```
