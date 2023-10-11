import flet as ft
from flet_route import Params, Basket

from ..controls.attributes.attribute_table import AttributeTable


def AttributesView(page: ft.Page, params: Params, basket: Basket):
    return ft.View(
        "/attributes",
        controls=[
            ft.ElevatedButton("Save Game Editor", on_click=lambda _: page.go("/")),
            ft.Text("attributes"),
            AttributeTable(page=page),
        ],
    )
