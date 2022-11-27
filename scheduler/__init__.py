import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any

import aioschedule
from aiogram import Bot

from messages.sheduler import *


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
                        {"$eq": [{"$dayOfMonth": "$birthday"}, {"$dayOfMonth": datetime.today()}]},
                        {"$eq": [{"$month": "$birthday"}, {"$month": datetime.today()}]},
                        {"$eq": [{"$hour": {"date": "$$NOW", "timezone": "$timezone"}}, 9]}
                    ]
                }
            }
        }]
        users = self.database.users.aggregate(request)
        async for user in users:
            for group in user["groups"]:
                logging.debug(user)

    async def tomorrow(self):
        request = [{
            "$match": {
                "$expr": {
                    "$and": [
                        {"$eq": [{"$dayOfMonth": "$birthday"}, {"$dayOfMonth": datetime.today() + timedelta(days=1)}]},
                        {"$eq": [{"$month": "$birthday"}, {"$month": datetime.today() + timedelta(days=1)}]},
                        {"$eq": [{"$hour": {"date": "$$NOW", "timezone": "$timezone"}}, 9]}
                    ]
                }
            }
        }]
        tomorrow = self.database.users.aggregate(request)
        async for birthday in tomorrow:
            photos = await self.bot.get_user_profile_photos(birthday["_id"], limit=1)
            for group_id in birthday["groups"]:
                group = await self.database.groups.find_one({"_id": group_id})
                for user in filter(lambda i: i['_id'] != birthday["_id"], group["users"]):
                    if photos.total_count == 0 or not photos:
                        await self.bot.send_message(user["_id"], (await TOMORROW.render_async(user=birthday, title=group["title"])))
                    else:
                        await self.bot.send_photo(user["_id"], photos.photos[0][-1].file_id, caption=(await TOMORROW.render_async(user=birthday, title=group["title"])))

    async def next_5_day(self):
        request = [{
            "$match": {
                "$expr": {
                    "$and": [
                        {"$eq": [{"$dayOfMonth": "$birthday"}, {"$dayOfMonth": datetime.today() + timedelta(days=5)}]},
                        {"$eq": [{"$month": "$birthday"}, {"$month": datetime.today() + timedelta(days=5)}]},
                        {"$eq": [{"$hour": {"date": "$$NOW", "timezone": "$timezone"}}, 9]}
                    ]
                }
            }
        }]
        next_5_day = self.database.users.aggregate(request)
        async for birthday in next_5_day:
            photos = await self.bot.get_user_profile_photos(birthday["_id"], limit=1)
            for group_id in birthday["groups"]:
                group = await self.database.groups.find_one({"_id": group_id})
                for user in filter(lambda i: i['_id'] != birthday["_id"], group["users"]):
                    if photos.total_count == 0:
                        await self.bot.send_message(user["_id"], (
                            await NEXT_5_DAY.render_async(user=birthday, title=group["title"])))
                    else:
                        await self.bot.send_photo(user["_id"], photos.photos[0][-1].file_id, caption=(
                            await NEXT_5_DAY.render_async(user=birthday, title=group["title"])))
