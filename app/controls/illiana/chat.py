import time

import app.core.ai as ai
import app.core.styles as styles
import flet as ft
from app.controls.illiana.chat_config import ChatConfig
from app.core.config import settings
from app.core.log import ic


# ChatMessage class
class ChatMessage(ft.Column):
    def __init__(self, username: str, message: str = ""):
        self.username = username
        self.message = message
        self.message_display = ft.Markdown(
            self.message,
            selectable=True,
            extension_set=ft.MarkdownExtensionSet.GITHUB_FLAVORED,
            code_theme="atom-one-dark",
            code_style=ft.TextStyle(
                size=16,
                font_family="Roboto Mono",
                weight=ft.FontWeight.W_500,
            ),
        )
        super().__init__(spacing=4)
        avatar_color: str = styles.ColorPalette.ACCENT
        if username == settings.CHAT_BOTNAME:
            avatar_color = "#C2185B"
        self.controls = [
            ft.CircleAvatar(
                # foreground_image_url="https://lh5.googleusercontent.com/-7KjAFSgxT-I/AAAAAAAAAAI/AAAAAAAAADs/bSN5JebQUgI/photo.jpg",
                content=ft.Text(
                    self.create_initials(self.username),
                    font_family=styles.FontConfig.FAMILY_PRIMARY,
                ),
                max_radius=15,
                bgcolor=avatar_color,
            ),
            # ft.Markdown(self.username, opacity=0.6),
            self.message_display,
        ]

    def create_initials(self, name: str) -> str:
        """Create initials from the given name string."""
        words = name.split()

        if len(words) >= 2:
            return words[0][0].upper() + words[1][0].upper()
        elif words:
            return words[0][:2].upper()
        else:
            return ""

    def animate_message(self, message: str):
        characters = list(message)
        for character in characters:
            self.message_display.value += character
            self.message_display.update()
            time.sleep(settings.CHAT_TEXT_ANIMATION_SPEED)


# ChatView class
class ChatView(ft.Container):
    def __init__(self, chat_config: ChatConfig, page: ft.Page) -> None:
        super().__init__(**styles.ChatWindowStyle().to_dict())
        self.chat = ft.ListView(expand=True, height=200, spacing=15)
        self.content = self.chat
        self.chat_config = chat_config
        self.page = page

    def add_chat_line(self, chat_message: ChatMessage):
        chat_message.message_display = chat_message.message
        self.chat.controls.append(chat_message)
        self.chat.update()

    def type_chat_line(self, chat_message: ChatMessage):
        chat_message.message_display.value = ""
        self.chat.controls.append(chat_message)
        self.chat.update()

        chat_message.animate_message(chat_message.message)


# MessageHandler class
class MessageHandler:
    def __init__(self, chat_view: ChatView):
        self.chat_view = chat_view

    def handle_user_message(self, message: str):
        chat_message = ChatMessage(
            username=settings.CHAT_USERNAME,
            message=message,
        )
        self.chat_view.add_chat_line(chat_message)

    def handle_bot_response(self, user_input: str):
        # Display progress ring while waiting for a response
        progress_ring = ft.Row(
            controls=[
                ft.ProgressRing(width=16, height=16),
                ft.Text(
                    value="Thinking...",
                    **styles.ModalSubtitle().to_dict(),
                ),
            ],
            spacing=4,
        )
        self.chat_view.chat.controls.append(progress_ring)
        self.chat_view.chat.update()

        # Get response from AI
        knowledge_base_name = (
            self.chat_view.chat_config.knowledge_base_dropdown.dropdown.value
        )
        response = ai.chat_with_llm(
            user_input=user_input,
            document_data=self.chat_view.chat_config.knowledge_base_helper.document_data[
                knowledge_base_name
            ],
            model=self.chat_view.chat_config.llm_dropdown.dropdown.value,
            context_window=self.chat_view.chat_config.llm_context_window.value,
            knowledge_base_name=knowledge_base_name,
        )

        # Remove progress ring
        self.chat_view.chat.controls.remove(progress_ring)
        self.chat_view.chat.update()

        # Display animated AI response
        chat_message = ChatMessage(
            username=settings.CHAT_BOTNAME,
            message=response["response"],
        )
        self.chat_view.type_chat_line(chat_message)

        # Display sources
        if response.get("sources"):
            self.chat_view.chat.controls.append(ft.Markdown("Sources:"))
            sources = []
            for source in response["sources"]:
                source_control = ft.Markdown(
                    auto_follow_links=True,
                    code_style=ft.TextStyle(
                        size=16,
                        font_family="Roboto Mono",
                        weight=ft.FontWeight.W_500,
                    ),
                    code_theme="atom-one-dark",
                    extension_set=ft.MarkdownExtensionSet.GITHUB_FLAVORED,
                    selectable=True,
                    value=f"- [{source.metadata['source']}](https://www.google.com)",
                )
                sources.append(source_control)
            self.chat_view.chat.controls.append(
                ft.Container(content=ft.Column(sources, spacing=4))
            )
        self.chat_view.chat.update()


class UserInputField(ft.TextField):
    ENABLED_PROMPT = "Enter a prompt here"
    DISABLED_PROMPT = "Illiana is thinking about your question..."

    def __init__(self, chat_view: ChatView) -> None:
        super().__init__(
            **styles.ChatMessageInputStyle().to_dict(),
            on_submit=self.handle_user_input,
            bgcolor=styles.ColorPalette.BG_SECONDARY,
            border=ft.border.all(2, "#444444"),
            border_radius=15,
            text_size=styles.FontConfig.SIZE_SECONDARY,
            multiline=True,
            min_lines=1,
            max_lines=9,
            shift_enter=True,
            hint_text=self.ENABLED_PROMPT,
            suffix_style=styles.ModalSubtitle().to_dict(),
        )
        self.chat_view = chat_view
        self.message_handler = MessageHandler(chat_view)

    def handle_user_input(self, event: ft.ControlEvent) -> None:
        ic(event.control.value)
        self.handle_input(event.control.value)

    def handle_input(self, input: str) -> None:
        ic(f"Handling input: {input}")
        message = self.sanitize_input(input)
        if message:
            # Disable input
            self.value = ""
            self.disabled = True
            self.hint_text = self.DISABLED_PROMPT
            self.update()

            # Send message to chat view
            self.message_handler.handle_user_message(message)
            self.message_handler.handle_bot_response(message)

            # Re-enable input
            self.hint_text = self.ENABLED_PROMPT
            self.disabled = False
            self.update()

    def sanitize_input(self, message: str) -> str:
        return message.strip()


class SubmitButton(ft.IconButton):
    def __init__(self, user_input_field: UserInputField):
        super().__init__(
            icon=ft.icons.SUBDIRECTORY_ARROW_RIGHT_OUTLINED,
            icon_size=36,
            icon_color=styles.ColorPalette.ACCENT,
            tooltip="Send prompt",
            on_click=lambda _: user_input_field.handle_input(
                user_input_field.value
            ),  # noqa
        )


class StopButton(ft.IconButton):
    def __init__(self, user_input_field: UserInputField):
        super().__init__(
            icon=ft.icons.STOP_CIRCLE_OUTLINED,
            icon_size=36,
            icon_color=styles.ColorPalette.ACCENT_STOP,
            tooltip="Stop",
            on_click=lambda _: user_input_field.handle_input(
                user_input_field.value
            ),  # noqa
        )


class UserInputBar(ft.Container):
    def __init__(self, user_input_field: UserInputField):
        super().__init__(
            height=200,
            content=ft.Row(
                controls=[
                    ft.IconButton(
                        icon=ft.icons.ADD_CIRCLE_OUTLINE_OUTLINED,
                        icon_size=36,
                        tooltip="Upload file",
                    ),
                    user_input_field,
                    SubmitButton(user_input_field),
                    # stop_button,
                ],
                vertical_alignment=ft.CrossAxisAlignment.START,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        )
