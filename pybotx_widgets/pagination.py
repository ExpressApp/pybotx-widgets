"""Pagination widget."""
import asyncio
from typing import Any, List
from uuid import UUID

from botx import SendingMessage

from pybotx_widgets.base import Widget, WidgetMarkup
from pybotx_widgets.resources import strings

START_FROM_KEY = "pagination_start_from"
MESSAGE_IDS_KEY = "pagination_message_ids"


class MarkupMixin(WidgetMarkup):
    BACKWARD_BTN_TEMPLATE: strings.FormatTemplate = (
        strings.PAGINATION_BACKWARD_BTN_TEMPLATE
    )
    FORWARD_BTN_TEMPLATE: strings.FormatTemplate = (
        strings.PAGINATION_FORWARD_BTN_TEMPLATE
    )

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
            data={START_FROM_KEY: left_border},
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
            data={START_FROM_KEY: left_border},
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
        self.message_ids = self.message.metadata.get(MESSAGE_IDS_KEY, [])

    @property
    def display_content(self) -> List[SendingMessage]:
        """Paginated content to be displayed."""

        return self.widget_content[self.start_from : self.start_from + self.paginate_by]

    def add_markup(self) -> None:
        """Get markup with Backward/Forward buttons to control widget."""

        if self.content_len > self.paginate_by:
            self.add_backward_btn()
            self.add_forward_btn()

    async def send_widget_message(self) -> None:
        """Send or update multiple paginated messages."""

        if self.message_ids:
            await self._update_widget_messages()
        else:
            await self._send_new_widget_messages()

    async def _send_new_widget_messages(self) -> None:
        """Send multiple paginated messages."""

        display_content = self.display_content
        if not display_content:
            return

        for widget_message in display_content[:-1]:
            message_id = await self.bot.send(widget_message)
            self.message_ids.append(message_id)
            await asyncio.sleep(self.delay_between_messages)

        last_widget_message = display_content[-1]
        self._prepare_last_message(last_widget_message)
        await self.bot.send(last_widget_message)

    async def _update_widget_messages(self) -> None:
        """Update multiple paginated messages."""

        display_content = self.display_content
        for index in range(self.paginate_by - 1):
            try:
                widget_message = display_content[index]
            except IndexError:
                widget_message = self.empty_msg

            widget_message.credentials.message_id = self.message_ids[index]
            await self.bot.send(widget_message, update=True)
            await asyncio.sleep(self.delay_between_messages)

        try:
            last_widget_message = display_content[index + 1]  # noqa: WPS441
        except IndexError:
            last_widget_message = self.empty_msg

        self._prepare_last_message(last_widget_message)
        last_widget_message.credentials.message_id = self.message.source_sync_id
        await self.bot.send(last_widget_message, update=True)

    def _prepare_last_message(self, message: SendingMessage) -> None:
        self.add_additional_markup()
        message.markup = self.merge_markup(message.markup, self.widget_msg.markup)
        message.metadata = {**message.metadata, MESSAGE_IDS_KEY: self.message_ids}
