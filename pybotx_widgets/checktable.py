from typing import Any, Dict, List, Optional, TypeVar, Generic, Union

from botx import Bot, Message, MessageMarkup
from pydantic import root_validator, BaseModel

from pybotx_widgets.resources import strings
from pybotx_widgets.service import merge_markup, send_or_update_message
from pybotx_widgets.undefined import Undefined, undefined

T = TypeVar("T")  # noqa: WPS111


class CheckboxContent(BaseModel, Generic[T]):
    """Checkbox content."""

    #: text that will be shown on the element.
    label: str
    #: command that will be triggered by click on the element.
    command: str
    #: value which will be displayed on the button associated with this checkbox.
    checkbox_value: Optional[Union[T, Undefined]] = undefined
    #: list of available values.
    mapping: Optional[Dict[T, str]] = None
    #: extra payload that will be stored in button and then received in new message.
    data: Optional[Dict[str, Any]] = None

    class Config:
        arbitrary_types_allowed = True

    @root_validator(pre=True)
    def is_checkbox_value_exist_in_mapping(cls, values):
        mapping = values.get("mapping")
        checkbox_value = values.get("checkbox_value")
        if (
                mapping
                and not isinstance(checkbox_value, Undefined)
                and checkbox_value not in mapping
        ):
            raise ValueError(
                f"'mapping' should contains 'checkbox_value' - '{checkbox_value}'"
            )

        return values


def add_checkboxes(checkboxes: List[CheckboxContent]) -> MessageMarkup:
    """Add checkbox."""
    markup = MessageMarkup()

    for checkbox in checkboxes:
        if checkbox.data is None:
            checkbox.data = {}  # noqa: WPS110

        if isinstance(checkbox.checkbox_value, Undefined):
            checkbox_status = strings.CHECKBOX_UNCHECKED
        else:
            checkbox_status = strings.CHECKBOX_CHECKED

        checkbox_text = f"{checkbox_status} {checkbox.label}"

        if checkbox.checkbox_value is None:
            value_text = strings.EMPTY
        else:
            if checkbox.mapping:
                if not isinstance(checkbox.checkbox_value, Undefined):
                    value_text = checkbox.mapping[checkbox.checkbox_value]
                else:
                    value_text = strings.CHOOSE_LABEL

            else:
                if not isinstance(checkbox.checkbox_value, Undefined):
                    value_text = checkbox.checkbox_value
                else:
                    value_text = strings.FILL_LABEL

        markup.add_bubble(checkbox.command, checkbox_text, data=checkbox.data)
        markup.add_bubble(
            checkbox.command, value_text, new_row=False, data=checkbox.data
        )

    return markup


async def checktable(
    message: Message,
    bot: Bot,
    checkboxes: List[CheckboxContent],
    label: str,
    additional_markup: MessageMarkup = None,
) -> None:
    """Create checktable widget.

    :param message - botx Message
    :param bot - botx Bot
    :param checkboxes - All content to be displayed
    :param label - Text of message
    :param additional_markup - Additional markup for attaching to widget
    """

    markup = add_checkboxes(checkboxes)

    if additional_markup:
        markup = merge_markup(markup, additional_markup)

    await send_or_update_message(message, bot, label, markup)
