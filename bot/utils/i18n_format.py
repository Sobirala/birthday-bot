from typing import Any, Dict, Protocol

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.common import WhenCondition
from aiogram_dialog.widgets.text import Text
from aiogram_i18n import I18nContext


class Values(Protocol):
    def __getitem__(self, item: Any) -> Any:
        raise NotImplementedError


def default_format_text(text: str, data: Values) -> str:
    return text.format_map(data)


class I18NFormat(Text):
    def __init__(self, text: str, when: WhenCondition = None, **kwargs: Any):
        super().__init__(when)
        self.text = text
        self.data = kwargs

    async def _render_text(self, data: Dict[str, Any], manager: DialogManager) -> str:
        i18n: I18nContext = manager.middleware_data["i18n"]
        data.update(self.data)
        return i18n.get(self.text, **data)
