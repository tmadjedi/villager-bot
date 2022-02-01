import asyncio
import socket
import sys
import logging
import time
from logging.handlers import TimedRotatingFileHandler
 
 
class IRC:
 
    def __init__(self):  
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

        handler = TimedRotatingFileHandler(filename='logs/irc.log', when='midnight')
        handler.setLevel(logging.DEBUG)

        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        ch.setFormatter(formatter)

        logger.addHandler(handler)
        logger.addHandler(ch)
        self.logger = logger

    async def privmsg(self, chan, msg):
        self.writer.write(("PRIVMSG #" + chan + " :" + msg + "\r\n").encode())
        await self.writer.drain()

    async def send(self, msg):
        self.writer.write((msg + "\r\n").encode())
        await self.writer.drain()
 
    async def connect(self, server, port, nick, oauth):
        self.logger.info(f'Connecting to {server}')

        self.reader, self.writer = await asyncio.open_connection(host=server, port=port)

        connect_lines = [
            'CAP REQ :twitch.tv/tags\r\n'.encode(),
            'CAP REQ :twitch.tv/commands\r\n'.encode(),
            f'PASS {oauth} \r\n'.encode(),
            f'NICK {nick} \r\n'.encode()]

        self.writer.writelines(connect_lines)
        await self.writer.drain()

        messages = await self.reader.read(2048)
        messages = messages.decode()
        lines = filter(None, messages.split('\r\n'))

        for line in lines:
            self.logger.info(line)

    async def disconnect(self):
        self.writer.close()
        await self.writer.wait_closed()

    async def close(self):
        self.logger.handlers = []

    async def join(self, channel):
        self.writer.write((f'JOIN #{channel}\r\n').encode())
        await self.writer.drain()
        self.logger.info(f'Joined {channel}')

    async def parse_line(self, line):
        event = {
            'tags': '',
            'code': '',
            'message': ''
        }

        if line.startswith('@'):
            tags = line[1:].split(' ')[0]
            event['tags'] = dict([tag.split('=', 1) for tag in tags.split(';')])
            line = line.split(' ', 1)
            line = line[1]

        if line.startswith(':'):
            parts = line[1:].split(' :', 1)
            args = parts[0].split(' ')

            if len(args) > 1:
                event['code'] = args[1]

                if len(args) > 2:
                    event['channel'] = args[2].strip()

                if len(parts) == 2:
                    event['message'] = parts[1].strip()
        else:
            parts = line.split(' :')
            event['code'] = parts[0]
            if len(parts) > 1:
                event['message'] = parts[1]
 
        if event['code'] == 'PING':                      
            self.writer.write(("PONG :" + event['message'] + "\r\n").encode()) 
            await self.writer.drain()
            self.logger.info('Sent PONG')
 
        self.logger.debug(f'Event: {event}')
        return event

    async def get_events(self):
        message = await self.reader.readuntil(separator='\r\n'.encode())
        message = message.decode()
        self.logger.debug(f'Message: {message}')
        events = [await self.parse_line(message)]
        return events
