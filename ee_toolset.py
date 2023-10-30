import flet as ft
from flet_route import Routing

from app.controls import GameDataSwitcher, SideBarControl
from app.controls.attributes.attribute_table import AttributeTable
import app.core.constants as constants
from app.core.log import logger
from app.core.routing import app_routes
from app.models import GameData


def main(page: ft.Page):
    logger.info("main", page=page)
    page.window_height = constants.PAGE_WINDOW_HEIGHT
    page.window_width = constants.PAGE_WINDOW_WIDTH

    page.appbar = ft.AppBar(
        leading_width=40,
        title=ft.Text(constants.PAGE_TITLE),
        center_title=False,
        bgcolor=ft.colors.SURFACE_VARIANT,
    )
    page.title = constants.PAGE_TITLE
    page.scroll = ft.ScrollMode.AUTO

    # Setup routing

    game_data = GameData.load()
    page.add(
        ft.Row(
            controls=[
                SideBarControl(),
                # ft.VerticalDivider(
                #     width=20,
                #     color=ft.colors.RED,
                #     thickness=3,
                # ),
                # GameDataSwitcher(game_data),
                AttributeTable(page=page),
            ]
        )
    )

    # Routing(
    #     page=page,  # Here you have to pass the page. Which will be found as a parameter in all your views
    #     app_routes=app_routes,  # Here a list has to be passed in which we have defined app routing like app_routes
    # )
    # page.go(page.route)

    page.update()


ft.app(target=main)
