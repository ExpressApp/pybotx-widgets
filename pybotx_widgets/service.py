"""Widgets services."""

from typing import Optional, Union
from uuid import UUID, uuid4

from botx import (
    Bot,
    File,
    Message,
    MessageMarkup,
    SendingCredentials,
    SendingMessage,
    UpdatePayload,
)


async def send_or_update_message(
    message: Message,
    bot: Bot,
    text: Optional[str],
    markup: MessageMarkup = None,
    msg_file: File = None,
    new_message_id: Union[str, UUID] = None,
) -> None:
    """Send new message or update exist."""

    current_message_id = message.data.get("message_id")
    new_message_id = new_message_id or uuid4()

    if markup:
        for bubbles in markup.bubbles:
            for bubble in bubbles:
                bubble.data["message_id"] = current_message_id or new_message_id
    else:
        markup = MessageMarkup()

    if current_message_id:
        payload = UpdatePayload(text=text, file=msg_file)
        payload.set_markup(markup=markup)

        await bot.update_message(
            SendingCredentials(
                sync_id=current_message_id, bot_id=message.bot_id, host=message.host
            ),
            update=payload,
        )
    else:
        message = SendingMessage.from_message(text=text, file=msg_file, message=message)
        message.credentials.message_id = new_message_id
        message.markup = markup
        await bot.send(message)
