import os
import time
import traceback
from typing import Optional

import flet as ft
from langchain.callbacks.base import BaseCallbackHandler

import app.core.ai as ai
import app.core.styles as styles
from app.controls import CopyButton, ThumbsUpDownButtons
from app.controls.illiana.chat_config import ChatConfig
from app.controls.illiana.text import ErrorText
from app.core.config import settings
from app.core.log import ic, logger


# ChatMessage class
class ChatMessage(ft.Column):
    def __init__(self, username: str, message: str = ""):
        self.username: str = username
        self.message: str = message
        self.message_display: ft.Markdown = ft.Markdown(
            self.message,
            selectable=True,
            extension_set=ft.MarkdownExtensionSet.GITHUB_FLAVORED,
            code_theme="ir-black",
            code_style=ft.TextStyle(
                size=16,
                font_family="Roboto Mono",
                weight=ft.FontWeight.W_500,
            ),
            auto_follow_links=True,
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

    def add_line(self, control: ft.Control):
        self.chat.controls.append(control)
        self.chat.scroll_to(offset=-1)
        self.chat.update()

    def remove_line(self, control: ft.Control):
        if control in self.chat.controls:
            self.chat.controls.remove(control)
            self.chat.scroll_to(offset=-1)
            self.chat.update()

    def add_chat_line(self, chat_message: ChatMessage):
        chat_message.message_display.value = chat_message.message
        self.add_line(chat_message)

    def type_chat_line(self, chat_message: ChatMessage):
        chat_message.message_display.value = ""
        self.add_line(chat_message)

        chat_message.animate_message(chat_message.message)


class ChatResponseGenerator:
    def __init__(
        self, progress_ring: ft.Row, chat_view: ChatView, chat_message: ChatMessage
    ):
        self.generator = self._create_generator()
        self.progress_ring = progress_ring
        self.chat_view = chat_view
        self.chat_message = chat_message
        next(self.generator)

    def _create_generator(self):
        try:
            removed_progress_ring: bool = False
            iter_count: int = 0
            token_count: int = 0
            while True:
                iter_count += 1
                token = yield
                if token:
                    if not removed_progress_ring:
                        # self.chat_view.remove_line(self.progress_ring)
                        removed_progress_ring = True
                    self.chat_message.message_display.value += token
                    self.chat_message.message_display.update()
                    token_count += 1
                    self.chat_view.chat.scroll_to(offset=-1)
                    self.chat_view.chat.update()
        except GeneratorExit:
            ic(token_count, iter_count)

    def send(self, token: str):
        self.generator.send(token)

    def close(self):
        logger.debug("chat_response_generator.close")
        self.generator.close()


class StreamingCallbackHandler(BaseCallbackHandler):
    def __init__(self, response_generator: ChatResponseGenerator):
        self.response_generator = response_generator

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.response_generator.send(token)


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
        self.chat_view.add_line(
            ft.Row(controls=[CopyButton(self.chat_view.page, message)])
        )

    def display_sources(self, response: dict, chat_view: ChatView) -> None:
        if response.get("sources"):
            chat_view.add_line(ft.Markdown("Sources:"))

            seen = set()
            sources: list[str] = []
            for source in response["sources"]:
                source_key = source.metadata["source"]
                if source_key not in seen:
                    seen.add(source_key)
                    sources.append(source_key)
            source_controls: list[ft.Markdown] = []

            for source in sources:
                value = (
                    f"[{os.path.basename(source.rstrip('/'))}]({source})"
                    if source.startswith("http")
                    else source
                )
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
                    value=f"- {value}",
                )
                source_controls.append(source_control)
            chat_view.add_line(
                ft.Container(content=ft.Column(source_controls, spacing=4))
            )
            chat_view.chat.update()

    def create_streaming_callback_handler(
        self,
        progress_ring: ft.Row,
        initial_chat_message: ChatMessage,
        stream_response=True,
    ) -> Optional[StreamingCallbackHandler]:
        if stream_response:
            response_generator = ChatResponseGenerator(
                progress_ring=progress_ring,
                chat_view=self.chat_view,
                chat_message=initial_chat_message,
            )
            streaming_callback_handler = StreamingCallbackHandler(response_generator)
            return streaming_callback_handler
        return None

    def add_post_footer(self, response: dict) -> ft.Container:
        def create_icon_button(icon: str, tooltip: str, on_click=None) -> ft.IconButton:
            return ft.IconButton(
                icon=icon,
                icon_size=16,
                tooltip=tooltip,
                on_click=on_click,
            )

        self.chat_view.add_line(
            ft.Row(
                spacing=0,
                controls=[
                    CopyButton(self.chat_view.page, response["response"]),
                    ThumbsUpDownButtons(self.chat_view.page),
                    create_icon_button(
                        icon=ft.icons.REFRESH_OUTLINED,
                        tooltip="Retry prompt",
                    ),
                ],
            )
        )

    def handle_bot_response(self, user_input: str, stream_response: bool = True):
        # Get response from AI
        # TODO: Add real exception handling
        try:
            # Display animated AI response
            initial_chat_message = ChatMessage(username=settings.CHAT_BOTNAME)
            self.chat_view.add_chat_line(initial_chat_message)

            # Display progress ring while waiting for a response
            progress_ring = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.ProgressRing(width=16, height=16),
                    ],
                ),
                padding=5,
            )
            self.chat_view.add_line(progress_ring)

            # Create streaming callback handler
            streaming_callback_handler = self.create_streaming_callback_handler(
                progress_ring=progress_ring,
                initial_chat_message=initial_chat_message,
                stream_response=stream_response,
            )

            knowledge_base_name = (
                self.chat_view.chat_config.knowledge_base_dropdown.dropdown.value
            )
            response, refreshed_vectorstore = ai.stream_chat_with_llm(
                user_input=user_input,
                knowledge_base_documents=self.chat_view.chat_config.knowledge_base_helper.get_documents(  # noqa
                    knowledge_base_name
                ),
                model=self.chat_view.chat_config.llm_dropdown.dropdown.value,
                context_window=self.chat_view.chat_config.llm_context_window.value,
                knowledge_base_name=knowledge_base_name,
                use_knowledge_base=self.chat_view.chat_config.use_knowledge_base_checkbox.value,  # noqa
                streaming_callback_handler=streaming_callback_handler,
            )

            if stream_response:
                if streaming_callback_handler:
                    streaming_callback_handler.response_generator.close()
                self.chat_view.remove_line(progress_ring)
            else:
                # Remove progress ring
                self.chat_view.remove_line(progress_ring)

                # TODO: Fix this hack which is only here because
                # `type_chat_line()` does some things create
                # a new `ChatMessage` instance.
                self.chat_view.remove_line(initial_chat_message)

                # Display animated AI response
                initial_chat_message = ChatMessage(
                    username=settings.CHAT_BOTNAME,
                    message=response["response"],
                )
                self.chat_view.type_chat_line(initial_chat_message)

            # Show copy/refresh post icon buttons
            self.add_post_footer(response)

            # Display sources
            self.display_sources(response, self.chat_view)

            if refreshed_vectorstore:
                self.chat_view.chat_config.knowledge_base_helper.refesh(
                    knowledge_base_name
                )
                self.chat_view.chat_config.files_container_control.update_files_container()  # noqa
        except Exception:
            exception: str = traceback.format_exc(limit=10, chain=True)
            logger.error("chat.handle_bot_response.error", exception=exception)
            self.chat_view.add_line(ErrorText(text=exception))
            self.chat_view.remove_line(progress_ring)


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
