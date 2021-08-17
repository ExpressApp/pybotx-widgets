from typing import Optional, Union
from uuid import UUID, uuid4

from botx import (
    Bot,
    Message,
    MessageMarkup,
    SendingMessage,
)


class WidgetMarkup:
    widget_msg: SendingMessage
    additional_markup: Optional[MessageMarkup]

    def add_additional_markup(self) -> None:
        if self.additional_markup:
            self.widget_msg.markup = self.merge_markup(self.widget_msg.markup, self.additional_markup)

    @classmethod
    def merge_markup(
        cls, primary: MessageMarkup, additional: MessageMarkup
    ) -> MessageMarkup:
        return MessageMarkup(
            bubbles=(primary.bubbles + additional.bubbles),
            keyboard=(primary.keyboard + additional.keyboard),
        )


class Widget:
    def __init__(
        self,
        message: Message,
        bot: Bot,
        command: str,
        additional_markup: MessageMarkup = None,
    ):
        """
        :param message - botx Message
        :param bot - botx Bot
        :param command - Used for bubbles 'command' attribute
        :param additional_markup -  Additional markup for attaching to widget
        """
        self.message = message
        self.bot = bot
        self.command = command
        self.additional_markup = additional_markup

        self.widget_msg = SendingMessage.from_message(message=message)

    def add_markup(self) -> None:
        """Add widget markup."""
        raise NotImplementedError

    async def send_widget_message(self) -> None:
        await self.send_or_update_message(self.widget_msg)

    async def display(self) -> None:
        self.add_markup()
        await self.send_widget_message()

    async def send_or_update_message(
        self, widget_msg: SendingMessage, new_message_id: Union[str, UUID] = None
    ) -> None:
        """Send new message or update exist."""

        message_id = self.message.data.get("message_id")
        is_message_id_exists = bool(message_id)

        message_id = new_message_id or message_id or uuid4()

        widget_msg.credentials.message_id = message_id

        widget_msg.metadata = {**self.message.data, "message_id": message_id}
        await self.bot.send(
            widget_msg, update=is_message_id_exists
        )
