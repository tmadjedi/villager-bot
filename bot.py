from villager_bot.villager_bot import VillagerBot

import json
import asyncio


if __name__ == '__main__':
    bot = VillagerBot()
    asyncio.run(bot.run_forever())
