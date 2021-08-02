"""Checklist widget."""
from typing import Any, List, Sequence

from botx import Bot, BubbleElement, Message, MessageMarkup
from pybotx_widgets.resources import strings
from pybotx_widgets.service import merge_markup, send_or_update_message

SELECTED_ITEM_KEY = "checklist_selected_item"
CHECKED_ITEMS_KEY = "checklist_checked_items"


async def checklist(
    message: Message,
    bot: Bot,
    widget_content: Sequence,
    label: str,
    command: str,
    additional_markup: MessageMarkup = None,
) -> str:
    """Show checklist and return selected item.

    :param message - botx Message
    :param bot - botx Message
    :param widget_content - All content to be displayed
    :param label - Text of message
    :param command - Command for bubbles command attribute
    :param additional_markup - Additional markup for attaching to widget

    """
    # Get selected item
    selected_item = message.data.get(SELECTED_ITEM_KEY)

    if selected_item:
        # Append selected item in checked_items list
        checked_items = message.data.get(CHECKED_ITEMS_KEY, [])

        if selected_item in checked_items:
            checked_items.remove(selected_item)
        else:
            checked_items.append(selected_item)

        message.data[CHECKED_ITEMS_KEY] = checked_items

    markup = _get_markup(message, widget_content, command)

    message.data.pop(SELECTED_ITEM_KEY, None)

    if additional_markup:
        markup = merge_markup(markup, additional_markup)

    await send_or_update_message(message, bot, label, markup)

    return selected_item


def get_checked_items(message: Message) -> List[str]:
    """Get checked items list from message.data."""

    return message.data.get("checklist_checked_items", [])


def _get_markup(
    message: Message, widget_content: Sequence, command: str
) -> MessageMarkup:
    """Generate and return markup for Checklist widget."""

    markup = MessageMarkup()
    checked_items = message.data.get(CHECKED_ITEMS_KEY, [])

    for content_item in widget_content:
        if not isinstance(content_item, (list, tuple, set)):
            checkbox = _get_checkbox_emoji(content_item, checked_items)

            markup.bubbles.append(
                [
                    BubbleElement(
                        command=command,
                        label=f"{checkbox} {content_item}",
                        data={**message.data, SELECTED_ITEM_KEY: content_item},
                    )
                ]
            )
            continue

        row = []
        for row_item in content_item:
            checkbox = _get_checkbox_emoji(row_item, checked_items)

            row.append(
                BubbleElement(
                    command=command,
                    label=f"{checkbox} {row_item}",
                    data={**message.data, SELECTED_ITEM_KEY: row_item},
                )
            )
        markup.bubbles.append(row)

    return markup


def _get_checkbox_emoji(content_item: Any, checked_items: List[str]) -> str:
    """Get selected or unselected checkbox emoji."""

    # If item is selected
    if content_item in checked_items:
        return strings.CHECKBOX_CHECKED

    return strings.CHECKBOX_UNCHECKED
