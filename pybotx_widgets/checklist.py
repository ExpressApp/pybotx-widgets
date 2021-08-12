"""Checklist widget."""
from typing import Any, Optional, Sequence, Union, List

from botx import BubbleElement, Message, MessageMarkup

from pybotx_widgets.base import Widget
from pybotx_widgets.resources import strings
from pybotx_widgets.service import merge_markup, send_or_update_message

SELECTED_ITEM_KEY = "checklist_selected_item"
CHECKED_ITEMS_KEY = "checklist_checked_items"


class MarkupMixin:
    CHECKBOX_CHECKED: str
    CHECKBOX_UNCHECKED: str

    command: str
    message: Message
    widget_content: Sequence

    markup = MessageMarkup()
    checked_items: list

    def get_checkbox_emoji(self, content_item: Any) -> str:
        """Get selected or unselected checkbox emoji."""

        # If item is selected
        if content_item in self.checked_items:
            return self.CHECKBOX_CHECKED

        return self.CHECKBOX_UNCHECKED

    def add_item(self, value: Union[list, str]) -> None:
        """Add checkbox item."""

        self.markup.bubbles.append(value)

    def add_row(self, row: Sequence) -> None:
        """Add buttons row into markup."""

        buttons_row = []
        for row_item in row:
            checkbox = self.get_checkbox_emoji(row_item)

            buttons_row.append(
                BubbleElement(
                    command=self.command,
                    label=f"{checkbox} {row_item}",
                    data={**self.message.data, SELECTED_ITEM_KEY: row_item},
                )
            )
        self.add_item(buttons_row)

    def add_markup(self) -> None:
        """Generate markup for Checklist widget."""

        for content_item in self.widget_content:
            if isinstance(content_item, (list, tuple, set)):
                # if markup is in table format, then add row with buttons
                self.add_row(content_item)
                continue

            checkbox = self.get_checkbox_emoji(content_item)
            self.add_item(
                [
                    BubbleElement(
                        command=self.command,
                        label=f"{checkbox} {content_item}",
                        data={**self.message.data, SELECTED_ITEM_KEY: content_item},
                    )
                ]
            )


class CheckListWidget(Widget, MarkupMixin):
    CHECKBOX_CHECKED = strings.CHECKBOX_CHECKED
    CHECKBOX_UNCHECKED = strings.CHECKBOX_UNCHECKED

    def __init__(
        self,
        widget_content: Sequence,
        label: str,
        *args: Any,
        **kwargs: Any
    ):
        """
        :param widget_content - All content to be displayed
        :param label - Text of message
        """
        super().__init__(*args, **kwargs)
        self.widget_content = widget_content
        self.label = label

        self.markup = MessageMarkup()
        self.selected_item = self.message.data.get(SELECTED_ITEM_KEY)
        self.checked_items = self.message.data.get(CHECKED_ITEMS_KEY, [])

    @classmethod
    def get_value(cls, message: Message) -> str:
        return message.data[SELECTED_ITEM_KEY]

    @classmethod
    def get_checked_items(cls, message: Message) -> List[str]:
        return message.data.get(CHECKED_ITEMS_KEY, [])

    async def display(self) -> Optional[str]:
        """Show checklist and return selected item."""

        if self.selected_item:
            if self.selected_item in self.checked_items:
                self.checked_items.remove(self.selected_item)
            else:
                self.checked_items.append(self.selected_item)

            self.message.data[CHECKED_ITEMS_KEY] = self.checked_items

        self.add_markup()

        if self.additional_markup:
            self.markup = merge_markup(self.markup, self.additional_markup)

        await send_or_update_message(self.message, self.bot, self.label, self.markup)

        return self.get_value(self.message) if self.selected_item else None
