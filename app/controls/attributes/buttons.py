from dataclasses import asdict
from typing import Callable

import app.core.styles as styles
import flet as ft


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


class ElevatedRefreshButton(BaseElevatedButton):
    def __init__(self, on_click_callable: Callable):
        super().__init__(
            on_click_callable,
            style=styles.ELEVATED_BUTTON_REFRESH_STYLE,
            text="Refresh",
            text_style=styles.RefreshButtonTextStyle,
        )


class BaseIconButton(ft.UserControl):
    def __init__(
        self,
        on_click_callable: Callable,
        icon: str,
        color: str = None,
        get_param_callable: Callable = None,
        tooltip: str = None,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.on_click_callable = on_click_callable
        self.get_param_callable = get_param_callable
        self.icon = icon
        self.color = color
        self.tooltip = tooltip

    def build(self) -> ft.IconButton:
        return ft.IconButton(
            icon=self.icon,
            icon_color=self.color,
            on_click=lambda _: self.on_click(),
            tooltip=self.tooltip,
        )

    def on_click(self):
        param = self.get_param_callable() if self.get_param_callable else None
        if param:
            self.on_click_callable(param)
        else:
            self.on_click_callable()


class IconAddButton(BaseIconButton):
    def __init__(self, on_click_callable: Callable):
        super().__init__(
            on_click_callable,
            icon=ft.icons.ADD_OUTLINED,
            # color=styles.ColorPalette.ACCENT,
            tooltip="Add knowledge base.",
        )


class IconRefreshButton(BaseIconButton):
    def __init__(self, on_click_callable: Callable, get_param_callable: Callable):
        super().__init__(
            on_click_callable,
            icon=ft.icons.REFRESH_SHARP,
            # color=styles.ColorPalette.ACCENT_SUCCESS,
            get_param_callable=get_param_callable,
            tooltip="Refresh selected knowledge base.",
        )


class IconDeleteButton(BaseIconButton):
    def __init__(self, on_click_callable: Callable, get_param_callable: Callable):
        super().__init__(
            on_click_callable,
            icon=ft.icons.DELETE_OUTLINED,
            # color=styles.ColorPalette.ACCENT_STOP,
            get_param_callable=get_param_callable,
            tooltip="Delete selected knowledge base.",
        )
