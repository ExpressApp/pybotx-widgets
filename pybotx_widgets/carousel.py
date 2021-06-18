"""Carousel widget."""

import string
from collections import namedtuple
from itertools import cycle, islice
from typing import Iterator, Optional, Sequence, Tuple

from botx import Bot, BubbleElement, Message, MessageMarkup

from pybotx_widgets.resources import strings
from pybotx_widgets.service import merge_markup, send_or_update_message

PaginationInfo = namedtuple(
    "PaginationInfo", ("start", "end", "page_len", "content_len")
)

LEFT_PRESSED = "CAROUSEL_LEFT_BUTTON_PRESSED"
RIGHT_PRESSED = "CAROUSEL_RIGHT_BUTTON_PRESSED"


async def carousel(  # noqa: WPS211
    message: Message,
    bot: Bot,
    widget_content: Sequence,
    label: str,
    command: str,
    start_from: int = 0,
    displayed_content_count: int = 3,
    selected_value_label: str = strings.SELECTED_VALUE_LABEL,
    control_labels: Tuple[str, str] = None,
    inline: bool = True,
    loop: bool = True,
    show_numbers: bool = False,
    additional_markup: MessageMarkup = None,
) -> Optional[str]:
    """Show carousel or return selected value.

    :param message - botx Message
    :param bot - botx Bot
    :param widget_content - All content to be displayed
    :param label - Text of message
    :param command - Used for bubbles 'command' attribute
    :param start_from - Start display content from
    :param displayed_content_count - Count of content to be displayed
    :param selected_value_label - Display format of the selected value,
    default = "{label} {selected_val}"
    :param control_labels - Override default control labels.
    :param inline - Inline mode
    :param loop - Loop content or not
    :param show_numbers - Show content order numbers
    for prev/next control bubbles' labels.
    :param additional_markup - Additional markup for attaching to widget
    """

    if "{selected_val}" not in selected_value_label:
        raise ValueError("'selected_value_label' should contains '{selected_val}'")

    if start_from > len(widget_content):
        raise ValueError("'start_from' is greater than 'widget_content'")

    if loop and show_numbers:
        raise ValueError("Sorry, you can't enable both 'loop' and 'show_numbers'")

    if inline and show_numbers:
        raise ValueError("Sorry, you can't enable both 'inline' and 'show_numbers'")

    if not control_labels:
        control_labels = (
            (f"{strings.LEFT_ARROW} ({{}}-{{}})", f"{strings.RIGHT_ARROW} ({{}}-{{}})")
            if show_numbers
            else (strings.LEFT_ARROW, strings.RIGHT_ARROW)
        )

    if show_numbers:
        if not _is_valid_label_for_placing_numbers(control_labels[0]):
            raise ValueError("Left control label should have exactly two '{}'")

        if not _is_valid_label_for_placing_numbers(control_labels[1]):
            raise ValueError("Right control label should have exactly two '{}'")

    # Try to get position from message.data
    start_from = message.data.get("carousel_start_from", start_from)

    selected_val = message.data.pop("carousel_selected_val", "")

    # if user click on left arrow
    if selected_val == LEFT_PRESSED:
        start_from -= displayed_content_count

    # if user click on right arrow
    elif selected_val == RIGHT_PRESSED:
        start_from += displayed_content_count

    # if user select value
    elif selected_val:
        await send_or_update_message(
            message,
            bot,
            selected_value_label.format(label=label, selected_val=selected_val),
        )
        _clear_carousel_data(message)

        return selected_val

    # Set current position in message.data
    message.data["carousel_start_from"] = start_from

    # Set selected_value_label and carousel_message_label for get_carousel_result
    message.data["carousel_selected_value_label"] = selected_value_label
    message.data["carousel_message_label"] = label

    # Count new start position
    content_len = len(widget_content)
    if start_from < 0 or start_from > content_len:
        start_from = abs(content_len - abs(start_from))

    # Count end position
    end = start_from + displayed_content_count

    if len(widget_content) <= displayed_content_count:
        # if all content displayed, then hide arrows
        show_right_arrow = False
        show_left_arrow = False
    elif loop:
        # Loop content and always show arrows
        widget_content = cycle(widget_content)  # type: ignore
        show_right_arrow = True
        show_left_arrow = True
    else:
        show_right_arrow = end < content_len
        show_left_arrow = start_from > 0

    displayed_content = islice(widget_content, start_from, end)

    if inline:
        markup = _get_inline_markup(
            message,
            command,
            displayed_content,
            show_left_arrow,
            show_right_arrow,
            control_labels,
            additional_markup,
        )
    else:
        markup = _get_newline_markup(
            message,
            command,
            displayed_content,
            show_left_arrow,
            show_right_arrow,
            show_numbers,
            PaginationInfo(start_from, end, displayed_content_count, content_len),
            control_labels,
            additional_markup,
        )

    await send_or_update_message(message, bot, label, markup=markup)

    return None


async def get_carousel_result(message: Message, bot: Bot) -> Optional[str]:
    selected_val = message.data.get("carousel_selected_val", "")
    selected_value_label = message.data.get("carousel_selected_value_label")
    message_label = message.data.get("carousel_message_label")

    # if user select value
    if selected_val and selected_val not in {LEFT_PRESSED, RIGHT_PRESSED}:
        await send_or_update_message(
            message,
            bot,
            selected_value_label.format(label=message_label, selected_val=selected_val),
        )
        _clear_carousel_data(message)

        return selected_val

    return None


def _clear_carousel_data(message: Message) -> None:
    """Clear widget data form message.data."""

    message.data.pop("message_id", None)
    message.data.pop("carousel_selected_val", None)
    message.data.pop("carousel_selected_value_label", None)
    message.data.pop("carousel_message_label", None)
    message.data.pop("carousel_start_from", None)


def _is_valid_label_for_placing_numbers(label: str) -> bool:
    number_places = list(string.Formatter().parse(label))

    if len([place for place in number_places if place[1] == ""]) != 2:
        return False

    return True


def _get_inline_markup(
    message: Message,
    command: str,
    displayed_content: Iterator,
    show_left_arrow: bool,
    show_right_arrow: bool,
    control_labels: Tuple[str, str],
    additional_markup: MessageMarkup = None,
) -> MessageMarkup:
    """Build inline markup for Carousel widget."""

    markup = MessageMarkup()

    if show_left_arrow:
        markup.add_bubble(
            command=message.command.command,
            label=control_labels[0],
            data={**message.data, "carousel_selected_val": LEFT_PRESSED},
            new_row=False,
        )

    for content_item in displayed_content:
        markup.add_bubble(
            command=command,
            label=content_item,
            data={**message.data, "carousel_selected_val": content_item},
            new_row=False,
        )

    if show_right_arrow:
        markup.add_bubble(
            command=message.command.command,
            label=control_labels[1],
            data={**message.data, "carousel_selected_val": RIGHT_PRESSED},
            new_row=False,
        )

    if additional_markup:
        markup = merge_markup(markup, additional_markup)

    return markup


def _get_newline_markup(
    message: Message,
    command: str,
    displayed_content: Iterator,
    show_left_arrow: bool,
    show_right_arrow: bool,
    show_numbers: bool,
    pagination: PaginationInfo,
    control_labels: Tuple[str, str],
    additional_markup: MessageMarkup = None,
) -> MessageMarkup:
    """Build newline markup for Carousel widget."""

    markup = MessageMarkup()
    right_label = control_labels[1]

    if show_numbers:
        right_bound = pagination.end + pagination.page_len
        if pagination.content_len < right_bound:
            right_bound = pagination.content_len

        right_label = right_label.format(pagination.end + 1, right_bound)

    right_arrow_bubble = {
        "command": message.command.command,
        "label": right_label,
        "data": {**message.data, "carousel_selected_val": RIGHT_PRESSED},
    }

    for content_item in displayed_content:
        if isinstance(content_item, (list, tuple, set)):
            markup.bubbles.append(
                [
                    BubbleElement(
                        command=command,
                        label=row_item,
                        data={**message.data, "carousel_selected_val": row_item},
                    )
                    for row_item in content_item
                ]
            )
            continue

        markup.bubbles.append(
            [
                BubbleElement(
                    command=command,
                    label=content_item,
                    data={**message.data, "carousel_selected_val": content_item},
                )
            ]
        )

    if show_left_arrow:
        left_label = control_labels[0]

        if show_numbers:
            left_bound = pagination.start - pagination.page_len + 1
            left_label = left_label.format(left_bound, pagination.start)

        markup.add_bubble(
            command=message.command.command,
            label=left_label,
            data={**message.data, "carousel_selected_val": LEFT_PRESSED},
        )
        # if left arrow displayed, then show right arrow inline
        right_arrow_bubble["new_row"] = False

    if show_right_arrow:
        markup.add_bubble(**right_arrow_bubble)

    if additional_markup:
        markup = merge_markup(markup, additional_markup)

    return markup
