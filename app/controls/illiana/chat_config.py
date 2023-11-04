import flet as ft
import threading

from app.core.config import settings
from app.core.log import logger, ic
import flet as ft
import app.core.styles as styles


class ChatConfig(ft.UserControl):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.llm_title = ft.Text(
            "",
            color=styles.ColorPalette.TEXT_PRIMARY_DEFAULT,
            font_family=styles.FontConfig.FAMILY_PRIMARY,
            size=styles.FontConfig.SIZE_PRIMARY,
            weight=ft.FontWeight.W_700,
        )
        self.llm_description = ft.Text(
            "",
            color=styles.ColorPalette.TEXT_SECONDARY_DEFAULT,
            font_family=styles.FontConfig.FAMILY_PRIMARY,
            size=styles.FontConfig.SIZE_SECONDARY,
            weight=ft.FontWeight.W_400,
        )
        self.llm_context_window = ft.TextField(
            "",
            color=styles.ColorPalette.TEXT_SECONDARY_DEFAULT,
            # font_family=styles.FontConfig.FAMILY_PRIMARY,
            # size=styles.FontConfig.SIZE_SECONDARY,
            # weight=ft.FontWeight.W_400,
            label="Context Window",
            read_only=True,
        )
        self.llm_training_data = ft.Text(
            "",
            color=styles.ColorPalette.TEXT_SECONDARY_DEFAULT,
            font_family=styles.FontConfig.FAMILY_PRIMARY,
            size=styles.FontConfig.SIZE_SECONDARY,
            weight=ft.FontWeight.W_400,
        )
        self.temperature_slider = TemperatureSlider()
        self.files_dict: dict[str, bytes] = {}
        self.files_container = ft.Container()
        self.loading_indicator = ft.ProgressRing(visible=False)
        self.selected_files = ft.Text(value="No files selected.")
        self.pick_files_dialog = ft.FilePicker(on_result=self.pick_files_result)
        self.page.overlay.append(self.pick_files_dialog)

    def bytes_to_human_readable(self, num_bytes):
        """
        Convert bytes to a human-readable format.
        :param num_bytes: Number of bytes.
        :return: Human-readable string.
        """
        for unit in ["bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]:
            if abs(num_bytes) < 1024.0:
                return f"{num_bytes:3.1f} {unit}"
            num_bytes /= 1024.0
        return f"{num_bytes:.1f} YB"

    def truncate_file_name(self, file_name, max_length=25):
        """
        Truncate a file name if it's longer than max_length.
        :param file_name: The name of the file.
        :param max_length: Maximum length of the file name.
        :return: Truncated file name with ellipsis if needed.
        """
        return (
            (file_name[:max_length] + "...")
            if len(file_name) > max_length
            else file_name
        )

    def on_llm_selection_change(self, event: ft.ControlEvent):
        ic(event.control.value)
        selected_llm = event.control.value

        if selected_llm:
            self.update_llm_values(selected_llm)
            self.update()

    def update_llm_values(self, selected_llm):
        self.llm_title.value = settings.LLMS[selected_llm]["title"]
        self.llm_description.value = settings.LLMS[selected_llm]["description"]
        self.llm_context_window.value = settings.LLMS[selected_llm]["content_window"]
        self.llm_training_data.value = settings.LLMS[selected_llm]["training_data"]

    def get_llm_dropdown(self):
        llm_names = list(settings.LLMS.keys())
        llm_dropdown = ft.Dropdown(
            options=[ft.dropdown.Option(name) for name in llm_names],
            label="LLM Selection",
            width=260,
            height=50,
            hint_text="Select an LLM for Illiana to use.",
            bgcolor=styles.ColorPalette.BG_SECONDARY,
            border_width=1,
            border_color="#444444",
            border_radius=10,
            color=styles.ColorPalette.TEXT_PRIMARY_DEFAULT,
            # font_family=styles.FontConfig.FAMILY_PRIMARY,
            text_size=styles.FontConfig.SIZE_SECONDARY,
            on_change=lambda event: self.on_llm_selection_change(event),
            focused_border_color=styles.ColorPalette.ACCENT,
            focused_border_width=2,
        )
        llm_dropdown.value = "gpt-3.5-turbo-1106"
        self.update_llm_values("gpt-3.5-turbo-1106")
        return llm_dropdown

    def get_llm_description(self):
        return ft.Text(
            "The Language Model (LLM) is the model that Illiana uses to generate responses. "
            "You can select the LLM that Illiana uses to generate responses here.",
            color=styles.ColorPalette.TEXT_SECONDARY_DEFAULT,
            font_family=styles.FontConfig.FAMILY_PRIMARY,
            size=styles.FontConfig.SIZE_SECONDARY,
            weight=ft.FontWeight.W_400,
        )

    def pick_files_result(self, e: ft.FilePickerResultEvent):
        threading.Thread(target=self.process_files, args=(e,), daemon=True).start()

    def process_files(self, e: ft.FilePickerResultEvent):
        if e.files:
            self.loading_indicator.visible = True
            self.update()

            for uploaded_file in e.files:
                file_path = uploaded_file.path
                file_bytes = open(file_path, "rb").read()
                self.files_dict[uploaded_file.name] = file_bytes

            self.update_files_container()
            self.loading_indicator.visible = False
            self.update()
        else:
            self.selected_files.value = "No files selected or upload cancelled."
            self.update_files_container()
            self.selected_files.update()

    def delete_file(self, e: ft.ControlEvent, file_name: str):
        del self.files_dict[file_name]
        self.update_files_container()

    def update_files_container(self):
        files_text_widgets = []

        for file_name, file_bytes in self.files_dict.items():
            file_info = self.truncate_file_name(file_name)
            file_text_widget = ft.Text(
                file_info,
                tooltip=f"{file_name} (Size: {self.bytes_to_human_readable(len(file_bytes))} bytes)",
                **styles.FilePickerFileStyle().to_dict(),
            )

            file_row = ft.Chip(
                bgcolor=styles.ColorPalette.BG_SECONDARY,
                delete_icon_color=styles.ColorPalette.ACCENT_STOP,
                delete_icon_tooltip="Remove file",
                label=file_text_widget,
                leading=ft.Icon(
                    ft.icons.INSERT_DRIVE_FILE_OUTLINED,
                    color=styles.ColorPalette.TEXT_SECONDARY_DEFAULT,
                    size=16,
                ),
                on_delete=lambda e: self.delete_file(e, file_name),
            )

            files_text_widgets.append(file_row)

        self.files_container.content = ft.Column(files_text_widgets, spacing=5)
        self.files_container.update()

    def build(self):
        self.llm_dropdown = self.get_llm_dropdown()
        return ft.Container(
            width=300,
            height=1000,
            border_radius=15,
            padding=15,
            alignment=ft.alignment.top_center,
            bgcolor=styles.ColorPalette.BG_SECONDARY,
            border=ft.border.all(2, "#444444"),
            content=ft.Column(
                controls=[
                    self.llm_dropdown,
                    # self.get_llm_description(),
                    # self.llm_title,
                    # self.llm_context_window,
                    self.temperature_slider,
                    MaximumLengthSlider(),
                    ft.Row(
                        controls=[
                            ft.Text(
                                "Knowledge",
                                **styles.SliderLabelStyle().to_dict(),
                                tooltip="Upload files that contain knowledge that Illiana can use to generate responses.",
                            ),
                            ft.IconButton(
                                icon=ft.icons.ADD_CIRCLE_OUTLINE_OUTLINED,
                                on_click=lambda _: self.pick_files_dialog.pick_files(
                                    allow_multiple=True,
                                    allowed_extensions=[
                                        "txt",
                                        "pdf",
                                        "docx",
                                        "doct",
                                        "html",
                                        "htm",
                                        "rtf",
                                    ],
                                ),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    self.loading_indicator,
                    ft.Divider(),
                    self.files_container,
                ]
            ),
        )


class Slider(ft.UserControl):
    def __init__(self, label: str, min_value: int, max_value: int, tooltip: str = None):
        super().__init__()
        self.text_value = ft.Text(
            value=str(min_value), **styles.SliderValueStyle().to_dict()
        )
        self.slider = ft.Slider(
            value=min_value,
            min=min_value,
            max=max_value,
            divisions=max_value - min_value,
            height=50,
            width=300,
            thumb_color=styles.ColorPalette.ACCENT,
            on_change=lambda event: self.slider_changed(event),
            tooltip=tooltip,
        )
        self.label = label

    def build(self):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(self.label, **styles.SliderLabelStyle().to_dict()),
                            self.text_value,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    self.slider,
                ],
            ),
        )


class TemperatureSlider(Slider):
    def __init__(self):
        super().__init__(
            label="Temperature",
            min_value=0.0,
            max_value=1.0,
            tooltip="""Controls randomness: Lowering results in less random\ncompletions. As the temperature approaches zero, the\nmodel will become deterministic and repetitive. Higher\ntemperature nresults in more random completions.""",
        )

    def slider_changed(self, event: ft.ControlEvent):
        self.text_value.value = str(round(event.control.value, 2))
        self.update()


class MaximumLengthSlider(Slider):
    def __init__(self):
        super().__init__(
            label="Maximum length",
            min_value=1,
            max_value=4096,
            tooltip="""Controls the maximum number of tokens that the\ncompletion may contain. Tokens are roughly equal to\nwords.""",
        )

    def slider_changed(self, event: ft.ControlEvent):
        self.text_value.value = int(event.control.value)
        self.update()
