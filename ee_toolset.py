import flet as ft
from flet_route import Routing

from app.controls import GameDataSwitcher, SideBarControl
from app.controls.attributes.attribute_table import AttributeTable
import app.core.constants as constants
from app.core.log import logger
import app.core.styles as styles
from app.core.routing import app_routes
from app.models import GameData


def main(page: ft.Page):
    def check_item_clicked(e):
        e.control.checked = not e.control.checked
        page.update()

    logger.info("main", page=page)
    page.window_height = constants.PAGE_WINDOW_HEIGHT
    page.window_width = constants.PAGE_WINDOW_WIDTH
    page.bgcolor = styles.ColorPalette.BG_PRIMARY

    page.appbar = ft.AppBar(
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
    page.title = constants.PAGE_TITLE
    page.scroll = ft.ScrollMode.AUTO

    # Setup routing

    game_data = GameData.load()
    # page.add(
    #     ft.Row(
    #         controls=[
    #             ft.Container(
    #                 # padding=ft.Padding(left=10, top=10, right=10, bottom=10),
    #                 padding=15,
    #                 content=SideBarControl(),
    #                 bgcolor=styles.ColorPalette.BG_SECONDARY,
    #                 width=250,
    #                 # height=800,
    #                 border_radius=ft.border_radius.all(15),
    #                 expand=False,
    #             ),
    #             ft.VerticalDivider(
    #                 width=2,
    #                 color=ft.colors.RED,
    #                 thickness=3,
    #             ),
    #             # GameDataSwitcher(game_data),
    #             AttributeTable(page=page),
    #         ],
    #         vertical_alignment=ft.alignment.top_center,
    #     )
    # )

    page.add(
        ft.Container(
            alignment=ft.alignment.top_center,
            content=ft.Row(
                controls=[
                    ft.Container(
                        # padding=ft.Padding(left=10, top=10, right=10, bottom=10),
                        padding=15,
                        content=SideBarControl(),
                        bgcolor=styles.ColorPalette.BG_SECONDARY,
                        width=250,
                        # height=800,
                        border_radius=ft.border_radius.all(15),
                        expand=False,
                    ),
                    ft.VerticalDivider(
                        width=2,
                        color=ft.colors.RED,
                        thickness=3,
                    ),
                    # GameDataSwitcher(game_data),
                    AttributeTable(page=page),
                ],
                vertical_alignment=ft.alignment.top_center,
            ),
        )
    )

    # Routing(
    #     page=page,  # Here you have to pass the page. Which will be found as a parameter in all your views
    #     app_routes=app_routes,  # Here a list has to be passed in which we have defined app routing like app_routes
    # )
    # page.go(page.route)

    page.update()


ft.app(target=main)
