"""Widgets services."""

from typing import Optional

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
) -> None:
    """Send new message or update exist."""

    is_pybotx_widget = message.data.get("pybotx_widget")

    markup = markup or MessageMarkup()

    if is_pybotx_widget:
        payload = UpdatePayload(text=text, file=msg_file)
        payload.set_markup(markup=markup)

        await bot.update_message(
            SendingCredentials(
                sync_id=message.source_sync_id, bot_id=message.bot_id, host=message.host
            ),
            update=payload,
        )
    else:
        message = SendingMessage.from_message(text=text, file=msg_file, message=message)
        message.markup = markup
        await bot.send(message)
