"""Calendar widget."""

import re
from calendar import Calendar
from datetime import date
from typing import List, Optional

from botx import Bot, BubbleElement, Message, MessageMarkup
from dateutil import parser
from dateutil.relativedelta import relativedelta

from pybotx_widgets.resources import strings
from pybotx_widgets.service import merge_markup, send_or_update_message


async def calendar(
    message: Message,
    bot: Bot,
    command: str,
    start_date: date = None,
    end_date: date = date.max,
    include_past: bool = False,
    additional_markup: MessageMarkup = None,
) -> Optional[date]:
    """Show calendar for date selection.

    :param message - botx Message
    :param bot - botx Bot
    :param command - Used for bubbles 'command' attribute
    :param start_date - Calendar start date, previews dates hides
    :param end_date - Calendar end date, next dates hides
    :param include_past - Include past dates from start_date
    :param additional_markup - Additional markup for attaching to widget
    """

    arg = message.command.single_argument
    start_date = start_date or date.today()
    current_date = date.today()
    markup = MessageMarkup()

    current_date_str = message.data.get("calendar_current_date")
    selected_date_str = message.data.get("calendar_selected_date")

    arrows_regexp = "|".join([strings.LEFT_ARROW, strings.RIGHT_ARROW])

    if re.findall(arrows_regexp, arg) and current_date_str:
        current_date = parser.parse(current_date_str).date()

    elif selected_date_str:
        selected_date = parser.parse(selected_date_str).date()

        # Remove buttons
        await send_or_update_message(message, bot, strings.CAL_DATE_SELECTED)
        _clear_calendar_data(message)

        return selected_date

    prev_year = (current_date - relativedelta(years=1)).replace(month=1, day=1)
    next_year = (current_date + relativedelta(years=1)).replace(month=1, day=1)

    prev_month = current_date - relativedelta(months=1)
    next_month = current_date + relativedelta(months=1)

    # TODO: refactor add_year_bubbles and add_month_bubbles
    add_year_bubbles(
        message,
        markup,
        command,
        current_date,
        prev_year,
        next_year,
        start_date,
        end_date,
        include_past,
    )
    add_month_bubbles(
        message,
        markup,
        command,
        current_date,
        prev_month,
        next_month,
        start_date,
        end_date,
        include_past,
    )
    add_week_bubbles(markup)

    weeks = Calendar().monthdatescalendar(
        year=current_date.year, month=current_date.month
    )

    add_day_bubbles(message, markup, command, weeks, start_date, end_date, include_past)

    if additional_markup:
        markup = merge_markup(markup, additional_markup)

    await send_or_update_message(message, bot, strings.SELECT_DATE, markup)

    return None


def add_year_bubbles(
    message: Message,
    markup: MessageMarkup,
    command: str,
    current_date: date,
    prev_year: date,
    next_year: date,
    start_date: date,
    end_date: date,
    include_past: bool,
) -> MessageMarkup:
    """Add year bubbles ([<] [year] [>])."""

    if not include_past and start_date.year == current_date.year:
        markup.add_bubble(
            command=command,
            label=" ",
        )
    else:
        markup.add_bubble(
            command=f"{command} {strings.LEFT_ARROW}",
            label=strings.LEFT_ARROW,
            data={**message.data, "calendar_current_date": prev_year},
        )

    markup.add_bubble(
        command="", label=str(current_date.year), data=message.data, new_row=False
    )

    if current_date.year == end_date.year:
        markup.add_bubble(
            command=command,
            label=" ",
        )
    else:
        markup.add_bubble(
            command=f"{command} {strings.RIGHT_ARROW}",
            label=strings.RIGHT_ARROW,
            data={**message.data, "calendar_current_date": next_year},
            new_row=False,
        )
    return markup


def add_month_bubbles(
    message: Message,
    markup: MessageMarkup,
    command: str,
    current_date: date,
    prev_month: date,
    next_month: date,
    start_date: date,
    end_date: date,
    include_past: bool,
) -> MessageMarkup:
    """Add month bubbles ([<] [month_name] [>])."""

    is_lower_limit = (
        start_date.month == current_date.month and start_date.year == current_date.year
    )
    is_upper_limit = (
        end_date.month == current_date.month and end_date.year == current_date.year
    )

    if not include_past and is_lower_limit:
        markup.add_bubble(
            command=command,
            label=" ",
        )
    else:
        markup.add_bubble(
            command=f"{command} {strings.LEFT_ARROW}",
            label=strings.LEFT_ARROW,
            data={**message.data, "calendar_current_date": prev_month},
        )
    markup.add_bubble(
        command="",
        label=strings.MONTHS[current_date.month],
        data=message.data,
        new_row=False,
    )

    if is_upper_limit:
        markup.add_bubble(
            command=command,
            label=" ",
        )
    else:
        markup.add_bubble(
            command=f"{command} {strings.RIGHT_ARROW}",
            label=strings.RIGHT_ARROW,
            data={**message.data, "calendar_current_date": next_month},
            new_row=False,
        )
    return markup


def add_week_bubbles(
    markup: MessageMarkup,
) -> MessageMarkup:
    """Add week bubbles ([Пн][Вт][Ср][Чт][Пт][Сб][Вс])."""

    markup.bubbles.append(
        [BubbleElement(label=weekday, command="") for weekday in strings.WEEKDAYS]
    )

    return markup


def add_day_bubbles(
    message: Message,
    markup: MessageMarkup,
    command: str,
    weeks: List[List[date]],
    start_date: date,
    end_date: date,
    include_past: bool = False,
) -> MessageMarkup:
    """Add day bubbles.

    [1][2][3][4][5][6][7]
    ...
    [25][26][27][28][29][30]
    """

    for calendar_row, week in enumerate(weeks, 1):
        calendar_dates_row: List[BubbleElement] = []
        append_row = False

        for calendar_date in week:
            show_day = True

            if not include_past and calendar_date < start_date:
                show_day = False

            elif calendar_date > end_date:
                show_day = False

            elif calendar_row == len(weeks) and calendar_date.day < 7:
                show_day = False

            elif calendar_row == 1 and calendar_date.day > 7:
                show_day = False

            if show_day:
                label = str(calendar_date.day)
                bubble_data = {**message.data, "calendar_selected_date": calendar_date}
                bubble_command = f"{command} {calendar_date}"

                append_row = True
            else:
                label = ""
                bubble_data = message.data
                bubble_command = ""

            calendar_dates_row.append(
                BubbleElement(
                    command=bubble_command,
                    label=label,
                    new_row=not calendar_date.weekday(),
                    data=bubble_data,
                )
            )

        if append_row:
            markup.bubbles.append(calendar_dates_row)

    return markup


def _clear_calendar_data(message: Message) -> None:
    """Clear widget data form message.data."""

    message.data.pop("calendar_current_date", None)
    message.data.pop("calendar_selected_date", None)
