import threading
from typing import Callable, Optional

import pyperclip

import app.core.styles as styles
import flet as ft
from app.controls.attributes.snack_bar import SuccessSnackBar


class CopyButton(ft.UserControl):
    def __init__(
        self,
        page: ft.Page,
        text: str,
        tooltip: str = "Copy to clipboard",
        icon: str = ft.icons.COPY_OUTLINED,
        icon_size: int = 16,
        on_click: Optional[Callable[[], None]] = None,
        show_success_snack_bar: bool = True,
    ):
        super().__init__()
        self.page = page
        self.text = text
        self.tooltip = tooltip
        self.icon = icon
        self.original_icon = icon
        self.icon_size = icon_size
        self.on_click = on_click if on_click else self.default_on_click
        self.show_success_snack_bar = show_success_snack_bar
        self.icon_button = ft.IconButton(
            icon=self.icon,
            icon_size=self.icon_size,
            tooltip=self.tooltip,
            on_click=lambda _: self.on_click(),
        )

    def build(self) -> ft.IconButton:
        return self.icon_button

    def default_on_click(self) -> None:
        pyperclip.copy(self.text)
        self.icon_button.icon = ft.icons.CHECK
        self.icon_button.icon_color = styles.ColorPalette.ACCENT_SUCCESS
        self.icon_button.update()

        confirmation_duration_ms: int = 3000
        if self.show_success_snack_bar:
            SuccessSnackBar(
                "Copied to clipboard", self.page, duration_ms=confirmation_duration_ms
            ).open()
        threading.Thread(
            target=self.revert_icon, args=(confirmation_duration_ms / 1000,)
        ).start()

    def revert_icon(self, delay) -> None:
        threading.Event().wait(delay)
        self.icon_button.icon = self.original_icon
        self.icon_button.icon_color = None
        self.icon_button.update()
