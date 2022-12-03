import asyncio
from loguru import logger
from datetime import datetime, timedelta
from typing import Any
import pytz

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from messages.sheduler import *


class Scheduler:
    def __init__(self, bot: Bot, database: Any):
        self.bot: Bot = bot
        self.database: Any = database

    async def start(self):
        scheduler = AsyncIOScheduler(timezone=pytz.UTC)
        scheduler.add_job(self.congratulations, 'cron', minute="01", hour="*")
        scheduler.start()

    async def congratulations(self):
        today = asyncio.create_task(self.today(), name="Today function")
        tomorrow = asyncio.create_task(self.tomorrow(), name="Tomorrow function")
        next_5_day = asyncio.create_task(self.next_5_day(), name="Next 5 day function")
        with logger.catch(message="Scheduler not done"):
            done, pending = await asyncio.wait(
                [today, tomorrow, next_5_day],
                return_when=asyncio.ALL_COMPLETED
            )
            for task in done:
                name = task.get_name()
                logger.debug(f"DONE: {name}")
                exception = task.exception()
                if isinstance(exception, Exception):
                    logger.error(f"{name} threw {exception}")
            for task in pending:
                task.cancel()

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
            congratulation = (await self.database.congratulations.aggregate([{ "$sample": { "size": 1 } }]).to_list(length=1))[0]
            username = f'<a href="tg://user?id={birthday["_id"]}">{birthday["fullname"]}</a>'
            for group_id in birthday["groups"]:
                with logger.catch(message=f"Message not sent to group: {group_id}"):
                    await self.bot.send_document(group_id, congratulation["fileid"], caption=congratulation["message"].format(username=username))


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
                    with logger.catch(message=f"Message not sent to user: {user['_id']}"):
                        if photos.total_count == 0 or not photos:
                            await self.bot.send_message(user["_id"], (
                                await TOMORROW.render_async(user=birthday, title=group["title"])))
                        else:
                            await self.bot.send_photo(user["_id"], photos.photos[0][-1].file_id, caption=(
                                await TOMORROW.render_async(user=birthday, title=group["title"])))

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
                    with logger.catch(message=f"Message not sent to user: {user['_id']}"):
                        if photos.total_count == 0:
                            await self.bot.send_message(user["_id"], (
                                await NEXT_5_DAY.render_async(user=birthday, title=group["title"])))
                        else:
                            await self.bot.send_photo(user["_id"], photos.photos[0][-1].file_id, caption=(
                                await NEXT_5_DAY.render_async(user=birthday, title=group["title"])))
