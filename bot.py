from villager_bot import VillagerBot

import json


if __name__ == '__main__':
    with open('config.json') as f:
        config = json.load(f)

    bot = VillagerBot(config)
    bot.run_forever()
