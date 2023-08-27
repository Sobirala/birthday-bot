from datetime import date, datetime

from aiogram import Bot
from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from babel.dates import format_datetime
from fluentogram import TranslatorRunner
from sqlalchemy.orm import selectinload

from bot.keyboards.calendar_widget import Calendar, SelectDate
from bot.keyboards.confirm import SelectConfirm, confirm_keyboard
from bot.keyboards.gender import SelectGender, gender_keyboard
from bot.models import Group, User
from bot.repositories.group import GroupFilter
from bot.repositories.uow import UnitOfWork
from bot.repositories.user import UserFilter
from bot.services.google_maps import GoogleMaps
from bot.states.form import Form
from bot.enums import Gender, ConfirmTypes


async def calculate_age(birthdate: date) -> int:
    today = date.today()
    one_or_zero = (today.month, today.day) < (birthdate.month, birthdate.day)
    year_difference = today.year - birthdate.year
    age = year_difference - one_or_zero
    return age


async def start_form(
        message: Message,
        bot: Bot,
        uow: UnitOfWork,
        i18n: TranslatorRunner,
        locale: str,
        command: CommandObject,
        state: FSMContext,
):
    await state.clear()
    group = await uow.groups.find_one(GroupFilter(chat_id=int(command.args)), options=[selectinload(Group.users)])

    user = await uow.users.find_one(UserFilter(user_id=message.chat.id), options=[selectinload(User.groups)])

    if not group:
        return await message.answer(i18n.error.group.notfound())

    try:
        chat = await bot.get_chat(chat_id=command.args)
        member = await bot.get_chat_member(
            chat_id=command.args, user_id=message.chat.id
        )
        if member.status in (ChatMemberStatus.LEFT, ChatMemberStatus.KICKED):
            return await message.answer(i18n.error.group.notfound())
    except TelegramBadRequest:
        return await message.answer(i18n.error.group.notfound())

    if user:
        if group in user.groups:
            return await message.answer(i18n.private.already.added(title=chat.title))
        else:
            group.users.append(user)

            is_admin = False
            if member.status in (
                    ChatMemberStatus.CREATOR,
                    ChatMemberStatus.ADMINISTRATOR,
            ):
                is_admin = True

            return await message.answer(
                i18n.private.form.confirm(title=chat.title, is_admin=is_admin)
            )

    await state.set_state(Form.birthday)
    await state.update_data(chat_id=int(command.args))
    await message.answer(i18n.private.form.start(title=chat.title))
    await message.answer(
        i18n.private.form.birthday(),
        reply_markup=Calendar.generate_keyboard(locale),
    )


async def input_birthday(
        callback: CallbackQuery,
        state: FSMContext,
        callback_data: SelectDate,
        i18n: TranslatorRunner,
):
    birthday = date(callback_data.year, callback_data.month, callback_data.day)
    age = await calculate_age(birthday)
    if age < 0 or age > 120:
        return callback.answer("Неправильна дата")
    await state.update_data(birthday=birthday.strftime("%d/%m/%Y"))
    await state.set_state(Form.gender)
    await callback.message.edit_reply_markup()
    await callback.message.answer(i18n.private.form.gender(), reply_markup=gender_keyboard(i18n))


async def input_gender(
        callback: CallbackQuery,
        state: FSMContext,
        callback_data: SelectGender,
        i18n: TranslatorRunner,
):
    data = await state.update_data(gender=callback_data.gender.value)
    await state.set_state(Form.confirm_birthday)
    await callback.message.edit_reply_markup()
    await callback.message.answer(
        i18n.private.form.confirm.birthday(
            birthday=datetime.strptime(data["birthday"], "%d/%m/%Y"),
            gender=callback_data.gender.value,
        ),
        reply_markup=confirm_keyboard(i18n),
    )


async def confirm_birthday(
        callback: CallbackQuery,
        state: FSMContext,
        callback_data: SelectConfirm,
        i18n: TranslatorRunner,
        locale: str,
):
    await callback.message.edit_reply_markup()
    if callback_data.selected == ConfirmTypes.YES:
        await state.set_state(Form.address)
        await callback.message.answer(i18n.private.form.address())
    else:
        await state.set_state(Form.birthday)
        await callback.message.answer(
            i18n.private.form.disallow.birthday(),
            reply_markup=await Calendar.generate_keyboard(locale),
        )


async def input_address(message: Message, state: FSMContext, i18n: TranslatorRunner, locale: str):
    async with GoogleMaps() as api:
        address = await api.get_address(message.text, "uk-UA")
        if address:
            timezone = await api.get_timezone(address.latitude, address.longitude)
            await state.update_data(timezone=timezone.zone)
            await state.set_state(Form.confirm_address)
            return await message.answer(
                i18n.private.form.confirm.address(
                    address=address.address,
                    now=format_datetime(
                        datetime=datetime.utcnow(),
                        format="dd MMMM, HH:mm",
                        tzinfo=timezone,
                        locale=locale
                    ),
                ),
                reply_markup=confirm_keyboard(i18n),
            )
    return await message.answer(i18n.error.address.notfound())


async def confirm_address(
        callback: CallbackQuery,
        uow: UnitOfWork,
        state: FSMContext,
        callback_data: SelectConfirm,
        i18n: TranslatorRunner,
        bot: Bot,
):
    if callback_data.selected == ConfirmTypes.YES:
        data = await state.get_data()
        info = dict(
            fullname=callback.from_user.full_name,
            gender=Gender(data["gender"]),
            timezone=data["timezone"],
            birthday=datetime.strptime(data["birthday"], "%d/%m/%Y"),
        )
        if await uow.users.check_exists(UserFilter(user_id=callback.from_user.id)):
            user = await uow.users.update(UserFilter(user_id=callback.from_user.id), **info)
        else:
            user = User(user_id=callback.from_user.id, **info)
            await uow.users.create(user)
        if "chat_id" in data:
            group = await uow.groups.find_one(GroupFilter(chat_id=data["chat_id"]), options=[selectinload(Group.users)])
            group.users.append(user)
            try:
                chat = await bot.get_chat(chat_id=data["chat_id"])
                member = await bot.get_chat_member(
                    chat_id=data["chat_id"], user_id=callback.from_user.id
                )
                is_admin = False
                if member.status in (
                        ChatMemberStatus.CREATOR,
                        ChatMemberStatus.ADMINISTRATOR,
                ):
                    is_admin = True
                await callback.message.edit_text(
                    i18n.private.form.confirm(title=chat.title, is_admin=is_admin)
                )
            except TelegramBadRequest:
                return await callback.message.answer(i18n.error.group.notfound())
        else:
            await callback.message.edit_text("Ваші дані оновлено")

        await state.clear()
    else:
        await state.set_state(Form.address)
        await callback.message.edit_text(i18n.private.form.disallow.address())


async def remove_extra(message: Message):
    await message.delete()
