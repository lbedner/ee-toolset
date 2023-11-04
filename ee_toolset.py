import flet as ft

from app.controls import AppBar
import app.core.constants as constants
from app.core.log import logger, ic
import app.core.styles as styles
from app.core.routing import ROUTE_TO_VIEW


def main(page: ft.Page):
    logger.info("main", page=page)
    page.window_height = constants.PAGE_WINDOW_HEIGHT
    page.window_width = constants.PAGE_WINDOW_WIDTH
    page.bgcolor = styles.ColorPalette.BG_PRIMARY
    page.appbar = AppBar(page=page).build()
    page.title = constants.PAGE_TITLE
    page.scroll = ft.ScrollMode.AUTO

    # Setup routing

    def route_change(route):
        ic(f"route_change: {page.route}")
        page.views.clear()
        view_class = ROUTE_TO_VIEW.get(page.route)
        if view_class:
            page.views.append(
                view_class(page=page).create_view(),
            )
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)

    page.update()


ft.app(target=main)
