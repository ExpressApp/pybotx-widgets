"""Calendar widget."""
import re
from calendar import Calendar
from collections.abc import Callable
from datetime import date
from typing import Any, Dict, List, Tuple

from botx import Bot, BubbleElement, Message
from dateutil import parser
from dateutil.relativedelta import relativedelta

from pybotx_widgets.base import Widget, WidgetMarkup
from pybotx_widgets.resources import strings
from pybotx_widgets.service import send_or_update_message

MONTH_TO_DISPLAY_KEY = "calendar_month_to_display"
SELECTED_DATE_KEY = "calendar_selected_date"


class MarkupMixin(WidgetMarkup):
    message: Message
    command: str

    start_date: date
    end_date: date
    current_date: date
    include_past: bool

    LEFT_ARROW: str
    RIGHT_ARROW: str

    MONTHS: Dict[int, str]
    WEEKDAYS: Tuple[str]

    get_prev_and_next_year: Callable
    get_prev_and_next_month: Callable

    def add_year_bubbles(self) -> None:
        """Add year bubbles ([<] [year] [>])."""

        prev_year, next_year = self.get_prev_and_next_year()

        if not self.include_past and self.start_date.year == self.current_date.year:
            self.widget_msg.markup.add_bubble(
                command=self.command,
                label=" ",
            )
        else:
            self.widget_msg.markup.add_bubble(
                command=f"{self.command} {self.LEFT_ARROW}",
                label=self.LEFT_ARROW,
                data={MONTH_TO_DISPLAY_KEY: prev_year},
            )

        self.widget_msg.markup.add_bubble(
            command="",
            label=str(self.current_date.year),
            new_row=False,
        )

        if self.current_date.year == self.end_date.year:
            self.widget_msg.markup.add_bubble(
                command=self.command,
                label=" ",
            )
        else:
            self.widget_msg.markup.add_bubble(
                command=f"{self.command} {self.RIGHT_ARROW}",
                label=self.RIGHT_ARROW,
                data={MONTH_TO_DISPLAY_KEY: next_year},
                new_row=False,
            )

    def add_month_bubbles(self) -> None:
        """Add month bubbles ([<] [month_name] [>])."""
        prev_month, next_month = self.get_prev_and_next_month()

        is_lower_limit = all(
            (
                self.start_date.month >= self.current_date.month,
                self.start_date.year >= self.current_date.year,
            )
        )
        is_upper_limit = all(
            (
                self.end_date.month == self.current_date.month,
                self.end_date.year == self.current_date.year,
            )
        )

        if not self.include_past and is_lower_limit:
            self.widget_msg.markup.add_bubble(
                command=self.command,
                label=" ",
            )
        else:
            self.widget_msg.markup.add_bubble(
                command=f"{self.command} {self.LEFT_ARROW}",
                label=self.LEFT_ARROW,
                data={MONTH_TO_DISPLAY_KEY: prev_month},
            )
        self.widget_msg.markup.add_bubble(
            command="",
            label=self.MONTHS[self.current_date.month],
            new_row=False,
        )

        if is_upper_limit:
            self.widget_msg.markup.add_bubble(
                command=self.command,
                label=" ",
            )
        else:
            self.widget_msg.markup.add_bubble(
                command=f"{self.command} {self.RIGHT_ARROW}",
                label=self.RIGHT_ARROW,
                data={MONTH_TO_DISPLAY_KEY: next_month},
                new_row=False,
            )

    def add_week_bubbles(self) -> None:
        """Add week bubbles ([Пн][Вт][Ср][Чт][Пт][Сб][Вс])."""

        self.widget_msg.markup.bubbles.append(
            [BubbleElement(label=weekday, command="") for weekday in self.WEEKDAYS]
        )

    def add_day_bubbles(self) -> None:
        """Add day bubbles.

        [1][2][3][4][5][6][7]
        ...
        [25][26][27][28][29][30]
        """

        weeks = Calendar().monthdatescalendar(
            year=self.current_date.year, month=self.current_date.month
        )
        for calendar_row, week in enumerate(weeks, 1):
            calendar_dates_row: List[BubbleElement] = []
            append_row = False

            for calendar_date in week:

                # show_day will be False, if any condition is True
                show_day = not any(
                    (
                        not self.include_past and calendar_date < self.start_date,
                        calendar_date > self.end_date,
                        calendar_row == len(weeks) and calendar_date.day < 7,
                        calendar_row == 1 and calendar_date.day > 7,
                    )
                )

                if show_day:
                    label = str(calendar_date.day)
                    bubble_data = {SELECTED_DATE_KEY: calendar_date}
                    bubble_command = f"{self.command} {calendar_date}"

                    append_row = True
                else:
                    label = ""
                    bubble_data = {}
                    bubble_command = ""

                calendar_dates_row.append(
                    BubbleElement(
                        command=bubble_command,
                        label=label,
                        data=bubble_data,
                    )
                )

            if append_row:
                self.widget_msg.markup.bubbles.append(calendar_dates_row)


class CalendarWidget(Widget, MarkupMixin):
    LEFT_ARROW = strings.LEFT_ARROW
    RIGHT_ARROW = strings.RIGHT_ARROW
    AFTER_SELECT_TEXT = strings.CAL_DATE_SELECTED
    SELECT_DATE = strings.SELECT_DATE
    WEEKDAYS = strings.WEEKDAYS  # type: ignore
    MONTHS = strings.MONTHS

    def __init__(
        self,
        start_date: date = None,
        end_date: date = date.max,
        include_past: bool = False,
        *args: Any,
        **kwargs: Any,
    ):
        """
        :param start_date - Calendar start date, previews dates hides
        :param end_date - Calendar end date, next dates hides
        :param include_past - Include past dates from start_date
        """
        super().__init__(*args, **kwargs)

        self.start_date = start_date or date.today()
        self.end_date = end_date
        self.include_past = include_past

        self.month_to_display = self.message.data.get(MONTH_TO_DISPLAY_KEY)
        self.selected_date = self.message.data.get(SELECTED_DATE_KEY)
        self.widget_msg.text = self.SELECT_DATE
        self.current_date = self.get_current_date()

    def get_current_date(self) -> date:
        arg = self.message.command.single_argument
        arrows_regexp = f"{self.LEFT_ARROW}|{self.RIGHT_ARROW}"

        if re.findall(arrows_regexp, arg) and self.month_to_display:
            return parser.parse(self.month_to_display).date()
        else:
            return date.today()

    @classmethod
    async def get_value(cls, message: Message, bot: Bot) -> date:
        selected_date = message.data[SELECTED_DATE_KEY]
        try:
            selected_date = parser.parse(selected_date).date()
        except parser.ParserError:  # type: ignore
            raise RuntimeError("Date is not selected.")

        _clear_calendar_data(message)
        # Remove buttons
        await send_or_update_message(message, bot, cls.AFTER_SELECT_TEXT)

        return selected_date

    def get_prev_and_next_year(self) -> Tuple[date, date]:
        month = 1 if self.include_past else date.today().month
        prev_year = (self.current_date - relativedelta(years=1)).replace(
            month=month, day=1
        )
        next_year = (  # noqa: WPS221
            self.current_date + relativedelta(years=1)
        ).replace(month=1, day=1)
        return prev_year, next_year

    def get_prev_and_next_month(self) -> Tuple[date, date]:
        prev_month = self.current_date - relativedelta(months=1)
        next_month = self.current_date + relativedelta(months=1)
        return prev_month, next_month

    def add_markup(self) -> None:
        self.add_year_bubbles()
        self.add_month_bubbles()
        self.add_week_bubbles()
        self.add_day_bubbles()

        self.add_additional_markup()


def _clear_calendar_data(message: Message) -> None:
    """Clear widget data form message.data."""

    message.command.data.pop(MONTH_TO_DISPLAY_KEY, None)
    message.command.data.pop(SELECTED_DATE_KEY, None)
