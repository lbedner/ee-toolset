import flet as ft
from icecream import ic

from app.models.game_data import Unit


class UnitDataApp(ft.UserControl):
    def __init__(self, unit_data: list[Unit]):
        super().__init__()
        self.unit_data = unit_data

    def build(self):
        # controls = [
        #     ft.Text(
        #         "Units", weight=ft.FontWeight.BOLD, style=ft.TextThemeStyle.LABEL_LARGE
        #     ),
        #     ft.GridView(
        #         expand=1,
        #         runs_count=5,
        #         max_extent=150,
        #         child_aspect_ratio=1.0,
        #         spacing=5,
        #         run_spacing=5,
        #         controls=[
        #             ft.Card(
        #                 content=ft.Container(
        #                     content=ft.Column(
        #                         controls=[
        #                             ft.Text(
        #                                 f"{unit.FirstName} {unit.LastName}",
        #                                 style=ft.TextThemeStyle.LABEL_LARGE,
        #                                 weight=ft.FontWeight.BOLD,
        #                             ),
        #                             ft.Text(
        #                                 unit.Class, style=ft.TextThemeStyle.LABEL_LARGE
        #                             ),
        #                             ft.Text(
        #                                 f"Level {int(unit.Attributes.LEVEL)}",
        #                                 style=ft.TextThemeStyle.LABEL_LARGE,
        #                             ),
        #                             ft.Text(
        #                                 unit.Type, style=ft.TextThemeStyle.LABEL_LARGE
        #                             ),
        #                         ]
        #                     ),
        #                     width=200,
        #                     padding=ft.Padding(10, 10, 10, 10),
        #                     on_click=lambda e, unit=unit: self.show_unit_info_alert_dialog(
        #                         unit
        #                     ),
        #                 )
        #             )
        #             for unit in self.unit_data
        #         ],
        #     ),
        # ]
        # return ft.Column(controls=controls)

        controls = []
        controls.append(
            ft.Text(
                "Units",
                weight=ft.FontWeight.BOLD,
                style=ft.TextThemeStyle.LABEL_LARGE,
            )
        )

        for unit in self.unit_data:
            card = ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                f"{unit.FirstName} {unit.LastName}",
                                style=ft.TextThemeStyle.LABEL_LARGE,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                unit.Class,
                                style=ft.TextThemeStyle.LABEL_LARGE,
                            ),
                            ft.Text(
                                f"Level {int(unit.Attributes.LEVEL)}",
                                style=ft.TextThemeStyle.LABEL_LARGE,
                            ),
                            ft.Text(
                                unit.Type,
                                style=ft.TextThemeStyle.LABEL_LARGE,
                            ),
                        ],
                    ),
                    width=200,
                    padding=ft.Padding(10, 10, 10, 10),
                    on_click=lambda e: self.show_unit_info_alert_dialog(unit),
                )
            )

            controls.append(card)

        return ft.Column(
            controls=controls,
        )

    def show_unit_info_alert_dialog(self, unit: Unit):
        ic(f"Showing info for {unit.FirstName} {unit.LastName}".strip())
        # Create a new AlertDialog
        alert_dialog = ft.AlertDialog(
            # modal=True,
            title=ft.Text(f"{unit.FirstName} {unit.LastName}"),
            content=ft.Text(
                f"Name: {unit.FirstName} {unit.LastName}\n"
                f"Class: {unit.Class}\n"
                f"Level: {int(unit.Attributes.LEVEL)}\n"
                f"Type: {unit.Type}"
            ),
            on_dismiss=lambda e: ic("Modal dialog dismissed!"),
        )

        # Show the AlertDialog
        self.page.show_dialog(alert_dialog)
        self.page.dialog = alert_dialog
        alert_dialog.open = True
        self.update()