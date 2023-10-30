import flet as ft

import app.core.styles as styles


class SuccessSnackBar(ft.UserControl):
    def __init__(self, message: str):
        super().__init__()
        self.message = message

    def build(self):
        return ft.SnackBar(
            bgcolor=styles.ColorPalette.ACCENT_SUCCESS,
            content=ft.Text(
                self.message,
                font_family=styles.FontConfig.FAMILY_PRIMARY,
                size=styles.FontConfig.SIZE_PRIMARY,
                weight=ft.FontWeight.W_500,
                color=ft.colors.BLACK,
            ),
            duration=5000,
            show_close_icon=True,
            width=600,
        )
