import asyncio
import requests
import sqlite3
import logging
import datetime
import json
import difflib
from logging.handlers import TimedRotatingFileHandler

from irc import IRC


class VillagerBot:

    def __init__(self, config):

        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        
        handler = TimedRotatingFileHandler(filename='logs/villager_info.log', when='midnight')
        handler.setLevel(logging.DEBUG)
        
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(handler)
        logger.addHandler(ch)
        self.logger = logger

        self.config = config

        conn = sqlite3.connect(self.config['db'])
        cursor = conn.cursor()

        cursor.execute('CREATE TABLE IF NOT EXISTS channels (username text)')

        cursor.close()
        conn.close()

        with open('final_villager_info.json') as f:
            villagers = json.load(f)

        self.villagers = villagers[0]
        self.cooldowns = {}

    async def connect(self):
        irc = IRC()
        await irc.connect(self.config['server'],
            self.config['port'],
            self.config['nick'],
            self.config['oauth'])
        self.irc = irc

    async def join_all_channels(self):
        print('joining channels')
        conn = sqlite3.connect(self.config['db'])
        cursor = conn.cursor()

        cursor.execute('SELECT username FROM channels')
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        channels = [row[0] for row in rows]
        channels.append('isabellesays')
        channels = set(channels)

        for channel in channels:
            await self.irc.join(channel)
            await asyncio.sleep(0.51)

    async def say_info(self, channel, command, sent_time):
        sent_time = datetime.datetime.fromtimestamp(sent_time / 1000)

        tokens = command.split(None, 1)
        if len(tokens) < 2:
            await self.irc.privmsg(channel,
                'Usage: !villager <villager name>')
            return

        villager_name = tokens[1].lower().replace(' ', '_')

        if villager_name not in self.villagers:
            message = 'Couldn\'t find the specified villager :('

            villagers = self.villagers.keys()
            match = difflib.get_close_matches(villager_name, villagers, n=1)
            if match:
                message += f" did you mean {self.villagers[match[0]]['name']}?"

            await self.irc.privmsg(channel, message)
            response_time = datetime.datetime.now() - sent_time
            self.logger.info(f'{channel} - {response_time.total_seconds()} - {tokens[1]} - {villager_name} - NOT FOUND')
            return

        if channel not in self.cooldowns:
            cooldown = datetime.datetime.now() + datetime.timedelta(seconds=5)
            self.cooldowns[channel] = { villager_name: cooldown }
        elif channel in self.cooldowns and villager_name in self.cooldowns[channel]:
            if self.cooldowns[channel][villager_name] > datetime.datetime.now():
                self.logger.info(f'{channel} - ON COOLDOWN - {villager_name}')
                return
            else:
                del self.cooldowns[channel][villager_name]
        elif channel in self.cooldowns and villager_name not in self.cooldowns[channel]:
            cooldown = datetime.datetime.now() + datetime.timedelta(seconds=5)
            self.cooldowns[channel][villager_name] = cooldown

        # clean up cooldowns
        if channel in self.cooldowns:
            for villager in list(self.cooldowns[channel]):
                if self.cooldowns[channel][villager] <= datetime.datetime.now():
                    del self.cooldowns[channel][villager]

        info = self.villagers[villager_name]
        message = f"{info['name']} is a {info['personality'].lower()} {info['species'].lower()}, {info['phrase']}! More info: {info['link']}"
        await self.irc.privmsg(channel, message)
        response_time = datetime.datetime.now() - sent_time
        self.logger.info(f'{channel} - {response_time.total_seconds()} - {info["name"]}')

    async def handle_add(self, username):
        conn = sqlite3.connect(self.config['db'])
        cursor = conn.cursor()

        cursor.execute('SELECT username FROM channels')
        rows = cursor.fetchall()
        channels = [row[0] for row in rows]

        if username in channels:
            await self.irc.privmsg('isabellesays', f'I am already in your channel, {username}')
            self.logger.info(f'{username} - ALREADY JOINED')
            return

        cursor.execute('INSERT INTO channels VALUES (?)', (username,))
        conn.commit()

        cursor.close()
        conn.close()

        await self.irc.send(f'JOIN #{username}')
        await self.irc.privmsg('isabellesays', f'I have joined your channel, {username}')
        self.logger.info(f'{username} - JOINED')

    async def handle_remove(self, username):
        conn = sqlite3.connect(self.config['db'])
        cursor = conn.cursor()

        cursor.execute('DELETE FROM channels WHERE username = (?)', (username,))
        conn.commit()

        cursor.close()
        conn.close()

        await self.irc.send(f'PART #{username}')
        await self.irc.privmsg('isabellesays', f'I have left your channel, @{username}')
        self.logger.info(f'{username} - LEFT')

    async def handle_help(self):
        await self.irc.privmsg('isabellesays', 'Please see the panels below for usage details!')
        self.logger.info(f'HELPED')

    async def bot_loop(self):
        while True:
            try:
                events = await self.irc.get_events()
            except RuntimeError:
                self.logger.debug('Error encountered, stopping loop')
                break
            
            for event in events:
                if (event['code'] == 'PRIVMSG' and
                    event['message'].startswith('!villager')):
                    await self.say_info(event['channel'][1:],
                                  event['message'],
                                  int(event['tags']['tmi-sent-ts']))

                elif (event['code'] == 'PRIVMSG' and
                      event['channel'][1:] == 'isabellesays' and
                      event['message'].startswith('!help')):
                    await self.handle_help()

                elif (event['code'] == 'PRIVMSG' and
                      event['channel'][1:] == 'isabellesays' and
                      event['message'].startswith('!join')):
                    await self.handle_add(event['tags']['display-name'].lower())

                elif (event['code'] == 'PRIVMSG' and
                      event['channel'][1:] == 'isabellesays' and
                      event['message'].startswith('!leave')):
                    await self.handle_remove(event['tags']['display-name'].lower())

    async def run_forever(self):
        while True:
            await self.connect()

            L = await asyncio.gather(self.join_all_channels(), self.bot_loop())
