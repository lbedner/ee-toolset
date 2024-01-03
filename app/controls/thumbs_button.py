from typing import Callable, Optional

import flet as ft


class ThumbsUpDownButtons(ft.UserControl):
    def __init__(
        self,
        page: ft.Page,
        icon_size: int = 16,
        up_button_tooltip: str = "Upvote",
        down_button_tooltip: str = "Downvote",
        on_up_click: Optional[Callable[[], None]] = None,
        on_down_click: Optional[Callable[[], None]] = None,
    ):
        super().__init__()
        self.page = page
        self.up_button_tooltip = up_button_tooltip
        self.down_button_tooltip = down_button_tooltip
        self.on_up_click = on_up_click if on_up_click else self.default_on_up_click
        self.on_down_click = (
            on_down_click if on_down_click else self.default_on_down_click
        )
        self.up_selected_icon = ft.icons.THUMB_UP
        self.down_selected_icon = ft.icons.THUMB_DOWN
        self.up_unselected_icon = ft.icons.THUMB_UP_OUTLINED
        self.down_unselected_icon = ft.icons.THUMB_DOWN_OUTLINED
        self.up_button = ft.IconButton(
            icon=self.up_unselected_icon,
            icon_size=icon_size,
            tooltip=self.up_button_tooltip,
            on_click=lambda _: self.on_up_click(),
        )
        self.down_button = ft.IconButton(
            icon=self.down_unselected_icon,
            icon_size=icon_size,
            tooltip=self.down_button_tooltip,
            on_click=lambda _: self.on_down_click(),
        )

    def build(self):
        return ft.Row(
            spacing=0,
            controls=[
                self.up_button,
                self.down_button,
            ],
        )

    def default_on_up_click(self):
        self.up_button.icon = self.up_selected_icon
        self.up_button.update()
        self.down_button.icon = self.down_unselected_icon
        self.down_button.update()

    def default_on_down_click(self):
        self.up_button.icon = self.up_unselected_icon
        self.up_button.update()
        self.down_button.icon = self.down_selected_icon
        self.down_button.update()
