import flet as ft
from app.controls.unit_data import UnitDataApp
from app.models.game_data import GameData
from flet import ControlEvent


class GameDataSwitcher(ft.UserControl):
    def __init__(self, game_data: GameData):
        super().__init__()
        self.game_data = game_data
        self.game_data_app = GameDataApp(game_data)
        self.raw_game_data_control = RawGameDataControl(game_data)

    def on_switch(self, e: ControlEvent):
        if self.raw_game_data_control.visible:
            self.raw_game_data_control.visible = False
            self.game_data_app.visible = True
        else:
            self.raw_game_data_control.visible = True
            self.game_data_app.visible = False
        self.update()

    def build(self):
        title = ft.Text(
            "Save Game Editor",
            style=ft.TextThemeStyle.HEADLINE_SMALL,
        )
        switch = ft.Switch(
            value=True, label="Format Game Data", on_change=self.on_switch
        )
        return ft.Column(
            controls=[
                title,
                switch,
                self.game_data_app,
                self.raw_game_data_control,
            ]
        )


class RawGameDataControl(ft.UserControl):
    def __init__(self, game_data: GameData):
        super().__init__()
        self.game_data = game_data
        self.visible = False

    def build(self):
        controls = []
        controls.append(ft.Text(self.game_data.dump()))
        return ft.Column(controls=controls)


class GameDataApp(ft.UserControl):
    def __init__(self, game_data: GameData):
        super().__init__()
        self.game_data = game_data
        self.visible = True

    def get_root_level_key_value_pairs(self, data: dict) -> dict:
        key_value_pairs = {}
        for key, value in data.items():
            if isinstance(value, dict) or isinstance(value, list):
                continue
            else:
                key_value_pairs[key] = value
        return key_value_pairs

    def build(self):
        # Extract the root level key value pairs of the game data
        core_data: dict = self.get_root_level_key_value_pairs(
            self.game_data.model_dump()
        )
        controls = []

        controls.append(ft.Divider())
        controls.append(
            ft.Text(
                "Core Data",
                weight=ft.FontWeight.BOLD,
                style=ft.TextThemeStyle.LABEL_LARGE,
            )
        )
        for key, value in core_data.items():
            controls.append(
                ft.TextField(
                    label=key,
                    value=value,
                    read_only=True,
                    border_color=ft.colors.BLUE,
                )
            )
        controls.append(ft.Divider())
        unit_data_app = UnitDataApp(self.game_data.units)
        controls.append(unit_data_app)

        # Return a column with the text fields
        return ft.Column(
            controls=controls,
        )
