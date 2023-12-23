import os

import app.core.styles as styles
import flet as ft


class FileChip(ft.UserControl):
    def __init__(
        self,
        file_name,
        file_bytes: bytes,
        delete_handler,
        knowledge_base_name: str,
        loaded: bool = False,
    ):
        super().__init__()
        self.file_name = file_name
        self.file_bytes = file_bytes
        self.delete_handler = delete_handler
        self.knowledge_base_name = knowledge_base_name
        self.loaded = loaded

    def build(self):
        file_info = self.truncate_file_name(self.file_name)
        file_text_widget = ft.Text(
            file_info,
            tooltip=f"{self.file_name} (Size: {self.bytes_to_human_readable(len(self.file_bytes))} bytes)",  # noqa
            **styles.FilePickerFileStyle().to_dict(),
        )

        return ft.Chip(
            bgcolor=styles.ColorPalette.BG_SECONDARY,
            delete_icon_color=styles.ColorPalette.ACCENT_STOP,
            delete_icon_tooltip=f"Remove file: {self.file_name}",
            label=file_text_widget,
            leading=ft.Row(
                controls=[
                    ft.Icon(
                        ft.icons.CHECK_OUTLINED,
                        color=styles.ColorPalette.ACCENT_SUCCESS
                        if self.loaded
                        else styles.ColorPalette.TEXT_SECONDARY_DEFAULT,  # noqa
                        size=16,
                    ),
                ]
            ),
            on_delete=lambda e: self.delete_handler(
                e, self.knowledge_base_name, self.file_name
            ),
        )

    def bytes_to_human_readable(self, num_bytes: float) -> str:
        for unit in ["bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]:
            if abs(num_bytes) < 1024.0:
                return f"{num_bytes:3.1f} {unit}"
            num_bytes /= 1024.0
        return f"{num_bytes:.1f} YB"

    def truncate_file_name(self, file_name: str, max_length: int = 40) -> str:
        # get base name of file
        file_name = os.path.basename(file_name)
        return (
            (file_name[:max_length] + "...")
            if len(file_name) > max_length
            else file_name
        )
