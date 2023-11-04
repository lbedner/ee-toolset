import flet as ft
from icecream import ic

from app.core.constants import INDEX_ROUTE, ATTRIBUTES_ROUTE
import app.core.styles as styles


class SideBarControl(ft.UserControl):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page

    def create_item_container(
        self,
        icon: str,
        label: str,
        destination_route: str = None,
    ) -> ft.Container:
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
            on_click=lambda _: self.page.go(destination_route)
            if destination_route
            else None,
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
            "Game Management": [
                (ft.icons.SAVE_OUTLINED, "Save Game Editor", INDEX_ROUTE)
            ],
            "Design": [
                (ft.icons.HANDYMAN_OUTLINED, "Attributes", ATTRIBUTES_ROUTE),
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
            # padding=ft.Padding(left=10, top=10, right=10, bottom=10),
            padding=15,
            # content=SideBarControl(page=page),
            content=ft.Container(
                height=1300,
                width=300,
                # bgcolor="#282828",
                bgcolor=styles.ColorPalette.BG_SECONDARY,
                content=ft.Column(
                    controls=controls,
                    spacing=15,
                ),
            ),
            # on_hover=lambda e: ic(e),
            # bgcolor=styles.ColorPalette.BG_SECONDARY,
            bgcolor=styles.ColorPalette.BG_SECONDARY,
            width=250,
            # height=800,
            border_radius=ft.border_radius.all(15),
            expand=False,
        )
