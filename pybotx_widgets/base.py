from typing import Any, Optional, Union
from uuid import UUID, uuid4

from botx import (
    Bot,
    Message,
    MessageMarkup,
    SendingCredentials,
    SendingMessage,
    UpdatePayload,
)


class WidgetMarkup:
    markup: MessageMarkup
    additional_markup: Optional[MessageMarkup]

    def add_additional_markup(self) -> None:
        if self.additional_markup:
            self.markup = self.merge_markup(self.markup, self.additional_markup)

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
        self.markup = MessageMarkup()

    async def display(self) -> Optional[Any]:
        raise NotImplementedError

    async def send_or_update_message(
        self, widget_msg: SendingMessage, new_message_id: Union[str, UUID] = None
    ) -> None:
        """Send new message or update exist."""

        current_message_id = self.message.data.get("message_id")
        new_message_id = new_message_id or uuid4()

        for bubbles in widget_msg.markup.bubbles:
            for bubble in bubbles:
                bubble.data["message_id"] = current_message_id or new_message_id

        if current_message_id:
            payload = UpdatePayload(text=widget_msg.text, file=widget_msg.file)
            payload.set_markup(markup=widget_msg.markup)
            await self.bot.update_message(
                SendingCredentials(
                    sync_id=current_message_id,
                    bot_id=self.message.bot_id,
                    host=self.message.host,
                ),
                update=payload,
            )
        else:
            widget_msg.credentials.message_id = new_message_id
            await self.bot.send(widget_msg)
