# Twitch Animal Crosisng Villager Bot
## Setup
Create a heroku app, and create a Postgres database. The following environment variables are required to be configured in Heroku for deployment or passed into the docker container at runtime locally.
```
IRC_SERVER=irc.chat.twitch.tv
IRC_PORT=6667
IRC_NICK=<bot nick/account name, lowercase>
OAUTH=<twitch oauth token>
HEROKU_API_KEY=<heroku API key>
APP_NAME=<heroku app name>
SCHEMA=<db schema>
```

## Build
Build the docker image with the following command.
```
docker build -t villager-bot .
```

## Run Locally
```
sudo docker run villager-bot \
-e IRC_SERVER=irc.chat.twitch.tv \
-e IRC_PORT=6667 \
-e IRC_NICK=<> \
-e OAUTH=<> \
-e HEROKU_API_KEY=<> \
-e APP_NAME=<> \
-e SCHEMA=<>
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
