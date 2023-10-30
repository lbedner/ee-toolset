import flet as ft
from flet_route import Params, Basket

from app.core.constants import ATTRIBUTES_ROUTE, ATTRIBUTES_VIEW, INDEX_ROUTE
from app.models import GameData
from ..controls import GameDataSwitcher


def IndexView(page: ft.Page, params: Params, basket: Basket):
    return ft.View(
        INDEX_ROUTE,
        auto_scroll=True,
        controls=[
            # SideBarControl(),
            ft.ElevatedButton(
                ATTRIBUTES_VIEW, on_click=lambda _: page.go(ATTRIBUTES_ROUTE)
            ),
            GameDataSwitcher(GameData.load()),
        ],
    )
