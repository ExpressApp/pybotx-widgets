"""Carousel widget."""

from itertools import cycle, islice
from typing import Any, Iterator, Sequence, Tuple, Optional

from botx import Bot, BubbleElement, Message

from pybotx_widgets.base import Widget, WidgetMarkup
from pybotx_widgets.resources import strings
from pybotx_widgets.service import send_or_update_message

LEFT_PRESSED = "CAROUSEL_LEFT_BUTTON_PRESSED"
RIGHT_PRESSED = "CAROUSEL_RIGHT_BUTTON_PRESSED"

START_FROM_KEY = "carousel_start_from"
SELECTED_VALUE_KEY = "carousel_selected_val"
SELECTED_VALUE_LABEL_KEY = "carousel_selected_value_label"
MESSAGE_LABEL_KEY = "carousel_message_label"


class ValidationMixin:
    LEFT_ARROW: str
    RIGHT_ARROW: str
    SELECTED_VALUE_LABEL: str

    widget_content: Sequence
    _start_from: int
    loop: bool
    inline: bool
    show_numbers: bool
    _control_labels: Tuple[str, str]

    def _validate_params(self) -> None:
        if "{selected_val}" not in self.SELECTED_VALUE_LABEL:
            raise ValueError("'SELECTED_VALUE_LABEL' should contains '{selected_val}'")

        if self._start_from > len(self.widget_content):
            raise ValueError("'start_from' is greater than 'widget_content'")

        if self.loop and self.show_numbers:
            raise ValueError("Sorry, you can't enable both 'loop' and 'show_numbers'")

        if self.inline and self.show_numbers:
            raise ValueError("Sorry, you can't enable both 'inline' and 'show_numbers'")

        if self.show_numbers:
            if self._control_labels[0].count("{}") != 2:
                raise ValueError("Left control label should have exactly two '{}'")

            if self._control_labels[1].count("{}") != 2:
                raise ValueError("Right control label should have exactly two '{}'")


class MarkupMixin(WidgetMarkup):
    displayed_content: Iterator

    widget_content: Sequence
    displayed_content_count: int
    start_from: int
    end: int
    loop: bool

    message: Message
    command: str

    content_len: int
    left_btn_label: str
    right_btn_label: str

    def get_left_and_right_button_visibility(self) -> Tuple[bool, bool]:
        if len(self.widget_content) <= self.displayed_content_count:
            # if all content displayed, then hide arrows
            return False, False
        elif self.loop:
            # always show arrows
            return True, True
        else:
            return (self.start_from > 0), (self.end < self.content_len)

    def add_inline_markup(self) -> None:
        """Build inline markup for Carousel widget."""
        show_left_arrow, show_right_arrow = self.get_left_and_right_button_visibility()

        if show_left_arrow:
            self.widget_msg.markup.add_bubble(
                command=self.message.command.command,
                label=self.left_btn_label,
                data={**self.message.data, SELECTED_VALUE_KEY: LEFT_PRESSED},
                new_row=False,
            )

        for content_item in self.displayed_content:
            self.widget_msg.markup.add_bubble(
                command=self.command,
                label=content_item,
                data={**self.message.data, SELECTED_VALUE_KEY: content_item},
                new_row=False,
            )

        if show_right_arrow:
            self.widget_msg.markup.add_bubble(
                command=self.message.command.command,
                label=self.right_btn_label,
                data={**self.message.data, SELECTED_VALUE_KEY: RIGHT_PRESSED},
                new_row=False,
            )

    def add_newline_markup(self) -> None:
        """Build newline markup for Carousel widget."""

        show_left_arrow, show_right_arrow = self.get_left_and_right_button_visibility()
        right_arrow_bubble = {
            "command": self.message.command.command,
            "label": self.right_btn_label,
            "data": {**self.message.data, SELECTED_VALUE_KEY: RIGHT_PRESSED},
        }

        for content_item in self.displayed_content:
            if isinstance(content_item, (list, tuple, set)):
                self.widget_msg.markup.bubbles.append(
                    [
                        BubbleElement(
                            command=self.command,
                            label=row_item,
                            data={**self.message.data, SELECTED_VALUE_KEY: row_item},
                        )
                        for row_item in content_item
                    ]
                )
                continue

            self.widget_msg.markup.bubbles.append(
                [
                    BubbleElement(
                        command=self.command,
                        label=content_item,
                        data={**self.message.data, SELECTED_VALUE_KEY: content_item},
                    )
                ]
            )

        if show_left_arrow:
            self.widget_msg.markup.add_bubble(
                command=self.message.command.command,
                label=self.left_btn_label,
                data={**self.message.data, SELECTED_VALUE_KEY: LEFT_PRESSED},
            )
            # if left arrow displayed, then show right arrow inline
            right_arrow_bubble["new_row"] = False

        if show_right_arrow:
            self.widget_msg.markup.add_bubble(**right_arrow_bubble)


class CarouselWidget(Widget, ValidationMixin, MarkupMixin):
    LEFT_ARROW = strings.LEFT_ARROW
    RIGHT_ARROW = strings.RIGHT_ARROW
    LEFT_LABEL_WITH_NUMBERS = f"{LEFT_ARROW} ({{}}-{{}})"
    RIGHT_LABEL_WITH_NUMBERS = f"{RIGHT_ARROW} ({{}}-{{}})"

    # Display format of the selected value, default = "{label} {selected_val}"
    SELECTED_VALUE_LABEL = strings.SELECTED_VALUE_LABEL

    def __init__(
        self,
        widget_content: Sequence,
        label: str,
        start_from: int = 0,
        displayed_content_count: int = 3,
        control_labels: Tuple[str, str] = None,
        inline: bool = True,
        loop: bool = True,
        show_numbers: bool = False,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        :param widget_content - All content to be displayed
        :param label - Text of message
        :param start_from - Start display content from
        :param displayed_content_count - Count of content to be displayed
        :param control_labels - Override default control labels.
        :param inline - Inline mode
        :param loop - Loop content or not
        :param show_numbers - Show content order numbers
        for prev/next control bubbles' labels.
        """
        super().__init__(*args, **kwargs)

        self.widget_content = widget_content
        self.widget_msg.text = label
        self._start_from = start_from
        self.displayed_content_count = displayed_content_count
        self.inline = inline
        self.loop = loop
        self.show_numbers = show_numbers

        if not control_labels:
            if self.show_numbers:
                self._control_labels = (
                    self.LEFT_LABEL_WITH_NUMBERS,
                    self.RIGHT_LABEL_WITH_NUMBERS,
                )
            else:
                self._control_labels = (self.LEFT_ARROW, self.RIGHT_ARROW)

        self._validate_params()

        self.selected_val = self.message.data.get(SELECTED_VALUE_KEY, "")
        self._start_from = self.message.data.get(START_FROM_KEY, start_from)
        self.content_len = len(self.widget_content)

        if self.selected_val == LEFT_PRESSED:
            self._start_from -= displayed_content_count
        elif self.selected_val == RIGHT_PRESSED:
            self._start_from += displayed_content_count

        self.set_widget_data()

    @property
    def left_btn_label(self) -> str:
        """Left button label."""
        left_label = self._control_labels[0]

        if self.show_numbers:
            left_bound = self.start_from - self.displayed_content_count + 1
            left_label = left_label.format(left_bound, self.start_from)

        return left_label

    @property
    def right_btn_label(self) -> str:
        """Right button label."""
        right_label = self._control_labels[1]

        if self.show_numbers:
            right_bound = self.end + self.displayed_content_count
            if self.content_len < right_bound:
                right_bound = self.content_len

            right_label = right_label.format(self.end + 1, right_bound)

        return right_label

    @property
    def start_from(self) -> int:
        """Count start position."""

        if self._start_from < 0 or self._start_from > self.content_len:
            return abs(self.content_len - abs(self._start_from))

        return self._start_from

    @property
    def end(self) -> int:
        """Count end position."""

        return self.start_from + self.displayed_content_count

    @property
    def is_value_selected(self) -> bool:
        return self.selected_val and self.selected_val not in (
            LEFT_PRESSED,
            RIGHT_PRESSED,
        )

    @property
    def displayed_content(self) -> Iterator:
        if self.loop:
            # Loop content
            return islice(cycle(self.widget_content), self.start_from, self.end)

        return islice(self.widget_content, self.start_from, self.end)

    @classmethod
    async def get_value(cls, message: Message, bot: Bot) -> Optional[str]:
        selected_val = message.data[SELECTED_VALUE_KEY]
        label = message.data[MESSAGE_LABEL_KEY]

        if not selected_val or selected_val in {LEFT_PRESSED, RIGHT_PRESSED}:
            return

        msg_text = cls.SELECTED_VALUE_LABEL.format(
            label=label, selected_val=selected_val
        )
        await send_or_update_message(message, bot, msg_text)
        _clear_carousel_data(message)

        return selected_val

    def set_widget_data(self) -> None:
        """Set widget related data into message.data."""

        # Set current position in message.data
        self.message.data[START_FROM_KEY] = self._start_from

        # Set selected_value_label and carousel_message_label for get_carousel_result
        self.message.data[SELECTED_VALUE_LABEL_KEY] = self.SELECTED_VALUE_LABEL
        self.message.data[MESSAGE_LABEL_KEY] = self.widget_msg.text

    def add_markup(self) -> None:
        if self.inline:
            self.add_inline_markup()
        else:
            self.add_newline_markup()

        self.add_additional_markup()


def _clear_carousel_data(message: Message) -> None:
    """Clear widget data from message.data."""

    message.data.pop("message_id", None)
    message.data.pop(SELECTED_VALUE_KEY, None)
    message.data.pop(SELECTED_VALUE_LABEL_KEY, None)
    message.data.pop(MESSAGE_LABEL_KEY, None)
    message.data.pop(START_FROM_KEY, None)
