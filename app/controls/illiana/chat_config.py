import os
import threading

import app.core.styles as styles
import flet as ft
from app.core.config import settings
from app.core.log import logger
from app.models import KnowledgeBase, KnowledgeBaseDocument


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
        self.files_dict: dict[str, bytes] = self.load_knowledge_base_files()
        self.files_container: ft.Container = ft.Container(
            content=self.init_files_container()
        )
        self.loading_indicator = ft.ProgressRing(visible=False)
        self.selected_files = ft.Text(value="No files selected.")
        self.pick_files_dialog = ft.FilePicker(on_result=self.pick_files_result)
        self.page.overlay.append(self.pick_files_dialog)

    def load_knowledge_base_files(self) -> dict[str, bytes]:
        logger.debug("knowledge.load")
        knowledge_base = KnowledgeBase.load()

        files_dict: dict[str, bytes] = {}
        for key, document in knowledge_base.root.items():
            try:
                with open(document.Filepath, "rb") as file:
                    logger.debug(
                        "knowledge.load_file.success", key=key, document=document
                    )
                    files_dict[key] = file.read()
            except FileNotFoundError:
                logger.warning(
                    "knowledge.load_file.failure", document=document.Filepath
                )
            except IOError as e:
                logger.error(
                    "knowledge.load_file.failure", document=document.Filepath, e=e
                )
        return files_dict

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
        # get base name of file
        file_name = os.path.basename(file_name)
        return (
            (file_name[:max_length] + "...")
            if len(file_name) > max_length
            else file_name
        )

    def on_llm_selection_change(self, event: ft.ControlEvent):
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
            "The Language Model (LLM) is the model that Illiana uses to generate responses. "  # noqa
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

            knowledge_base = KnowledgeBase.load()
            for uploaded_file in e.files:
                uploaded_file_path = uploaded_file.path
                uploaded_file_basename = os.path.basename(uploaded_file_path)
                knowledge_base_file_path = f"{settings.VECTORSTORE_KNOWLEDGE_BASE_DIR}/{uploaded_file_basename}"  # noqa

                logger.debug(
                    "knowledge_base.process", uploaded_file_path=uploaded_file_path
                )

                with open(uploaded_file_path, "rb") as f:
                    with open(knowledge_base_file_path, "wb") as f2:
                        logger.debug(
                            "knowledge_base.add",
                            knowledge_base_file_path=knowledge_base_file_path,  # noqa
                        )
                        self.files_dict[uploaded_file_basename] = f.read()
                        f2.write(self.files_dict[uploaded_file_basename])
                        knowledge_base.add(
                            uploaded_file_basename,
                            KnowledgeBaseDocument(
                                Type="Document",
                                Filepath=knowledge_base_file_path,
                                Size=len(self.files_dict[uploaded_file_basename]),
                                Loaded=False,
                            ),
                        )
                        knowledge_base.dump()

            self.update_files_container()
            self.loading_indicator.visible = False
            self.update()
        else:
            self.selected_files.value = "No files selected or upload cancelled."
            self.update_files_container()
            self.selected_files.update()

    def save_file_to_disk(self, uploaded_file):
        file_path = "path/to/save/" + uploaded_file.name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.content)  # Assuming the file's content is available
        return file_path

    def delete_file_from_disk(self, file_path):
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.debug("knowledge.delete_file.success", file_path=file_path)
            else:
                logger.warning("knowledge.delete_file.no_file", file_path=file_path)
        except PermissionError:
            logger.error(f"Permission denied: unable to delete {file_path}.")
        except OSError as e:
            logger.error(f"Error occurred: {e}")

    def delete_file(self, e: ft.ControlEvent, file_name: str):
        knowledge_base = KnowledgeBase.load()
        knowledge_base_document = knowledge_base.root[file_name]
        logger.debug(
            "knowledge.delete",
            knowledge_base_document=knowledge_base_document,
            file_name=file_name,
        )
        knowledge_base.remove(file_name)
        self.delete_file_from_disk(knowledge_base_document.Filepath)
        del self.files_dict[file_name]
        self.update_files_container()

    def init_files_container(self) -> ft.Column:
        files_text_widgets = []

        for file_name, file_bytes in self.files_dict.items():
            file_info = self.truncate_file_name(file_name)
            file_text_widget = ft.Text(
                file_info,
                tooltip=f"{file_name} (Size: {self.bytes_to_human_readable(len(file_bytes))} bytes)",  # noqa
                **styles.FilePickerFileStyle().to_dict(),
            )

            logger.debug("knowledge_base.chip_creation", file_name=file_name)
            file_row = ft.Chip(
                bgcolor=styles.ColorPalette.BG_SECONDARY,
                delete_icon_color=styles.ColorPalette.ACCENT_STOP,
                delete_icon_tooltip=f"Remove file: {file_name}",
                label=file_text_widget,
                leading=ft.Icon(
                    ft.icons.INSERT_DRIVE_FILE_OUTLINED,
                    color=styles.ColorPalette.TEXT_SECONDARY_DEFAULT,
                    size=16,
                ),
                on_delete=lambda e, fn=file_name: self.delete_file(e, fn),
            )

            files_text_widgets.append(file_row)

        return ft.Column(files_text_widgets, spacing=5)

    def update_files_container(self):
        self.files_container.content = self.init_files_container()
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
                    self.temperature_slider,
                    MaximumLengthSlider(),
                    ft.Row(
                        controls=[
                            ft.Text(
                                "Knowledge",
                                **styles.SliderLabelStyle().to_dict(),
                                tooltip="Upload files that contain knowledge that Illiana can use to generate responses.",  # noqa
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
                ],
                scroll=ft.ScrollMode.AUTO,
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
            tooltip="""Controls randomness: Lowering results in less random\ncompletions. As the temperature approaches zero, the\nmodel will become deterministic and repetitive. Higher\ntemperature nresults in more random completions.""",  # noqa
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
            tooltip="""Controls the maximum number of tokens that the\ncompletion may contain. Tokens are roughly equal to\nwords.""",  # noqa
        )

    def slider_changed(self, event: ft.ControlEvent):
        self.text_value.value = int(event.control.value)
        self.update()
