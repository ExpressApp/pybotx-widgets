"""Pagination widget."""
from dataclasses import dataclass, field
from itertools import zip_longest
from typing import Iterator, List, Tuple
from uuid import UUID, uuid4

from botx import Bot, File, Message, MessageMarkup

from pybotx_widgets.resources import strings
from pybotx_widgets.service import merge_markup, send_or_update_message


@dataclass
class MessageContent:
    text: str = ""
    markup: MessageMarkup = field(default_factory=MessageMarkup)
    file: File = None  # noqa: WPS110


PaginatedContent = Iterator[Tuple[UUID, MessageContent]]


async def pagination(
    message: Message,
    bot: Bot,
    widget_content: List[MessageContent],
    paginate_by: int,
    command: str,
) -> None:
    """Paginate content."""

    if len(widget_content) <= paginate_by:
        for widget_message in widget_content:
            await bot.answer_message(
                widget_message.text, message, markup=widget_message.markup, file=widget_message.file
            )
        return

    start_from = message.data.get("pagination_start_from", 0)
    message_ids = message.data.get("pagination_message_ids")
    if not message_ids:
        message_ids = [uuid4() for _ in range(paginate_by)]

    control_markup = get_control_markup(
        command, start_from, len(widget_content), paginate_by, message_ids
    )
    display_content = widget_content[start_from : start_from + paginate_by]
    display_content: PaginatedContent = zip_longest(
        message_ids, display_content
    )

    for message_id, widget_message in display_content:
        if "message_id" in message.data:
            message.command.data["message_id"] = message_id

        widget_message = widget_message or MessageContent(text=strings.EMPTY_MSG_SYMBOL)

        if message_id == message_ids[-1]:
            widget_message.markup = merge_markup(widget_message.markup, control_markup)

        await send_or_update_message(
            message,
            bot,
            widget_message.text,
            widget_message.markup,
            widget_message.file,
            message_id,
        )


def get_control_markup(
    command: str,
    start_from: int,
    messages_content_len: int,
    paginate_by: int,
    message_ids: List[UUID],
) -> MessageMarkup:
    """Get markup with Backward/Forward buttons to control widget."""

    control_markup = MessageMarkup()
    if start_from >= paginate_by:
        left_border = start_from - paginate_by
        label = strings.PAGINATION_BACKWARD_BTN_TEMPLATE.format(
            left_num=left_border + 1, right_num=start_from
        )

        control_markup.add_bubble(
            label=label,
            command=command,
            data={
                "pagination_start_from": left_border,
                "pagination_message_ids": message_ids,
            },
        )

    if (start_from + paginate_by) < messages_content_len:
        left_border = start_from + paginate_by
        right_border = min(left_border + paginate_by, messages_content_len)

        label = strings.PAGINATION_FORWARD_BTN_TEMPLATE.format(
            left_num=left_border + 1, right_num=right_border
        )

        control_markup.add_bubble(
            label=label,
            command=command,
            new_row=False,
            data={
                "pagination_start_from": left_border,
                "pagination_message_ids": message_ids,
            },
        )

    return control_markup
