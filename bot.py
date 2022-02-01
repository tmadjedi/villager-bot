from villager_bot.villager_bot import VillagerBot

import json
import asyncio


if __name__ == '__main__':
    with open('config.json') as f:
        config = json.load(f)

    bot = VillagerBot(config)
    asyncio.run(bot.run_forever())

