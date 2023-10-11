import flet as ft
from icecream import ic

import app.core.styles as styles


class SideBarControl(ft.UserControl):
    def __init__(self):
        super().__init__()

    def create_item_container(self, icon: str, label: str) -> ft.Container:
        def on_hover(e):
            e.control.bgcolor = (
                "#2a2a2a"
                if e.data.lower() == "true"
                else styles.ColorPalette.BG_SECONDARY
            )
            e.control.update()

        return ft.Container(
            height=30,
            width=350,
            content=ft.Row(
                controls=[
                    ft.Icon(
                        icon,
                        size=24,
                        color=styles.ColorPalette.TEXT_PRIMARY_DEFAULT,
                    ),
                    ft.Text(
                        label,
                        **styles.SidebarLabelStyle().to_dict(),
                    ),
                ],
                spacing=15,
            ),
            on_hover=on_hover,
        )

    def create_subcategory_container(self, label_heading: str) -> ft.Container:
        return ft.Container(
            ft.Text(
                label_heading,
                **styles.SidebarLabelHeadingStyle().to_dict(),
            ),
            height=50,
        )

    def create_controls_group(self, subcategory: str, items: list) -> list:
        controls_group = [
            self.create_subcategory_container(subcategory),
        ]
        for item in items:
            controls_group.append(self.create_item_container(*item))
        controls_group.append(ft.Divider(height=10, thickness=2, color="#444444"))
        return controls_group

    def build(self):
        items_dict = {
            "Game Management": [(ft.icons.SAVE_OUTLINED, "Save Game Editor")],
            "Design": [
                (ft.icons.HANDYMAN_OUTLINED, "Attributes"),
                (ft.icons.KEY_OUTLINED, "Items"),
                (ft.icons.LOCAL_FIRE_DEPARTMENT_OUTLINED, "Abilities"),
            ],
            "Media": [(ft.icons.LIBRARY_MUSIC_OUTLINED, "Audio")],
            "Lore": [
                (ft.icons.MAP_OUTLINED, "Codex"),
                (ft.icons.CHAT_BUBBLE_OUTLINE, "Illiana"),
            ],
        }
        controls = []
        for subcategory, items in items_dict.items():
            controls += self.create_controls_group(subcategory, items)
        return ft.Container(
            height=1300,
            width=300,
            # bgcolor="#282828",
            bgcolor=styles.ColorPalette.BG_SECONDARY,
            content=ft.Column(
                controls=controls,
                spacing=15,
            ),
            # on_hover=lambda e: ic(e),
            # bgcolor=styles.ColorPalette.BG_SECONDARY,
        )
