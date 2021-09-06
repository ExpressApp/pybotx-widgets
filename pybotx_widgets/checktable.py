from typing import Any, Dict, Generic, List, Optional, TypeVar, Union

from pydantic import BaseModel, root_validator

from pybotx_widgets.base import Widget, WidgetMarkup
from pybotx_widgets.resources import strings
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
    def is_checkbox_value_exist_in_mapping(
        cls, values: Dict[str, Any]
    ) -> Dict[str, Any]:
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


class MarkupMixin(WidgetMarkup):
    CHECKBOX_CHECKED: str = strings.CHECKBOX_CHECKED
    CHECKBOX_UNCHECKED: str = strings.CHECKBOX_UNCHECKED
    EMPTY: str = strings.EMPTY
    FILL_LABEL: str = strings.FILL_LABEL
    CHOOSE_LABEL: str = strings.CHOOSE_LABEL

    checkboxes: List[CheckboxContent]
    uncheck_command: str

    def get_button_value_text(self, checkbox: CheckboxContent) -> str:
        """Get value text for button."""

        if checkbox.checkbox_value is None:
            return self.EMPTY

        is_undefined = isinstance(checkbox.checkbox_value, Undefined)

        if checkbox.mapping:
            if is_undefined:
                return self.CHOOSE_LABEL
            return checkbox.mapping[checkbox.checkbox_value]

        if is_undefined:
            return self.FILL_LABEL

        return checkbox.checkbox_value  # type: ignore

    def add_checkboxes(self) -> None:
        """Add checkboxes."""

        for checkbox in self.checkboxes:
            checkbox.data = checkbox.data or {}

            if isinstance(checkbox.checkbox_value, Undefined):
                checkbox_status = self.CHECKBOX_UNCHECKED
            else:
                checkbox_status = self.CHECKBOX_CHECKED

            checkbox_text = f"{checkbox_status} {checkbox.label}"

            value_text = self.get_button_value_text(checkbox)

            self.widget_msg.markup.add_bubble(
                self.uncheck_command, checkbox_text, data=checkbox.data
            )
            self.widget_msg.markup.add_bubble(
                checkbox.command, value_text, new_row=False, data=checkbox.data
            )


class ChecktableWidget(Widget, MarkupMixin):
    def __init__(
        self,
        checkboxes: List[CheckboxContent],
        label: str,
        uncheck_command: str,
        *args: Any,
        **kwargs: Any,
    ):
        """Create checktable widget.

        :param checkboxes - All content to be displayed
        :param label - Text of message
        :param uncheck_command - Command for handler which uncheck value
        """
        super().__init__(*args, **kwargs)

        self.checkboxes = checkboxes
        self.uncheck_command = uncheck_command
        self.widget_msg.text = label

    def add_markup(self) -> None:
        self.add_checkboxes()
        self.add_additional_markup()
