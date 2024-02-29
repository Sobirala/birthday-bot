from typing import List, TypedDict

from aiogram import Bot
from aiogram.types import (
    BotCommand,
    BotCommandScopeAllChatAdministrators,
    BotCommandScopeAllGroupChats,
    BotCommandScopeAllPrivateChats,
    BotCommandScopeChat,
    BotCommandScopeChatAdministrators,
    BotCommandScopeChatMember,
    BotCommandScopeDefault,
)


class ScopeCommands(TypedDict):
    commands: List[BotCommand]
    scope: BotCommandScopeDefault | BotCommandScopeAllPrivateChats | BotCommandScopeAllGroupChats | BotCommandScopeAllChatAdministrators | BotCommandScopeChat | BotCommandScopeChatAdministrators | BotCommandScopeChatMember | None


class LanguageCommands(TypedDict):
    commands: List[ScopeCommands]
    language_code: str


async def set_bot_commands(bot: Bot) -> None:
    all_commands: List[LanguageCommands] = [
        {
            "commands": [
                {
                    "scope": BotCommandScopeAllPrivateChats(),
                    "commands": [
                        BotCommand(command="start", description="Вивести стартове повідомлення"),
                        BotCommand(command="calendar", description="Переглянути всі дні народження групи"),
                        BotCommand(command="reset", description="Змінити дані про себе"),
                        BotCommand(command="removeme", description="Видалити дані про себе"),
                        BotCommand(command="donate", description="Допомогти проекту")
                    ]
                },
                {
                    "scope": BotCommandScopeAllGroupChats(),
                    "commands": [
                        BotCommand(command="start", description="Вивести повідомлення з пропозицією додати ДН до календаря групи"),
                        BotCommand(command="donate", description="Допомогти проекту")
                    ]
                },
                {
                    "scope": BotCommandScopeAllChatAdministrators(),
                    "commands": [
                        BotCommand(command="start", description="Вивести повідомлення з пропозицією додати ДН до календаря групи"),
                        BotCommand(command="collect", description="Увімкнути чи вимкнути збори грошей (тільки для адміністраторів групи)"),
                    ]
                }
            ],
            "language_code": "uk"
        }
    ]
    for lang_commands in all_commands:
        language_code = lang_commands["language_code"]
        for scope_commands in lang_commands["commands"]:
            await bot.set_my_commands(
                commands=scope_commands["commands"],
                scope=scope_commands["scope"],
                language_code=language_code
            )
