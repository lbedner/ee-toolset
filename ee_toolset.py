from typing import Optional

import app.core.constants as constants
import app.core.styles as styles
import flet as ft
from app.controls import AppBar
from app.core.log import logger
from app.core.routing import ROUTE_TO_VIEW
from app.views import BaseView


def main(page: ft.Page):
    logger.info("Starting up EE Toolset...", page=page)
    page.window_height = constants.PAGE_WINDOW_HEIGHT
    page.window_width = constants.PAGE_WINDOW_WIDTH
    page.bgcolor = styles.ColorPalette.BG_PRIMARY
    page.appbar = AppBar(page=page).build()
    page.title = constants.PAGE_TITLE
    # page.scroll = ft.ScrollMode.AUTO
    # page.window_full_screen = True
    page.window_maximized = True
    # page.theme = ft.Theme(page_transitions=ft.PageTransitionTheme.NONE)

    # Dictionary to cache views
    cached_views = {}

    def route_change(route_change_event: ft.RouteChangeEvent):
        logger.debug(f"route_change: {route_change_event}")
        route = route_change_event.route
        cached_view: Optional[BaseView] = None
        if route not in cached_views:
            logger.debug(f"route_change: {route} not cached. Caching now...")
            view_class = ROUTE_TO_VIEW.get(route)
            if view_class:
                cached_view = view_class(page=page).create_view()
                cached_views[route] = cached_view
            else:
                logger.error(f"route_change: {route} not found in ROUTE_TO_VIEW")
        else:
            logger.debug(f"route_change: {route} already cached")
            cached_view = cached_views[route]

        page.views.clear()
        page.views.append(cached_view)
        page.update()

    def view_pop(view_pop_event: ft.ViewPopEvent):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(constants.ILLIANA_ROUTE)

    page.update()
    logger.info("EE Toolset started!", page=page)


ft.app(target=main)
