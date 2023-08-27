from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from babel import Locale
from babel.dates import format_datetime
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from aiogram.exceptions import TelegramBadRequest
import structlog

from bot.repositories.congratulation import CongratulationFilter
from bot.repositories.uow import UnitOfWork
from bot.translator.hub import Translator


class Scheduler:
    def __init__(self, bot: Bot, async_session: async_sessionmaker[AsyncSession]):
        self._bot = bot
        self._async_sessionmaker = async_session
        self._translator_hub = Translator()
        self._scheduler = AsyncIOScheduler()
        self._logger = structlog.get_logger()

    async def start(self):
        async with self._async_sessionmaker() as session:
            async with session.begin():
                async with UnitOfWork(session) as uow:
                    await self.today(uow)
                    await self.tomorrow(uow)
                    await self.next_5_day(uow)
                    self._scheduler.start()

    async def today(self, uow: UnitOfWork):
        today = await uow.users.get_birthday_persons()
        for birthday in today:
            for group in birthday.groups:
                congratulation = await uow.congratulations.random(CongratulationFilter(language=group.language))
                print(congratulation.message)
                username = f'<a href="tg://user?id={birthday.user_id}">{birthday.fullname}</a>'
                await self._bot.send_document(
                    group.chat_id,
                    congratulation.photo_file_id,
                    caption=congratulation.message.format(username=username)
                )

    async def tomorrow(self, uow: UnitOfWork):
        tomorrow = await uow.users.get_birthday_persons(1)
        for birthday in tomorrow:
            for group in birthday.groups:
                users = await uow.users.get_birthday_group_users(birthday.id, group.id)
                for user in users:
                    try:
                        chat_member = await self._bot.get_chat_member(group.chat_id, birthday.user_id)
                        photos = await chat_member.user.get_profile_photos(limit=1)
                        caption = self._translator_hub(user.language).birthday.tomorrow(
                            group=group.title,
                            fullname=birthday.fullname,
                            date=format_datetime(
                                datetime=birthday.birthday,
                                format="dd MMMM",
                                tzinfo=user.timezone,
                                locale=Locale.parse(user.language, sep='-')
                            )
                        )
                        if photos:
                            await self._bot.send_photo(
                                user.user_id,
                                photos.photos[0][-1].file_id,
                                caption=caption
                            )
                        else:
                            await self._bot.send_message(
                                user.user_id,
                                caption
                            )
                    except TelegramBadRequest:
                        await self._logger.adebug(f"User {user} not send")

    async def next_5_day(self, uow: UnitOfWork):
        next_5_day = await uow.users.get_birthday_persons(5)
        for birthday in next_5_day:
            for group in birthday.groups:
                users = await uow.users.get_birthday_group_users(birthday.id, group.id)
                for user in users:
                    try:
                        chat_member = await self._bot.get_chat_member(group.chat_id, birthday.user_id)
                        photos = await chat_member.user.get_profile_photos(limit=1)
                        caption = self._translator_hub(user.language).get(
                            "birthday-next-5-day",
                            group=group.title,
                            fullname=birthday.fullname,
                            date=format_datetime(
                                datetime=birthday.birthday,
                                format="dd MMMM",
                                tzinfo=user.timezone,
                                locale=Locale.parse(user.language, sep='-')
                            )
                        )
                        if photos:
                            await self._bot.send_photo(
                                user.user_id,
                                photos.photos[-1][-1].file_id,
                                caption=caption
                            )
                        else:
                            await self._bot.send_message(
                                user.user_id,
                                caption
                            )
                    except TelegramBadRequest:
                        await self._logger.adebug(f"User {user} not send")
