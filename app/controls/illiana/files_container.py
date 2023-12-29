import os

import app.core.styles as styles
import flet as ft
from app.controls.illiana.chip import FileChip
from app.controls.illiana.dropdown import DropdownControl
from app.controls.illiana.file_picker import FilePickerControl
from app.core.config import settings
from app.models import KnowledgeBaseHelper


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
        init_knowledge_base_name,
    ):
        super().__init__()
        self.knowledge_base_helper = knowledge_base_helper
        self.file_picker_control = file_picker_control
        self.knowledge_base_dropdown = knowledge_base_dropdown
        self.delete_file_handler = delete_file_handler
        self.init_knowledge_base_name = init_knowledge_base_name
        self.container = ft.Container()
        self.init_files_container()

    def get_knowledge_base_name(self):
        """
        Returns the selected knowledge base name.

        Returns:
            str: The selected knowledge base name.
        """
        return self.knowledge_base_dropdown.get_dropdown_value()

    def init_files_container(self):
        """
        Updates the files container with the latest files.
        """
        knowledge_base_name = self.get_knowledge_base_name()
        if not knowledge_base_name:
            knowledge_base_name = self.init_knowledge_base_name
        files_text_widgets: list[FileChip] = []

        if knowledge_base_name in self.knowledge_base_helper.document_data:
            knowledge_base_documents = self.knowledge_base_helper.get_documents(
                knowledge_base_name,
            )

            files_text_widgets = [
                FileChip(
                    file_name=os.path.basename(knowledge_base_document.Filepath),
                    file_size=knowledge_base_document.Size,
                    delete_handler=self.delete_file_handler,
                    knowledge_base_name=knowledge_base_name,
                    loaded=knowledge_base_document.Loaded,
                )
                for knowledge_base_document in knowledge_base_documents.values()
            ]

        if self.knowledge_base_helper.get_knowledge_base_names():
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
                            f"Documents: {len(files_text_widgets)}",
                            **styles.SecondaryTextStyle().to_dict(),
                        ),
                    ],
                    alignment=ft.alignment.top_right,
                )
            )

            self.container.content = ft.Column(
                controls=[add_document_button] + files_text_widgets, spacing=5
            )

    def update_files_container(self):
        """
        Updates the files container with the latest files.
        """
        self.init_files_container()
        self.container.update()

    def build(self):
        """
        Builds and returns the container.

        Returns:
            ft.Container: The container that holds the files.
        """
        return self.container
