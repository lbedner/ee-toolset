import app.core.styles as styles
import flet as ft
from app.controls.attributes.buttons import (
    ElevatedAddButton,
    ElevatedCancelButton,
    ElevatedDeleteButton,
)
from app.controls.attributes.snack_bar import SuccessSnackBar
from app.controls.illiana.chip import FileChip
from app.controls.illiana.dropdown import DropdownControl
from app.controls.illiana.file_picker import FilePickerControl
from app.controls.illiana.slider import MaximumLengthSlider, TemperatureSlider
from app.core.config import settings
from app.models import KnowledgeBase, KnowledgeBaseDocument, KnowledgeBaseHelper


class AlertDialogControl(ft.AlertDialog):
    def __init__(
        self,
        title: ft.Control,
        content: ft.Control,
        on_dismiss=None,
        actions: list[ft.Control] = [],
    ):
        super().__init__()
        self.title = title
        self.content = content
        self.on_dismiss = on_dismiss if on_dismiss else lambda e: None
        self.actions = actions

    def show(self, page: ft.Page):
        page.show_dialog(self)
        page.dialog = self
        self.open = True
        page.update()


class ChatConfig(ft.UserControl):
    """
    Represents the configuration settings for the chat feature in the application.

    Args:
        page (ft.Page): The page where the chat configuration is used.

    Attributes:
        page (ft.Page): The page where the chat configuration is used.
        llm_context_window (ft.TextField): The text field for the context window.
        temperature_slider (TemperatureSlider): The temperature slider control.
        knowledge_base (KnowledgeBase): The knowledge base object.
        knowledge_base_helper (KnowledgeBaseHelper): The helper class for the knowledge base.
        loading_indicator (ft.ProgressRing): The progress ring control for loading.
        knowledge_base_dropdown (DropdownControl): The dropdown control for selecting the knowledge base.
        file_picker_control (FilePickerControl): The file picker control for selecting files.
        files_container_control (FilesContainerControl): The control for displaying the files container.

    Methods:
        on_llm_selection_change(event: ft.ControlEvent): Event handler for LLM selection change.
        on_knowledge_base_selection_change(event: ft.ControlEvent): Event handler for knowledge base selection change.
        update_llm_values(selected_llm): Updates the values for the selected LLM.
        get_llm_dropdown() -> DropdownControl: Returns the dropdown control for LLM selection.
        get_knowledge_base_dropdown() -> DropdownControl: Returns the dropdown control for knowledge base selection.
        on_files_processed(document_data: dict[str, bytes]): Event handler for files processed.
        delete_file(e: ft.ControlEvent, knowledge_base_name: str, document_name: str): Deletes a file from the knowledge base.
        on_click_close_dialog(): Event handler for closing the dialog.
        on_add_new_knowledge_base(): Event handler for adding a new knowledge base.
        add_new_knowledge_base(knowledge_base_name: str): Adds a new knowledge base.
        build() -> ft.Container: Builds and returns the chat configuration container.
    """  # noqa

    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.llm_context_window = ft.TextField(
            "",
            color=styles.ColorPalette.TEXT_SECONDARY_DEFAULT,
            label="Context Window",
            read_only=True,
        )
        self.temperature_slider = TemperatureSlider()
        self.knowledge_base = KnowledgeBase.load()
        self.knowledge_base_helper = KnowledgeBaseHelper(self.knowledge_base)
        self.loading_indicator = ft.ProgressRing(visible=False)
        self.knowledge_base_dropdown = self.get_knowledge_base_dropdown()
        self.file_picker_control = FilePickerControl(
            knowledge_base_dropdown=self.knowledge_base_dropdown,
            knowledge_base_helper=self.knowledge_base_helper,
            on_files_processed=self.on_files_processed,
            page=self.page,
        )
        self.page.overlay.append(self.file_picker_control)
        self.files_container_control = FilesContainerControl(
            knowledge_base_dropdown=self.knowledge_base_dropdown,
            knowledge_base_helper=self.knowledge_base_helper,
            file_picker_control=self.file_picker_control,
            delete_file_handler=self.delete_file,
        )

    def on_llm_selection_change(self, event: ft.ControlEvent):
        selected_llm = event.control.value

        if selected_llm:
            self.update_llm_values(selected_llm)
            self.update()

    def on_knowledge_base_selection_change(self, event: ft.ControlEvent):
        selected_knowledge_base = event.control.value

        if selected_knowledge_base:
            self.files_container_control.update_files_container()
            self.update()

    def update_llm_values(self, selected_llm):
        self.llm_context_window.value = settings.LLMS[selected_llm]["content_window"]

    def get_llm_dropdown(self):
        llm_names = list(settings.LLMS.keys())
        return DropdownControl(
            options=llm_names,
            label="LLM Selection",
            width=260,
            on_change=lambda event: self.on_llm_selection_change(event),
            default_value="gpt-3.5-turbo-1106",
            hint_text="Select an LLM for Illiana to use.",
        )

    def get_knowledge_base_dropdown(self) -> DropdownControl:
        knowledge_base_names = list(self.knowledge_base.root.keys())
        return DropdownControl(
            options=knowledge_base_names,
            label="Knowledge Base",
            width=200,
            on_change=lambda event: self.on_knowledge_base_selection_change(event),
            default_value="No knowledge bases"
            if not knowledge_base_names
            else knowledge_base_names[0],
        )

    def on_files_processed(self, document_data: dict[str, bytes]):
        self.document_data = document_data
        self.files_container_control.update_files_container()

    def delete_file(
        self, e: ft.ControlEvent, knowledge_base_name: str, document_name: str
    ):
        self.knowledge_base_helper.delete_document(knowledge_base_name, document_name)
        self.files_container_control.update_files_container()

    def on_click_close_dialog(self):
        self.page.dialog.open = False
        self.page.update()

    def on_add_new_knowledge_base(self):
        knowledge_base_name_field = ft.TextField(
            border_radius=15,
            label="Knowledge Base Name",
            width=480,
            height=70,
            bgcolor=styles.ColorPalette.BG_SECONDARY,
            border=ft.border.all(2, "#444444"),
            hint_text="Add a name for your new knowledge base.",
            text_size=styles.FontConfig.SIZE_SECONDARY,
        )

        def add_button_click():
            knowledge_base_name = knowledge_base_name_field.value
            self.add_new_knowledge_base(knowledge_base_name)
            self.page.dialog.open = False
            self.page.update()

        alert_dialog = AlertDialogControl(
            title=ft.Text("Add New Knowledge Base", **styles.ModalTitle().to_dict()),
            content=knowledge_base_name_field,
            actions=[
                ElevatedCancelButton(self.on_click_close_dialog),
                ElevatedAddButton(add_button_click),
            ],
        )
        alert_dialog.show(self.page)

    def add_new_knowledge_base(self, knowledge_base_name: str):
        self.knowledge_base_helper.add_new_knowledge_base(knowledge_base_name)
        self.knowledge_base_dropdown.add_option(knowledge_base_name, set_selected=True)
        self.page.snack_bar = SuccessSnackBar(
            message=f"Successfully added knowledge base: {knowledge_base_name}",
        ).build()
        self.page.snack_bar.open = True
        self.page.update()
        self.update()
        self.files_container_control.update_files_container()

    def on_delete_knowledge_base(self, knowledge_base_name: str):
        def delete_button_click():
            self.delete_knowledge_base(knowledge_base_name)
            self.page.dialog.open = False
            self.page.update()

        # Retrieve the knowledge base
        try:
            knowledge_base: dict[
                str, KnowledgeBaseDocument
            ] = self.knowledge_base_helper.get_knowledge_base(knowledge_base_name)
        except KeyError:
            # Handle the case where the knowledge base doesn't exist
            # You can log this error or show a message to the user
            return

        # Format the document list string
        document_count = len(knowledge_base.keys())
        document_list_str = "\n".join(
            [f"- {doc_name}" for doc_name in knowledge_base.keys()]
        )

        # Create the confirmation message
        confirmation_message = ft.Text(
            f"Are you sure you want to delete {knowledge_base_name} and the following {document_count} document(s):\n\n{document_list_str}",  # noqa
            **styles.ModalSubtitle().to_dict(),
        )

        # Set up the alert dialog
        alert_dialog = AlertDialogControl(
            title=ft.Text("Delete Knowledge Base", **styles.ModalTitle().to_dict()),
            content=confirmation_message,
            actions=[
                ElevatedCancelButton(self.on_click_close_dialog),
                ElevatedDeleteButton(delete_button_click),
            ],
        )
        alert_dialog.show(self.page)

    def delete_knowledge_base(self, knowledge_base_name: str):
        knowledge_base_name = self.knowledge_base_dropdown.dropdown.value
        self.knowledge_base_helper.delete_knowledge_base(knowledge_base_name)
        self.knowledge_base_dropdown.remove_option(knowledge_base_name)
        self.page.snack_bar = SuccessSnackBar(
            message=f"Successfully deleted knowledge base: {knowledge_base_name}",
        ).build()
        self.page.snack_bar.open = True
        self.page.update()
        self.update()
        self.files_container_control.update_files_container()

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
                    ft.Divider(),
                    ft.Row(
                        controls=[
                            self.knowledge_base_dropdown,
                            ft.IconButton(
                                icon=ft.icons.ADD_CIRCLE_OUTLINE_OUTLINED,
                                on_click=lambda _: self.on_add_new_knowledge_base(),
                            ),
                            ft.IconButton(
                                icon=ft.icons.DELETE_OUTLINE_ROUNDED,
                                on_click=lambda _: self.on_delete_knowledge_base(
                                    self.knowledge_base_dropdown.dropdown.value
                                ),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    self.loading_indicator,
                    ft.Divider(),
                    self.files_container_control,
                ],
                scroll=ft.ScrollMode.AUTO,
            ),
        )


class FilesContainerControl(ft.UserControl):
    """
    A control that displays a container of files related to a knowledge base.

    Args:
        knowledge_base_helper (KnowledgeBaseHelper): An instance of the KnowledgeBaseHelper class.
        file_picker_control (FilePickerControl): An instance of the FilePickerControl class.
        knowledge_base_dropdown (DropdownControl): An instance of the DropdownControl class.
        delete_file_handler: A handler function for deleting a file.

    Attributes:
        knowledge_base_helper (KnowledgeBaseHelper): An instance of the KnowledgeBaseHelper class.
        file_picker_control (FilePickerControl): An instance of the FilePickerControl class.
        knowledge_base_dropdown (DropdownControl): An instance of the DropdownControl class.
        delete_file_handler: A handler function for deleting a file.
        container (ft.Container): The container that holds the files.

    Methods:
        get_knowledge_base_name: Returns the selected knowledge base name.
        update_files_container: Updates the files container with the latest files.
        build: Builds and returns the container.

    """  # noqa

    def __init__(
        self,
        knowledge_base_helper: KnowledgeBaseHelper,
        file_picker_control: FilePickerControl,
        knowledge_base_dropdown: DropdownControl,
        delete_file_handler,
    ):
        super().__init__()
        self.knowledge_base_helper = knowledge_base_helper
        self.file_picker_control = file_picker_control
        self.knowledge_base_dropdown = knowledge_base_dropdown
        self.delete_file_handler = delete_file_handler
        self.container = ft.Container()

    def get_knowledge_base_name(self):
        """
        Returns the selected knowledge base name.

        Returns:
            str: The selected knowledge base name.
        """
        return self.knowledge_base_dropdown.dropdown.value

    def update_files_container(self):
        """
        Updates the files container with the latest files.
        """
        knowledge_base_name = self.get_knowledge_base_name()
        files_text_widgets: list[FileChip] = []
        if knowledge_base_name in self.knowledge_base_helper.document_data:
            files_text_widgets = [
                FileChip(
                    file_name=file_name,
                    file_bytes=file_bytes,
                    delete_handler=self.delete_file_handler,
                    knowledge_base_name=knowledge_base_name,
                )
                for file_name, file_bytes in self.knowledge_base_helper.document_data[
                    knowledge_base_name
                ].items()
            ]

        add_document_button = ft.Container(
            content=ft.Row(
                controls=[
                    ft.IconButton(
                        icon=ft.icons.ADD_CIRCLE_OUTLINE_OUTLINED,
                        on_click=lambda _: self.file_picker_control.pick_files_dialog.pick_files(  # noqa
                            allow_multiple=True,
                            allowed_extensions=settings.SUPPORTED_DOCUMENTS,
                        ),
                    ),
                    ft.Text(
                        f"Documents: {len(files_text_widgets)}/20",
                        **styles.SecondaryTextStyle().to_dict(),
                    ),
                ],
                alignment=ft.alignment.top_right,
            )
        )

        self.container.content = ft.Column(
            controls=[add_document_button] + files_text_widgets, spacing=5
        )
        self.container.update()

    def build(self):
        """
        Builds and returns the container.

        Returns:
            ft.Container: The container that holds the files.
        """
        return self.container
