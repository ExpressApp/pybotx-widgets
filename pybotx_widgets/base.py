from typing import Any, Optional

from botx import Bot, Message, MessageMarkup


class Widget:
    message: Message
    bot: Bot
    command: str
    additional_markup: MessageMarkup = None

    def __init__(
        self,
        message: Message,
        bot: Bot,
        command: str,
        additional_markup: MessageMarkup = None,
    ):
        self.message = message
        self.bot = bot
        self.command = command
        self.additional_markup = additional_markup

    async def display(self) -> Optional[Any]:
        raise NotImplemented
