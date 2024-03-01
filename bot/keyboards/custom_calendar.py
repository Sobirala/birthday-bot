from datetime import date, timedelta
from typing import Any, Dict

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Calendar, CalendarScope
from aiogram_dialog.widgets.kbd.calendar_kbd import (
    CalendarConfig,
    CalendarDaysView,
    CalendarMonthView,
    CalendarScopeView,
    CalendarYearsView,
)
from aiogram_dialog.widgets.text import Format, Text
from babel.dates import get_day_names, get_month_names

from bot.enums import Language


class WeekDay(Text):
    async def _render_text(self, data: Dict[str, Any], manager: DialogManager) -> str:
        selected_date: date = data["date"]
        locale = data.get("locale", Language.UK)
        return get_day_names(
            width="short", context='stand-alone', locale=locale,
        )[selected_date.weekday()].title()


class Month(Text):
    async def _render_text(self, data: Dict[str, Any], manager: DialogManager) -> str:
        selected_date: date = data["date"]
        locale = data.get("locale", Language.UK)
        return get_month_names(
            'wide', context='stand-alone', locale=locale,
        )[selected_date.month].title()


class CustomCalendar(Calendar):
    def _init_views(self) -> Dict[CalendarScope, CalendarScopeView]:
        return {
            CalendarScope.DAYS: CalendarDaysView(
                self._item_callback_data, self.config,
                header_text=Month(),
                weekday_text=WeekDay(),
                next_month_text=Month() + " >>",
                prev_month_text="<< " + Month(),
            ),
            CalendarScope.MONTHS: CalendarMonthView(
                self._item_callback_data, self.config,
                month_text=Month(),
                header_text=Format("{date:%Y}"),
                this_month_text="[" + Month() + "]",
            ),
            CalendarScope.YEARS: CalendarYearsView(
                self._item_callback_data, self.config,
            ),
        }

    @property
    def config(self) -> CalendarConfig:
        return CalendarConfig(
            min_date=date.today() - timedelta(days=47450),
            max_date=date.today()
        )

    @config.setter
    def config(self, value: CalendarConfig) -> None:
        ...
