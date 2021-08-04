from typing import Any, Optional

from botx import Bot, Message, MessageMarkup


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

    async def display(self) -> Optional[Any]:
        raise NotImplementedError

    @classmethod
    async def get_value(cls, message: Message, bot: Bot) -> Any:
        raise NotImplementedError
