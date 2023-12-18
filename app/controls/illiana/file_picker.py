import os
import threading

import flet as ft
from app.controls.attributes.snack_bar import SuccessSnackBar
from app.controls.illiana.dropdown import DropdownControl
from app.core.config import settings
from app.core.log import logger
from app.models import KnowledgeBaseHelper


class FilePickerControl(ft.UserControl):
    def __init__(
        self,
        knowledge_base_dropdown: DropdownControl,
        knowledge_base_helper: KnowledgeBaseHelper,
        page: ft.Page,
        on_files_processed=None,
        on_success_message: str = "Success!",
    ):
        super().__init__()
        self.on_files_processed = on_files_processed
        self.knowledge_base_dropdown = knowledge_base_dropdown
        self.knowledge_base_helper = knowledge_base_helper
        self.page = page
        self.loading_indicator = ft.ProgressRing(visible=False)
        self.pick_files_dialog = ft.FilePicker(on_result=self.pick_files_result)
        self.on_success_message = on_success_message

    def pick_files_result(self, e: ft.FilePickerResultEvent):
        logger.debug("pick_files_result", file_picker_result_event=e)
        threading.Thread(target=self.process_files, args=(e,), daemon=True).start()

    def process_files(self, e: ft.FilePickerResultEvent):
        logger.debug("process_files", file_picker_result_event=e)
        if e.files:
            self.loading_indicator.visible = True
            self.update()

            knowledge_base_name = self.knowledge_base_dropdown.dropdown.value

            for uploaded_file in e.files:
                uploaded_file_path = uploaded_file.path
                document_name = os.path.basename(uploaded_file_path)
                knowledge_base_file_path = os.path.join(
                    settings.VECTORSTORE_KNOWLEDGE_BASE_DIR,
                    knowledge_base_name,
                    document_name,
                )

                self.knowledge_base_helper.add_document(
                    knowledge_base_name=knowledge_base_name,
                    document_name=document_name,
                    incoming_filename=uploaded_file_path,
                    outgoing_filename=knowledge_base_file_path,
                )

            if self.on_files_processed:
                self.on_files_processed(self.knowledge_base_helper.document_data)

            self.loading_indicator.visible = False
            self.page.snack_bar = SuccessSnackBar(
                message=self.on_success_message,
            ).build()
            self.page.snack_bar.open = True
            self.page.update()

            self.update()
        else:
            self.update()

    def build(self):
        return ft.Column([self.loading_indicator, self.pick_files_dialog])
