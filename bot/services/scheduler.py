import pytz
import structlog
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram_i18n.cores.fluent_compile_core import FluentCompileCore
from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore
from babel import Locale
from babel.dates import format_datetime, get_timezone
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from structlog._config import BoundLoggerLazyProxy

from bot.repositories.congratulation import CongratulationFilter
from bot.repositories.uow import UnitOfWork


class Scheduler:
    def __init__(self, bot: Bot, async_session: async_sessionmaker[AsyncSession], i18n_core: FluentCompileCore):
        self._bot = bot
        self._async_sessionmaker = async_session
        self._i18n_core = i18n_core
        self._scheduler = AsyncIOScheduler(timezone=pytz.UTC)
        self._logger = structlog.get_logger()

    def start(self) -> None:
        self._scheduler.add_job(self.today, 'cron', hour="*", minute="01", args=(self._bot, self._async_sessionmaker, self._logger))
        self._scheduler.add_job(self.tomorrow, 'cron', hour="*", minute="01", args=(self._bot, self._async_sessionmaker, self._i18n_core, self._logger))
        self._scheduler.add_job(self.next_5_day, 'cron', hour="*", minute="01", args=(self._bot, self._async_sessionmaker, self._i18n_core, self._logger))
        self._scheduler.start()

    @staticmethod
    async def today(bot: Bot, async_session: async_sessionmaker[AsyncSession], logger: BoundLoggerLazyProxy) -> None:
        async with async_session() as session, session.begin():
            async with UnitOfWork(session) as uow:
                today = await uow.users.get_birthday_persons()
                for birthday in today:
                    for group in birthday.groups:
                        congratulation = await uow.congratulations.random(CongratulationFilter(language=group.language))
                        if congratulation:
                            username = f'<a href="tg://user?id={birthday.id}">{birthday.fullname}</a>'
                            try:
                                await bot.send_document(
                                    group.id,
                                    congratulation.photo_file_id,
                                    caption=congratulation.message.format(username=username)
                                )
                            except TelegramBadRequest:
                                await logger.aerror(f"Group with id {group.id} not found")

    @staticmethod
    async def tomorrow(bot: Bot, async_session: async_sessionmaker[AsyncSession], i18n_core: FluentCompileCore, logger: BoundLoggerLazyProxy) -> None:
        async with async_session() as session, session.begin():
            async with UnitOfWork(session) as uow:
                tomorrow = await uow.users.get_birthday_persons(1)
                for birthday in tomorrow:
                    for group in birthday.groups:
                        users = await uow.users.get_birthday_group_users(birthday.id, group.id)
                        for user in users:
                            try:
                                chat_member = await bot.get_chat_member(group.id, birthday.id)
                                photos = await chat_member.user.get_profile_photos(limit=1)
                                caption = i18n_core.get(
                                    "birthday-tomorrow",
                                    user.language,
                                    group=group.title,
                                    fullname=birthday.fullname,
                                    date=format_datetime(
                                        datetime=birthday.birthday,
                                        format="dd MMMM",
                                        tzinfo=get_timezone(user.timezone),
                                        locale=Locale.parse(user.language, sep='-')
                                    )
                                )
                                if photos:
                                    await bot.send_photo(
                                        user.id,
                                        photos.photos[0][-1].file_id,
                                        caption=caption
                                    )
                                else:
                                    await bot.send_message(user.id, caption)
                            except TelegramBadRequest:
                                await logger.error(f"User {user} not send")

    @staticmethod
    async def next_5_day(bot: Bot, async_session: async_sessionmaker[AsyncSession], i18n_core: FluentCompileCore, logger: BoundLoggerLazyProxy) -> None:
        async with async_session() as session, session.begin():
            async with UnitOfWork(session) as uow:
                next_5_day = await uow.users.get_birthday_persons(5)
                for birthday in next_5_day:
                    for group in birthday.groups:
                        users = await uow.users.get_birthday_group_users(birthday.id, group.id)
                        for user in users:
                            try:
                                chat_member = await bot.get_chat_member(group.id, birthday.id)
                                photos = await chat_member.user.get_profile_photos(limit=1)
                                caption = i18n_core.get(
                                    "birthday-next-5-day",
                                    user.language,
                                    group=group.title,
                                    fullname=birthday.fullname,
                                    date=format_datetime(
                                        datetime=birthday.birthday,
                                        format="dd MMMM",
                                        tzinfo=get_timezone(user.timezone),
                                        locale=Locale.parse(user.language, sep='-')
                                    )
                                )
                                if photos:
                                    await bot.send_photo(
                                        user.id,
                                        photos.photos[-1][-1].file_id,
                                        caption=caption
                                    )
                                else:
                                    await bot.send_message(user.id, caption)
                            except TelegramBadRequest:
                                await logger.aerror(f"User {user} not send")
