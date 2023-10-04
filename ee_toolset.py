import flet as ft

from app.controls import GameDataSwitcher, SideBarControl
import app.core.constants as constants
from app.core.log import logger
from app.models import GameData


def main(page: ft.Page):
    logger.info("main", page=page)
    page.window_height = 1200
    page.window_width = 1600

    page.appbar = ft.AppBar(
        leading_width=40,
        title=ft.Text(constants.PAGE_TITLE),
        center_title=False,
        bgcolor=ft.colors.SURFACE_VARIANT,
    )
    page.title = constants.PAGE_TITLE
    page.scroll = ft.ScrollMode.AUTO

    game_data: GameData = GameData.load()
    page.add(
        ft.Row(
            controls=[
                SideBarControl(),
                ft.VerticalDivider(
                    width=20,
                    color=ft.colors.RED,
                    thickness=3,
                ),
                GameDataSwitcher(game_data),
            ]
        )
    )

    page.update()


ft.app(target=main)
