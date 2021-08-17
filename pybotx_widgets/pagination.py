"""Pagination widget."""
import asyncio
from itertools import zip_longest
from typing import Iterator, List, Optional, Tuple, Any
from uuid import UUID, uuid4

from botx import SendingMessage

from pybotx_widgets.base import Widget, WidgetMarkup
from pybotx_widgets.resources import strings
from pybotx_widgets.resources.strings import FormatTemplate

START_FROM_KEY = "pagination_start_from"
MESSAGE_IDS_KEY = "pagination_message_ids"


PaginatedContent = Iterator[Tuple[UUID, Optional[SendingMessage]]]


class MarkupMixin(WidgetMarkup):
    BACKWARD_BTN_TEMPLATE: FormatTemplate = strings.PAGINATION_BACKWARD_BTN_TEMPLATE
    FORWARD_BTN_TEMPLATE: FormatTemplate = strings.PAGINATION_FORWARD_BTN_TEMPLATE

    paginate_by: int
    start_from: int
    content_len: int
    message_ids: List[UUID]

    command: str

    def add_backward_btn(self) -> None:
        """Add Backward buttons to scroll widget to the left."""

        if self.start_from < self.paginate_by:
            return

        left_border = self.start_from - self.paginate_by
        label = self.BACKWARD_BTN_TEMPLATE.format(
            left_num=left_border + 1, right_num=self.start_from
        )

        self.widget_msg.markup.add_bubble(
            label=label,
            command=self.command,
            data={
                START_FROM_KEY: left_border,
                MESSAGE_IDS_KEY: self.message_ids,
            },
        )

    def add_forward_btn(self) -> None:
        """Add Forward buttons to scroll widget to the right."""

        left_border = self.start_from + self.paginate_by

        if left_border >= self.content_len:
            return

        right_border = min(left_border + self.paginate_by, self.content_len)

        label = self.FORWARD_BTN_TEMPLATE.format(
            left_num=left_border + 1, right_num=right_border
        )

        self.widget_msg.markup.add_bubble(
            label=label,
            command=self.command,
            new_row=False,
            data={
                START_FROM_KEY: left_border,
                MESSAGE_IDS_KEY: self.message_ids,
            },
        )


class PaginationWidget(Widget, MarkupMixin):
    def __init__(
        self,
        widget_content: List[SendingMessage],
        paginate_by: int,
        delay_between_messages: float = 0.5,
        *args: Any,
        **kwargs: Any
    ):
        """
        :param widget_content - All content to be displayed
        :param paginate_by - Count of content to be displayed
        :param delay_between_messages - Delay between multiple messages
        """
        super().__init__(*args, **kwargs)

        self.widget_content = widget_content
        self.paginate_by = paginate_by
        self.delay_between_messages = delay_between_messages

        self.content_len = len(widget_content)
        self.empty_msg = SendingMessage.from_message(
            text=strings.EMPTY_MSG_SYMBOL, message=self.message
        )
        self.start_from = self.message.data.get(START_FROM_KEY, 0)
        self.message_ids = self.message.data.get(MESSAGE_IDS_KEY)

        min_len = min(paginate_by, self.content_len)
        self.message_ids = self.message_ids or [uuid4() for _ in range(min_len)]

    @property
    def display_content(self) -> PaginatedContent:
        """Paginated content to be displayed."""

        if self.content_len < self.paginate_by:
            return zip_longest(self.message_ids, self.widget_content)

        display_content = self.widget_content[
            self.start_from : self.start_from + self.paginate_by
        ]
        return zip_longest(self.message_ids, display_content)

    def add_markup(self) -> None:
        """Get markup with Backward/Forward buttons to control widget."""

        if self.content_len > self.paginate_by:
            self.add_backward_btn()
            self.add_forward_btn()

    async def send_widget_message(self) -> None:
        """Send multiple paginated messages."""
        widget_markup = self.widget_msg.markup

        for message_id, widget_message in self.display_content:
            if "message_id" in self.message.data:
                self.message.command.data["message_id"] = message_id

            widget_message = widget_message or self.empty_msg

            if message_id == self.message_ids[-1]:
                widget_message.markup = self.merge_markup(
                    widget_message.markup, widget_markup
                )
                self.add_additional_markup()

            await self.send_or_update_message(widget_message, message_id)
            await asyncio.sleep(self.delay_between_messages)
