from datetime import date, datetime
from typing import Any, Dict

import pytz
from aiogram import Bot, F
from aiogram.enums import ChatMemberStatus, ContentType
from aiogram.exceptions import TelegramForbiddenError, TelegramNotFound
from aiogram.filters import ExceptionTypeFilter
from aiogram.types import CallbackQuery, ErrorEvent, Message, User
from aiogram_dialog import ChatEvent, Dialog, DialogManager, ShowMode, StartMode, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Next, Row, Select, SwitchTo
from aiogram_dialog.widgets.kbd.calendar_kbd import ManagedCalendar, OnDateSelected
from aiogram_dialog.widgets.kbd.select import OnItemClick
from aiogram_dialog.widgets.text import Multi
from aiogram_i18n import I18nContext
from babel.dates import format_datetime
from sqlalchemy.orm import selectinload

from bot.enums import ConfirmTypes, Gender, Language
from bot.keyboards.custom_calendar import CustomCalendar
from bot.models import Group
from bot.models import User as UserModel
from bot.repositories.group import GroupFilter
from bot.repositories.uow import UnitOfWork
from bot.repositories.user import UserFilter
from bot.services.geo_service import GeoService
from bot.states.form import Form
from bot.utils.i18n_format import I18NFormat


async def get_confirm_data(chat_id: int, user_id: int, bot: Bot) -> Dict[str, Any]:
    chat = await bot.get_chat(chat_id=chat_id)
    member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
    return {
        "title": chat.title,
        "is_admin": True if member.status in (ChatMemberStatus.CREATOR, ChatMemberStatus.ADMINISTRATOR) else False
    }


async def start_form(message: Message, chat_id: int, uow: UnitOfWork, i18n: I18nContext, bot: Bot, dialog_manager: DialogManager) -> None:
    group = await uow.groups.find_one(GroupFilter(id=chat_id), options=[selectinload(Group.users)])
    user = await uow.users.find_one(UserFilter(id=message.chat.id), options=[selectinload(UserModel.groups)])

    if not group:
        await message.answer(i18n.error.group.notfound())
        return

    data = await get_confirm_data(chat_id, message.chat.id, bot)
    if user:
        if user in group.users:
            await message.answer(i18n.private.already.added(**data))
        else:
            group.users.append(user)
            await message.answer(i18n.private.form.confirm(**data))
        return

    await message.answer(i18n.private.form.start(title=data["title"]))
    await dialog_manager.start(Form.birthday, mode=StartMode.RESET_STACK, show_mode=ShowMode.SEND)
    dialog_manager.dialog_data["chat_id"] = chat_id


class OnSelectDate(OnDateSelected):
    async def __call__(self, event: ChatEvent, select: ManagedCalendar, dialog_manager: DialogManager, selected_date: date) -> None:
        dialog_manager.dialog_data["birthday"] = selected_date.strftime("%d/%m/%Y")
        await dialog_manager.next()


class OnSelectGender(OnItemClick[Any, Gender]):
    async def __call__(self, event: CallbackQuery, select: Any, dialog_manager: DialogManager, data: Gender) -> None:
        dialog_manager.dialog_data["gender"] = data
        await dialog_manager.next()


async def get_confirm_birthday_data(dialog_manager: DialogManager, **_: Any) -> Dict[str, Any]:
    return {
        "birthday": datetime.strptime(dialog_manager.dialog_data["birthday"], "%d/%m/%Y"),
        "item": dialog_manager.dialog_data.get("gender")
    }


async def address_handler(message: Message, message_input: MessageInput, manager: DialogManager) -> None:
    locale = manager.middleware_data.get("locale", Language.UK)
    i18n: I18nContext = manager.middleware_data["i18n"]
    async with GeoService() as api:
        address = await api.get_address(message.text, locale.replace("_", "-"))  # type: ignore[arg-type]
        if not address:
            await message.answer(i18n.error.address.notfound())
            return
        timezone = await api.get_timezone(address.latitude, address.longitude)
    manager.dialog_data["address"] = address.address
    manager.dialog_data["timezone"] = timezone
    await manager.next()


async def get_confirm_address_data(dialog_manager: DialogManager, **_: Any) -> Dict[str, Any]:
    locale = dialog_manager.middleware_data.get("locale", Language.UK)
    return {
        "address": dialog_manager.dialog_data.get("address"),
        "now": format_datetime(
            datetime=datetime.now(pytz.UTC),
            format="dd MMMM, HH:mm",
            tzinfo=dialog_manager.dialog_data.get("timezone"),
            locale=locale
        )
    }


async def confirm_user(callback: CallbackQuery, widget: Button, manager: DialogManager) -> None:
    data = manager.dialog_data
    manager.middleware_data.get("locale", Language.UK)
    uow: UnitOfWork = manager.middleware_data["uow"]
    bot: Bot = manager.middleware_data["bot"]
    info = {
        "fullname": callback.from_user.full_name,
        "gender": Gender(data["gender"]),
        "timezone": data["timezone"],
        "birthday": datetime.strptime(data["birthday"], "%d/%m/%Y"),
    }
    result = {}
    user = UserModel(id=callback.from_user.id, **info)
    if await uow.users.check_exists(UserFilter(id=callback.from_user.id)):
        result["reset"] = True
    else:
        result.update(await get_confirm_data(data["chat_id"], callback.from_user.id, bot))
    await uow.users.merge(user)
    await manager.done(result)


async def print_result(data: Dict[str, Any], manager: DialogManager) -> None:
    user: User = manager.middleware_data["event_from_user"]
    bot: Bot = manager.middleware_data["bot"]
    i18n: I18nContext = manager.middleware_data["i18n"]
    if "reset" in data:
        await bot.send_message(user.id, i18n.private.reset.confirm())
        return
    await bot.send_message(user.id, i18n.private.form.confirm(**data))


async def group_not_found(event: ErrorEvent, message: Message, i18n: I18nContext) -> None:
    await message.answer(i18n.error.group.notfound())


form = Dialog(
    Window(
        Multi(
            I18NFormat("private-form-birthday", when=~F["dialog_data"]),
            I18NFormat("private-form-disallow-birthday", when=F["dialog_data"])
        ),
        CustomCalendar(
            on_click=OnSelectDate(),
            id="calendar"
        ),
        state=Form.birthday
    ),
    Window(
        I18NFormat("private-form-gender"),
        Select(
            I18NFormat("gender-names"),
            items=list(Gender),
            item_id_getter=lambda x: x.value,
            on_click=OnSelectGender(),
            id="gender"
        ),
        state=Form.gender
    ),
    Window(
        I18NFormat("private-form-confirm-birthday"),
        Row(
            SwitchTo(I18NFormat("confirm", confirm=ConfirmTypes.NO), state=Form.birthday, id="declined"),
            Next(I18NFormat("confirm", confirm=ConfirmTypes.YES))
        ),
        getter=get_confirm_birthday_data,
        state=Form.confirm_birthday
    ),
    Window(
        I18NFormat("private-form-address"),
        MessageInput(address_handler, content_types=[ContentType.TEXT]),
        state=Form.address
    ),
    Window(
        I18NFormat("private-form-confirm-address"),
        Row(
            SwitchTo(I18NFormat("confirm", confirm=ConfirmTypes.NO), state=Form.address, id="declined"),
            Button(
                I18NFormat("confirm", confirm=ConfirmTypes.YES),
                on_click=confirm_user,
                id="confirm"
            )
        ),
        getter=get_confirm_address_data,
        state=Form.confirm_address
    ),
    on_close=print_result
)

form.error.register(
    group_not_found,
    ExceptionTypeFilter(TelegramForbiddenError, TelegramNotFound),
    F.update.message.as_("message") | F.update.callback_query.message.as_("message")
)
