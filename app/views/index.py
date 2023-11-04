import flet as ft

from app.core.constants import INDEX_ROUTE
from app.models import GameData
from ..controls import GameDataSwitcher
from .view import BaseView


class IndexView(BaseView):
    def __init__(self, page: ft.Page):
        super().__init__(page, INDEX_ROUTE, GameDataSwitcher(GameData.load()))
