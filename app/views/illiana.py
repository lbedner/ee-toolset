import flet as ft
from app.controls.illiana.chat import ChatView, UserInputBar, UserInputField
from app.controls.illiana.chat_config import ChatConfig
from app.controls.illiana.conversation_starters import ConversationStarters
from app.core.constants import ILLIANA_ROUTE

from .view import BaseView


class IllianaView(BaseView):
    def __init__(self, page: ft.Page):
        self.chat_config = ChatConfig(page=page)
        self.chat_view = ChatView(chat_config=self.chat_config, page=page)
        user_input_field = UserInputField(chat_view=self.chat_view)
        divider = ft.Divider(height=0.2, color="transparent")
        super().__init__(
            page,
            ILLIANA_ROUTE,
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                controls=[
                    ft.Column(
                        controls=[
                            ft.Text(
                                "Illiana",
                                size=24,
                                weight="w800",
                                font_family="Roboto",
                            ),
                            ft.Text(
                                "Illiana is a chatbot that uses the OpenAI API to generate responses to your messages. "  # noqa
                                "This is a work in progress.",
                                opacity=0.6,
                            ),
                            self.chat_view,
                            divider,
                            ConversationStarters(
                                self.chat_view,
                                user_input_field,
                            ),
                            divider,
                            UserInputBar(user_input_field),
                            ft.Container(
                                content=ft.Row(
                                    controls=[
                                        ft.Text(
                                            "Powered by OpenAI",
                                            opacity=0.6,
                                            font_family="Roboto",
                                            size=10,
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER,
                                ),
                                alignment=ft.alignment.center,
                                width=1200,
                            ),
                        ],
                        spacing=15,
                        alignment=ft.alignment.top_center,
                    ),
                    self.chat_config,
                ],
                spacing=0,
            ),
            scroll_mode="auto",
        )
        # user_input.focus()
