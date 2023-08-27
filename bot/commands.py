from aiogram import Bot
from aiogram.types import (
    BotCommand,
    BotCommandScopeAllChatAdministrators,
    BotCommandScopeAllGroupChats,
    BotCommandScopeAllPrivateChats,
)


async def set_bot_commands(bot: Bot) -> None:
    uk_commands = (
        (
            [
                BotCommand(
                    command="start", description="Вивести стартове повідомлення"
                ),
                BotCommand(
                    command="calendar",
                    description="Переглянути всі дні народження групи",
                ),
                BotCommand(command="reset", description="Змінити дані про себе"),
                BotCommand(command="removeme", description="Видалити дані про себе"),
                BotCommand(
                    command="donate",
                    description="Допомогти проекту"
                )
            ],
            BotCommandScopeAllPrivateChats(),
        ),
        (
            [
                BotCommand(
                    command="start",
                    description="Вивести повідомлення з пропозицією додати ДН до календаря групи",
                ),
                BotCommand(
                    command="donate",
                    description="Допомогти проекту"
                )
            ],
            BotCommandScopeAllGroupChats(),
        ),
        (
            [
                BotCommand(
                    command="start",
                    description="Вивести повідомлення з пропозицією додати ДН до календаря групи",
                ),
                BotCommand(
                    command="collect",
                    description="Увімкнути чи вимкнути збори грошей (тільки для адміністраторів групи)",
                ),
            ],
            BotCommandScopeAllChatAdministrators(),
        ),
    )
    for commands, scope in uk_commands:
        await bot.set_my_commands(commands=commands, scope=scope, language_code="uk")
