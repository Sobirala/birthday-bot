import calendar
from datetime import date

from aiogram import Router
from aiogram.filters import Text
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from babel.core import Locale
from fluentogram import TranslatorRunner

MAX_YEAR = 9999
MIN_YEAR = 1


class SelectYear(CallbackData, prefix="select_year"):
    year: int


class SelectMonth(CallbackData, prefix="select_month"):
    month: int
    year: int


class SelectDate(CallbackData, prefix="select_date"):
    day: int
    month: int
    year: int


class ChangeYear(CallbackData, prefix="change_year"):
    year: int


class ChangeMonth(CallbackData, prefix="change_month"):
    year: int


class Calendar:
    @staticmethod
    async def register_widget(router: Router):
        router.callback_query.register(Calendar.change_month, ChangeMonth.filter())
        router.callback_query.register(Calendar.select_month, SelectMonth.filter())
        router.callback_query.register(Calendar.change_year, ChangeYear.filter())
        router.callback_query.register(Calendar.select_year, SelectYear.filter())
        router.callback_query.register(Calendar.reset, Text("reset_calendar"))

    @staticmethod
    async def _years_keyboard(year: int) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        bottom_menu = []
        if year + 7 >= MAX_YEAR:
            for i in range(MAX_YEAR - 14, MAX_YEAR + 1):
                builder.button(text=f"{i}", callback_data=SelectYear(year=i))
            bottom_menu.append(
                InlineKeyboardButton(
                    text="◀️", callback_data=ChangeYear(year=year - 7).pack()
                )
            )
        elif year - 7 <= MIN_YEAR:
            for i in range(MIN_YEAR, MIN_YEAR + 15):
                builder.button(text=f"{i}", callback_data=SelectYear(year=i))
            bottom_menu.append(
                InlineKeyboardButton(
                    text="▶️", callback_data=ChangeYear(year=year + 7).pack()
                )
            )
        else:
            for i in range(year - 7, year + 8):
                builder.button(text=f"{i}", callback_data=SelectYear(year=i))
            bottom_menu.extend(
                (
                    InlineKeyboardButton(
                        text="◀️", callback_data=ChangeYear(year=year - 7).pack()
                    ),
                    InlineKeyboardButton(
                        text="▶️", callback_data=ChangeYear(year=year + 7).pack()
                    ),
                )
            )
        builder.adjust(3)
        builder.row(*bottom_menu)
        return builder.as_markup()

    @staticmethod
    async def _months_keyboard(year: int, locale: str) -> InlineKeyboardMarkup:
        local = Locale.parse(locale)

        builder = InlineKeyboardBuilder()
        builder.button(text=f"{year}", callback_data=ChangeYear(year=year))
        for ind, month in local.months["stand-alone"]["wide"].items():
            builder.button(
                text=month.title(),
                callback_data=SelectMonth(month=ind, year=year),
            )
        builder.adjust(1, 3)

        bottom_menu = []
        if year == MAX_YEAR:
            bottom_menu.extend(
                (
                    InlineKeyboardButton(
                        text="◀️", callback_data=SelectYear(year=year - 1).pack()
                    ),
                    InlineKeyboardButton(
                        text="↩️", callback_data=ChangeYear(year=year).pack()
                    ),
                )
            )
        elif year == MIN_YEAR:
            bottom_menu.extend(
                (
                    InlineKeyboardButton(
                        text="↩️", callback_data=ChangeYear(year=year).pack()
                    ),
                    InlineKeyboardButton(
                        text="▶️", callback_data=SelectYear(year=year + 1).pack()
                    ),
                )
            )
        else:
            bottom_menu.extend(
                (
                    InlineKeyboardButton(
                        text="◀️", callback_data=SelectYear(year=year - 1).pack()
                    ),
                    InlineKeyboardButton(
                        text="↩️", callback_data=ChangeYear(year=year).pack()
                    ),
                    InlineKeyboardButton(
                        text="▶️", callback_data=SelectYear(year=year + 1).pack()
                    ),
                )
            )
        builder.row(*bottom_menu)
        return builder.as_markup()

    @staticmethod
    async def _month_keyboard(
            year: int, month: int, locale: str
    ) -> InlineKeyboardMarkup:
        c = calendar.TextCalendar(calendar.MONDAY)
        local = Locale.parse(locale)

        builder = InlineKeyboardBuilder()
        builder.button(
            text=f"{local.months['stand-alone']['wide'][month].title()} {year}",
            callback_data=ChangeMonth(year=year),
        )

        for _, weekday in sorted(local.days["stand-alone"]["abbreviated"].items()):
            builder.button(text=weekday.title(), callback_data=" ")

        for i in c.itermonthdays(year, month):
            if i == 0:
                builder.button(text=" ", callback_data=" ")
            else:
                builder.button(
                    text=f"{i}", callback_data=SelectDate(day=i, month=month, year=year)
                )

        builder.adjust(1, 7)

        bottom_menu = []
        if year == MIN_YEAR and month - 1 == 0:
            bottom_menu.extend(
                (
                    InlineKeyboardButton(
                        text="↩️", callback_data=ChangeMonth(year=year).pack()
                    ),
                    InlineKeyboardButton(
                        text="▶️",
                        callback_data=SelectMonth(month=month + 1, year=year).pack(),
                    ),
                )
            )
        elif year == MAX_YEAR and month + 1 == 13:
            bottom_menu.extend(
                (
                    InlineKeyboardButton(
                        text="◀️",
                        callback_data=SelectMonth(month=month - 1, year=year).pack(),
                    ),
                    InlineKeyboardButton(
                        text="↩️", callback_data=ChangeMonth(year=year).pack()
                    ),
                )
            )
        else:
            next_data = (
                SelectMonth(month=1, year=year + 1)
                if month + 1 == 13
                else SelectMonth(month=month + 1, year=year)
            )
            prev_data = (
                SelectMonth(month=12, year=year - 1)
                if month - 1 == 0
                else SelectMonth(month=month - 1, year=year)
            )
            bottom_menu.extend(
                (
                    InlineKeyboardButton(text="◀️", callback_data=prev_data.pack()),
                    InlineKeyboardButton(
                        text="↩️", callback_data=ChangeMonth(year=year).pack()
                    ),
                    InlineKeyboardButton(text="▶️", callback_data=next_data.pack()),
                )
            )
        builder.row(*bottom_menu)
        builder.row(InlineKeyboardButton(text="Reset", callback_data="reset_calendar"))

        return builder.as_markup()

    @staticmethod
    async def generate_keyboard(locale: str):
        today = date.today()
        return await Calendar._month_keyboard(today.year, today.month, locale)

    @staticmethod
    async def change_month(
            callback: CallbackQuery, callback_data: ChangeMonth, locale: str
    ):
        await callback.message.edit_reply_markup(
            reply_markup=await Calendar._months_keyboard(callback_data.year, locale)
        )

    @staticmethod
    async def select_month(
            callback: CallbackQuery, callback_data: SelectMonth, locale: str
    ):
        await callback.message.edit_reply_markup(
            reply_markup=await Calendar._month_keyboard(
                callback_data.year, callback_data.month, locale
            )
        )

    @staticmethod
    async def change_year(callback: CallbackQuery, callback_data: ChangeYear):
        await callback.message.edit_reply_markup(
            reply_markup=await Calendar._years_keyboard(callback_data.year)
        )

    @staticmethod
    async def select_year(
            callback: CallbackQuery, callback_data: SelectYear, i18n: TranslatorRunner
    ):
        await callback.message.edit_reply_markup(
            reply_markup=await Calendar._months_keyboard(
                callback_data.year, list(i18n.translators)[0].locale
            )
        )

    @staticmethod
    async def reset(callback: CallbackQuery, locale: str):
        await callback.message.edit_reply_markup(
            reply_markup=await Calendar.generate_keyboard(locale)
        )
