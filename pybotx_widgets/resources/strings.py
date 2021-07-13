"""Text and templates for messages and api responses."""
import os
from typing import Any, Protocol, cast

from mako.lookup import TemplateLookup

RESOURCES_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(RESOURCES_DIR, "templates")


class FormatTemplate(Protocol):
    """
    Protocol for correct templates typing.

    Allow use format() instead of render() method that needed to maintain consistency
    with regular string formatting.
    """

    def format(self, **kwargs: Any) -> str:  # noqa: WPS125
        """Render template."""


class TemplateFormatterLookup(TemplateLookup):
    """Represent a collection of templates from the local filesystem."""

    def get_template(self, uri: str) -> FormatTemplate:
        """Cast default mako template to FormatTemplate."""
        template = super().get_template(uri)
        template.format = template.render  # noqa: WPS125
        return cast(FormatTemplate, template)


lookup = TemplateFormatterLookup(directories=[TEMPLATES_DIR], input_encoding="utf-8")

# ====Calendar====
MONTHS = {  # noqa: WPS407
    1: "Янв",
    2: "Фев",
    3: "Мар",
    4: "Апр",
    5: "Май",
    6: "Июн",
    7: "Июл",
    8: "Авг",
    9: "Сен",
    10: "Окт",
    11: "Ноя",
    12: "Дек",
}
WEEKDAYS = (
    "Пн",
    "Вт",
    "Ср",
    "Чт",
    "Пт",
    "Сб",
    "Вс",
)
CAL_DATE_SKIPPED = "Дата пропущена"
SKIP = "Пропустить"
CANCEL = "Отмена"
CAL_DATE_SELECTED = "Дата выбрана"
SELECT_CALENDAR = "Выберите календарь"
SELECT_DATE = "Выберите дату"
# ========

SELECTED_VALUE_LABEL = "{label} {selected_val}"
CHOOSE_LABEL = "Выбрать"
FILL_LABEL = "Ввести"
EMPTY = "[Пусто]"

LEFT_ARROW = "⬅️"
RIGHT_ARROW = "➡️"
UP_ARROW = "⬆️"
DOWN_ARROW = "⬇️"

CHECKBOX_CHECKED = "☑"
CHECKBOX_UNCHECKED = "☐"
CHECK_MARK = "✔️"
ENVELOPE = "✉️"
PENCIL = "✏️"
CROSS_MARK = "❌"


PAGINATION_BACKWARD_BTN_TEMPLATE = lookup.get_template(
    "pagination_backward_btn.txt.mako"
)
PAGINATION_FORWARD_BTN_TEMPLATE = lookup.get_template("pagination_forward_btn.txt.mako")

EMPTY_MSG_SYMBOL = "-"
