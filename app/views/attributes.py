import flet as ft
from app.controls.attributes.attribute_table import AttributeTable
from app.core.constants import ATTRIBUTES_ROUTE

from .view import BaseView


class AttributesView(BaseView):
    def __init__(self, page: ft.Page):
        super().__init__(
            page=page,
            route=ATTRIBUTES_ROUTE,
            main_control=AttributeTable(page=page),
        )
