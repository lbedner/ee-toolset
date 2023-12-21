import flet as ft
from app.controls import SideBarControl


class BaseView(ft.UserControl):
    def __init__(
        self,
        page: ft.Page,
        route: str,
        main_control: ft.UserControl,
        scroll_mode: str = ft.ScrollMode.AUTO,
    ):
        super().__init__()
        self.page = page
        self.route = route
        self.main_control = main_control
        self.scroll_mode = scroll_mode

    def create_view(self):
        return ft.View(
            scroll=self.scroll_mode,
            auto_scroll=False,
            route=self.route,
            controls=[
                self.page.appbar,
                ft.Container(
                    alignment=ft.alignment.top_center,
                    content=ft.Row(
                        controls=[
                            SideBarControl(page=self.page),
                            ft.VerticalDivider(
                                width=2,
                                color=ft.colors.RED,
                                thickness=3,
                            ),
                            self.main_control,
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.START,
                    ),
                ),
            ],
        )
