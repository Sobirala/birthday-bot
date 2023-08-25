from aiogram import F, Router
from aiogram.enums.chat_type import ChatType
from aiogram.filters import (
    JOIN_TRANSITION,
    LEAVE_TRANSITION,
    ChatMemberUpdatedFilter,
    Command,
    CommandStart,
)
from aiogram.types import ContentType

from bot.filters.chat_admin import IsChatAdmin
from .collect import collect
from .commands import commands
from .invite_bot import invite_bot, migrate_chat
from .invite_users import invite_users
from .kick_bot import kick_bot
from .kick_member import kick_member
from .rename_group import rename_group
from .start import start_group

router = Router()

router.message.filter(F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}))

router.my_chat_member.register(invite_bot, ChatMemberUpdatedFilter(JOIN_TRANSITION))
router.message.register(migrate_chat, F.migrate_from_chat_id)
router.message.register(invite_users, F.content_type == ContentType.NEW_CHAT_MEMBERS)

router.my_chat_member.register(kick_bot, ChatMemberUpdatedFilter(LEAVE_TRANSITION))
router.message.register(kick_member, F.content_type == ContentType.LEFT_CHAT_MEMBER)

router.message.register(start_group, CommandStart())
router.message.register(collect, Command(commands=["collect"]), IsChatAdmin())
router.message.register(commands, Command(commands=["calendar", "removeme", "help", "reset"]))

router.message.register(rename_group, F.new_chat_title)
