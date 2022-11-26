import asyncio
from datetime import datetime, timedelta
from typing import Any
import aioschedule
from aiogram import Bot


class Scheduler:
    def __init__(self, bot: Bot, database: Any):
        self.bot: Bot = bot
        self.database: Any = database

    async def start(self):
        aioschedule.every().hour.at(":01").do(self.today)
        aioschedule.every().hour.at(":01").do(self.tomorrow)
        aioschedule.every().hour.at(":01").do(self.next_5_day)
        asyncio.create_task(self.polling())

    @staticmethod
    async def polling():
        while True:
            await aioschedule.run_pending()
            await asyncio.sleep(1)

    async def today(self):
        request = [{
            "$match": {
                "$expr": {
                    "$and": [
                        {"$eq": [{"$dayOfYear": "$birthday"}, {"$dayOfYear": datetime.today()}]},
                        {"$eq": [{"$hour": {"date": "$$NOW", "timezone": "$timezone"}}, 9]}
                    ]
                }
            }
        }]
        users = self.database.users.aggregate(request)
        async for user in users:
            for group in user["groups"]:
                await self.bot.send_message(group, f"{user['fullname']}")

    async def tomorrow(self):
        request = [{
            "$match": {
                "$expr": {
                    "$and": [
                        {"$eq": [{"$dayOfYear": "$birthday"}, {"$dayOfYear": datetime.today()}]},
                    ]
                }
            }
        }]
        users = self.database.users.aggregate(request)
        async for user in users:
            await self.bot.send_message(user["_id"], f"{ user['fullname'] }")

    async def next_5_day(self):
        request = [{
            "$match": {
                "$expr": {
                    "$and": [
                        {"$eq": [{"$dayOfYear": "$birthday"}, {"$dayOfYear": datetime.today() + timedelta(days=5)}]},
                    ]
                }
            }
        }]
        next_5_day = self.database.users.aggregate(request)
        async for birthday in next_5_day:
            for group_id in birthday["groups"]:
                group = await self.database.groups.find_one({"_id": group_id})
                for user in filter(lambda i: i['_id'] != birthday["_id"], group["users"]):
                    await self.bot.send_message(user["_id"], f"{ birthday['fullname'] }")
