import socket
import sys
import logging
import time
from logging.handlers import TimedRotatingFileHandler
 
 
class IRC:
 
    irc = socket.socket()
  
    def __init__(self):  
        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

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
 
    def privmsg(self, chan, msg):
        self.irc.send(("PRIVMSG #" + chan + " :" + msg + "\r\n").encode())

    def send(self, msg):
        self.irc.send((msg + "\r\n").encode())
 
    def connect(self, server, port, nick, oauth):
        self.logger.info(f'Connecting to {server}')

        self.irc.connect((server, port))
        self.irc.send(('CAP REQ :twitch.tv/tags\r\n').encode())
        self.irc.send(('CAP REQ :twitch.tv/commands\r\n').encode())
        self.irc.send((f'PASS {oauth} \r\n').encode())
        self.irc.send((f'NICK {nick} \r\n').encode())

        messages = self.irc.recv(2048)
        messages = messages.decode()
        lines = filter(None, messages.split('\r\n'))

        for line in lines:
            self.logger.info(line)

    def disconnect(self):
        self.irc.close()

    def join(self, channel):
        self.irc.send((f'JOIN #{channel}\r\n').encode())
        self.logger.info(f'Joined {channel}')

    def parse_line(self, line):
        event = {
            'tags': '',
            'code': '',
            'message': ''
        }

        if line.startswith('@'):
            tags = line[1:].split(' ')[0]
            event['tags'] = dict([tag.split('=') for tag in tags.split(';')])
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
            self.irc.send(("PONG :" + event['message'] + "\r\n").encode()) 
            self.logger.info('Sent PONG')
 
        self.logger.debug(f'Event: {event}')
        return event

    def read_lines(self):
        lines = ''

        while True:
            message = self.irc.recv(2048)

            if not message:
                self.disconnect()
                raise RuntimeError('Socket closed unexpectedly') 
                
            message = message.decode()
            lines += message

            if lines.endswith('\r\n'):
                lines = filter(None, lines.split('\r\n'))
                return list(lines)

    def get_events(self):
        lines = self.read_lines()
        self.logger.debug(f'Lines: {lines}')
        events = [self.parse_line(line) for line in lines]
        return events
