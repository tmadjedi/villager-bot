from villager_bot.villager_bot import VillagerBot

import json
import asyncio

from dotenv import load_dotenv


if __name__ == '__main__':
    load_dotenv()

    bot = VillagerBot()
    asyncio.run(bot.run_forever())
