import flet as ft

from app.controls.game_data import GameDataSwitcher
from app.models.game_data import GameData


def main(page: ft.Page):
    page.window_height = 600
    page.window_width = 800

    page.appbar = ft.AppBar(
        leading=ft.Icon(ft.icons.SAVE_OUTLINED),
        leading_width=40,
        title=ft.Text("Eternal Engine Toolset"),
        center_title=False,
        bgcolor=ft.colors.SURFACE_VARIANT,
    )

    page.title = "Eternal Engine Toolset"

    page.scroll = ft.ScrollMode.ALWAYS

    page.add(ft.Text("Save Game Editor", style=ft.TextThemeStyle.HEADLINE_SMALL))

    game_data: GameData = GameData.load()
    game_data_switcher = GameDataSwitcher(game_data)
    page.add(game_data_switcher)

    page.update()


ft.app(target=main)
