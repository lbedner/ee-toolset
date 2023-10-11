from dataclasses import asdict
from typing import Callable

import flet as ft

import app.core.styles as styles


class BaseElevatedButton(ft.UserControl):
    def __init__(
        self,
        on_click_callable: Callable,
        style,
        text: str,
        text_style: styles.ButtonTextStyle,
        *args,
        **kwargs
    ):
        super().__init__()
        self.on_click_callable = on_click_callable
        self.style = style
        self.text = text
        self.text_style = text_style
        self.args = args
        self.kwargs = kwargs

    def build(self):
        return ft.ElevatedButton(
            style=self.style,
            content=ft.Text(self.text, **asdict(self.text_style)),
            on_click=lambda _: self.on_click_callable(*self.args, **self.kwargs),
        )


class ElevatedAddButton(BaseElevatedButton):
    def __init__(self, on_click_callable: Callable):
        super().__init__(
            on_click_callable,
            style=styles.ELEVATED_BUTTON_ADD_STYLE,
            text="Add",
            text_style=styles.AddButtonTextStyle,
        )


class ElevatedUpdateButton(BaseElevatedButton):
    def __init__(self, on_click_callable: Callable):
        super().__init__(
            on_click_callable,
            style=styles.ELEVATED_BUTTON_UPDATE_STYLE,
            text="Update",
            text_style=styles.UpdateButtonTextStyle,
        )


class ElevatedDeleteButton(BaseElevatedButton):
    def __init__(self, on_click_callable: Callable):
        super().__init__(
            on_click_callable,
            style=styles.ELEVATED_BUTTON_DELETE_STYLE,
            text="Delete",
            text_style=styles.DeleteButtonTextStyle,
        )


class ElevatedCancelButton(BaseElevatedButton):
    def __init__(self, on_click_callable: Callable):
        super().__init__(
            on_click_callable,
            style=styles.ELEVATED_BUTTON_CANCEL_STYLE,
            text="Cancel",
            text_style=styles.CancelButtonTextStyle,
        )
