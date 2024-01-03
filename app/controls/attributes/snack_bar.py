import app.core.styles as styles
import flet as ft


class SuccessSnackBar(ft.UserControl):
    def __init__(
        self,
        message: str,
        page: ft.Page,
        duration_ms: int = 5000,
        show_close_icon: bool = True,
        width: int = 600,
    ):
        super().__init__()
        self.message = message
        self.page = page
        self.duration_ms = duration_ms
        self.show_close_icon = show_close_icon
        self.width = width

    def open(self):
        self.page.snack_bar = self.build()
        self.page.snack_bar.open = True
        self.page.update()

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
            duration=self.duration_ms,
            show_close_icon=self.show_close_icon,
            width=self.width,
        )
