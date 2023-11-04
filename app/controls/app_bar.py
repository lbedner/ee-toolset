import flet as ft

import app.core.constants as constants
import app.core.styles as styles


class AppBar(ft.UserControl):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page

    def build(self):
        def check_item_clicked(e):
            e.control.checked = not e.control.checked
            self.page.update()

        return ft.AppBar(
            leading_width=40,
            title=ft.Text(
                constants.PAGE_TITLE,
                size=styles.FontConfig.HEADER_SIZE,
                font_family=styles.FontConfig.FAMILY_PRIMARY,
                weight=ft.FontWeight.W_700,
                color=styles.ColorPalette.TEXT_PRIMARY_DEFAULT,
            ),
            center_title=False,
            bgcolor=styles.ColorPalette.BG_PRIMARY,
            actions=[
                ft.IconButton(ft.icons.WB_SUNNY_OUTLINED, tooltip="Light/Dark Mode"),
                ft.IconButton(ft.icons.PERSON_OUTLINED, tooltip="Profile"),
                ft.PopupMenuButton(
                    icon=ft.icons.SETTINGS_OUTLINED,
                    items=[
                        ft.PopupMenuItem(text="Item 1"),
                        ft.PopupMenuItem(),  # divider
                        ft.PopupMenuItem(
                            text="Checked item",
                            checked=False,
                            on_click=check_item_clicked,
                        ),
                    ],
                    tooltip="Settings",
                ),
            ],
        )
