import app.core.styles as styles
import flet as ft


class ErrorText(ft.UserControl):
    def __init__(self, text, style=None):
        super().__init__()
        self.text = text
        self.style = style if style else styles.SecondaryTextStyle().to_dict()

    def build(self):
        error_text = ft.Text(value=self.text, **self.style)
        return ft.Container(
            content=error_text,
            padding=10,
            border_radius=10,
            bgcolor="#330000",  # Dark red background color
            border=ft.border.all(0.75, "red"),
        )
