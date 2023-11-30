import app.core.styles as styles
import flet as ft
from app.controls.illiana.chat import ChatView, UserInputField


class ConversationStarters(ft.UserControl):
    def __init__(self, chat_view: ChatView, user_input_field: UserInputField, **kwargs):
        super().__init__(**kwargs)
        self.chat_view = chat_view
        self.user_input_field = user_input_field
        self.selected_chip = None  # Track the selected chip

    def _create_chip(self, text):
        # This method will create a Chip with common styling and behavior.
        return ft.Chip(
            label=ft.Text(text, **styles.ModalSubtitle().to_dict()),
            bgcolor=styles.ColorPalette.BG_SECONDARY,
            on_click=lambda e: self.on_chip_click(e),
            selected_color=styles.ColorPalette.ACCENT,
            show_checkmark=False,
        )

    def on_chip_click(self, event: ft.ControlEvent):
        clicked_chip: ft.Chip = event.control
        # Logic to update the selected chip
        if self.selected_chip:
            self.selected_chip.selected = False  # Deselect the previously selected chip
        clicked_chip.selected = True  # Select the new chip
        self.selected_chip = clicked_chip
        self.update()

        # Send message to chat view
        self.user_input_field.handle_input(input=clicked_chip.label.value)

    def build(self):
        # Split conversation starters into two groups
        first_row_starters = [
            "How can you help me?",
            'What is "Rose of Eternity"?',
            "Summarize the document(s)",
            "Python code snippets",
            # 'Tell me about "The Coming".',
        ]

        # Create chips for each conversation starter
        first_row_chips = [self._create_chip(text) for text in first_row_starters]

        # Create two rows for conversation starters
        first_row = ft.Row(
            controls=first_row_chips, alignment=ft.MainAxisAlignment.CENTER
        )

        return ft.Container(
            content=ft.Column(
                controls=[
                    first_row,
                    # second_row,
                ],
                alignment=ft.alignment.center,
            ),
            alignment=ft.alignment.center,
            width=1100,
        )
