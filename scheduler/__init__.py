import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from messages.sheduler import *


class Scheduler:
    def __init__(self, bot: Bot, database: Any):
        self.bot: Bot = bot
        self.database: Any = database

    async def start(self):
        scheduler = AsyncIOScheduler()
        scheduler.add_job(self.congratulations, 'cron', minute="01", hour="*")
        scheduler.start()

    async def congratulations(self):
        today = asyncio.create_task(self.today(), name="Today function")
        tomorrow = asyncio.create_task(self.tomorrow(), name="Tomorrow function")
        next_5_day = asyncio.create_task(self.next_5_day(), name="Next 5 day function")
        try:
            done, pending = await asyncio.wait(
                [today, tomorrow, next_5_day],
                return_when=asyncio.ALL_COMPLETED
            )
            for task in done:
                name = task.get_name()
                logging.debug(f"DONE: {name}")
                exception = task.exception()
                if isinstance(exception, Exception):
                    logging.error(f"{name} threw {exception}")
            for task in pending:
                task.cancel()
        except Exception as e:
            logging.error(e)

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
        today = self.database.users.aggregate(request)
        async for birthday in today:
            logging.debug(birthday)

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
                    try:
                        if photos.total_count == 0 or not photos:
                            await self.bot.send_message(user["_id"], (
                                await TOMORROW.render_async(user=birthday, title=group["title"])))
                        else:
                            await self.bot.send_photo(user["_id"], photos.photos[0][-1].file_id, caption=(
                                await TOMORROW.render_async(user=birthday, title=group["title"])))
                    except Exception as err:
                        logging.error(err)

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
                    try:
                        if photos.total_count == 0:
                            await self.bot.send_message(user["_id"], (
                                await NEXT_5_DAY.render_async(user=birthday, title=group["title"])))
                        else:
                            await self.bot.send_photo(user["_id"], photos.photos[0][-1].file_id, caption=(
                                await NEXT_5_DAY.render_async(user=birthday, title=group["title"])))
                    except Exception as err:
                        logging.error(err)
