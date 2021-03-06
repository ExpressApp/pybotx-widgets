# pybotx-widgets

Примеры виджетов для pybotx. Могут быть использованы в проектах ботов.

---
### Установка

Выполните следующую команду в консоли:

`poetry add git+https://github.com/ExpressApp/pybotx-widgets.git`

---

### Виджет Carousel
#### Inline mode:
![carousel_img](pybotx_widgets/images/inline_carousel1.png "Carousel") 
![carousel_img](pybotx_widgets/images/inline_carousel2.png "Carousel")
![carousel_img](pybotx_widgets/images/inline_carousel3.png "Carousel")

#### Newline mode:
![carousel_img](pybotx_widgets/images/carousel1.png "Carousel") 
![carousel_img](pybotx_widgets/images/carousel2.png "Carousel")
![carousel_img](pybotx_widgets/images/carousel3.png "Carousel")

---

### Виджет Calendar
![calendar_img](pybotx_widgets/images/calendar.png?raw=true "Calendar")

#### `include_past=False` mode:
![calendar_img](pybotx_widgets/images/calendar_without_arrows.png?raw=true "Calendar")

---

### Виджет Checklist
![calendar_img](pybotx_widgets/images/checklist.png?raw=true "Checklist")

---

### Виджет Pagination
![calendar_img](pybotx_widgets/images/pagination.png?raw=true "Pagination")

---

### Виджет Checktable
![checktable_img](pybotx_widgets/images/checktable.png?raw=true "Checktable")

---
### Пример использования виджета Carousel:

```python
from pybotx_widgets.carousel import CarouselWidget
from botx import MessageMarkup

...

@collector.handler(command="/some_command", name="some_command_name")
async def some_command(message: Message, bot: Bot) -> None:
    markup = MessageMarkup()
    await CarouselWidget(
        widget_content,  # All content to be displayed
        label,  # Text of message
        start_from=0,  # Start display content from
        displayed_content_count=3,  # Count of content to be displayed
        selected_value_label="You selected: {selected_val}",  # Display format of the selected value, default = "{label} {selected_val}"
        control_labels=("", ""),  # Override default control labels
        inline=False,  # Inline mode
        loop=False,  # Loop content or not
        show_numbers=False,  # Show content order numbers for prev/next control bubbles' labels. Default = False
        additional_markup=markup,  # Additional markup for attaching to widget
        message=message,
        bot=bot,
        command="/some_command",  # Widget will trigger this command when a value is selected.
    ).display()
    
    try:
        selected_value = await CarouselWidget.get_value(message, bot)
    except KeyError:
        ...  #  do something
```
Метод `.display()` отправляет пользователю сообщение с виджетом.\
При отсутствии выбранного значения, метод `.get_value()` вызовет исключение.

Если виджет должен обновить уже отправленное сообщение, то добавьте в `message.command.data` ключ `message_id` 
с UUID сообщения, которое нужно обновить

Когда `loop=True`, стрелки отображаются всегда

---

### Пример использования виджета Calendar:

```python
from pybotx_widgets.calendar import CalendarWidget

...

@collector.handler(command="/some_command", name="some_command_name")
async def some_command(message: Message, bot: Bot) -> None:
    await CalendarWidget(
        start_date: date = None,  # Calendar start date, previews dates hides, default date.today()
        end_date: date = date.max,  # Calendar end date, next dates hides, default date.max
        include_past=False,  # Include past dates in calendar, default is False
        additional_markup=None,  # Additional markup for attaching to widget, default None
        command_name="/some_command",  # Widget will trigger this command when a value is selected.
        message=message, 
        bot=bot,
    ).display()
    
    try:
        selected_value = await CalendarWidget.get_value()
    except KeyError:
        ...  #  do something
```
Метод `.display()` отправляет пользователю сообщение с виджетом.\
При отсутствии выбранного значения, метод `.get_value()` вызовет исключение.

Когда пользователь выберет какое-то значение из виджета, метод `.get_value()` вернет его

Если виджет должен обновить уже отправленное сообщение, то добавьте в `message.command.data` ключ `message_id` 
с UUID сообщения, которое нужно обновить

---

### Пример использования виджета Checklist:

```python
from pybotx_widgets.checklist import CheckListWidget

...

@collector.handler(command="/some_command")
async def some_command(message: Message, bot: Bot) -> None:
    await CheckListWidget(
        content,  # All content to be displayed
        label,  # Text of message
        command="/some_command",  # Widget will trigger this command when a value is selected.
        message=message,
        bot=bot,
    ).display()
    
    try:
        current_selected_item = CheckListWidget.get_value(message)
    except KeyError:
        ...  #  do something
    
    all_selected_items = CheckListWidget.get_checked_items(message)
    
    if all_selected_items:
        ...  #  do something
```
Метод `.display()` отправляет пользователю сообщение с виджетом.\
При отсутствии выбранного значения, метод `.get_value()` вызовет исключение.

Список всех выбранных элементов можно получить через метод `.get_checked_items(message)`, по умолчанию пустой список.

Если виджет должен обновить уже отправленное сообщение, то добавьте в `message.command.data` ключ `message_id` 
с UUID сообщения, которое нужно обновить

---

### Пример использования виджета Pagination:

```python
from pybotx_widgets.pagination import PaginationWidget

...

@collector.handler(command="/some_command")
async def some_command(message: Message, bot: Bot) -> None:
    await PaginationWidget(
        content,  # All content to be displayed: List[SendingMessage]
        paginate_by, # Number of messages on one page        
        command="/some_command",  # Widget will trigger this command when a value is selected.
        message=message,
        bot=bot,
    ).display()
```
Метод `.display()` отправляет пользователю сообщение с виджетом.\

Если виджет должен обновить уже отправленное сообщение, то добавьте в `message.command.data` ключ `message_id` 
с UUID сообщения, которое нужно обновить

---

### Пример использования виджета Checktable:

```python
from pybotx_widgets.checktable import ChecktableWidget

...

@collector.handler(command="/some_command")
async def some_command(message: Message, bot: Bot) -> None:
    await ChecktableWidget(
        content,  # All content to be displayed: List[CheckboxContent]
        label, # Text of message
        "uncheck_command", # Command for handler which uncheck value         
        "some_command",  # Command for bubbles command attribute
        additional_markup,  # Additional markup for attaching to widget
        message=message,
        bot=bot,
    ).display()
```
Для корректной работы виджета нужно создать хэндлер с командой `uncheck_command` и прописать в нем поведение при сбрасывании значения.

#### Пример хэндлера:

```python
from pybotx_widgets.checktable import ChecktableWidget
from pybotx_widgets.undefined import undefined

...

UNCHECK_COMMAND = "/_checkbox:uncheck"

@collector.hidden(command=UNCHECK_COMMAND)
async def checkbox_uncheck(message: Message, bot: Bot) -> None:
    field_name = message.data.get("field_name")
    my_object = await get_my_object()
    
    setattr(my_object, field_name, undefined)
    await set_my_object(my_object)
        
    checkboxes = await build_checkboxes(my_object)
    await ChecktableWidget(message, bot, my_object, "some_label", UNCHECK_COMMAND).display()
```

---

## ЭМОДЗИ
В `pybotx_widgets.resources.strings` есть следующие эмодзи:

LEFT_ARROW = ⬅️ <br/>
RIGHT_ARROW = ➡️ <br/>
UP_ARROW = ⬆️ <br/>
DOWN_ARROW = ⬇️ <br/>
CHECKBOX_CHECKED = ☑ <br/>
CHECKBOX_UNCHECKED = ☐ <br/>
CHECK_MARK = ✔️ <br/>
ENVELOPE = ✉️ <br/>
PENCIL = ✏️ <br/>
CROSS_MARK = ❌ <br/>
