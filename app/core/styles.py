from dataclasses import asdict, dataclass

import flet as ft


@dataclass(frozen=True)
class ColorPalette:
    BG_PRIMARY: str = "#1E1E1E"
    BG_SECONDARY: str = "#343434"
    TEXT_PRIMARY_DEFAULT: str = "#E5E5E5"
    TEXT_SECONDARY_DEFAULT: str = "#B0B0B0"
    ACCENT: str = "#4A90E2"
    ACCENT_SUCCESS: str = "#52D869"
    ACCENT_STOP: str = "#E94E77"
    ERROR: str = "#8B0000"


@dataclass(frozen=True)
class ButtonColors:
    ADD_DEFAULT: str = "#4A90E2"
    ADD_BORDER_HOVERED: str = "#66A4F7"
    DELETE_DEFAULT: str = "#E94E77"
    DELETE_BORDER_HOVERED: str = "#FF5A85"
    CANCEL_DEFAULT: str = "#282828"
    CANCEL_BORDER_HOVERED: str = "#444444"
    UPDATE_DEFAULT: str = ADD_DEFAULT
    UPDATE_BORDER_HOVERED: str = ADD_BORDER_HOVERED
    REFRESH_DEFAULT: str = "#28A745"
    REFRESH_BORDER_HOVERED: str = "#52C76E"


@dataclass(frozen=True)
class FontConfig:
    FAMILY_PRIMARY: str = "Roboto"
    SIZE_PRIMARY: int = 16
    SIZE_SECONDARY: int = 14
    SIZE_TERTIARY: int = 12
    HEADER_SIZE: int = 24
    HEADING_SIZE: int = 18


@dataclass(frozen=True)
class ButtonTextStyle:
    weight: str = ft.FontWeight.W_600
    size: int = 16
    font_family: str = FontConfig.FAMILY_PRIMARY


# Create instances for each button type
AddButtonTextStyle = ButtonTextStyle()
UpdateButtonTextStyle = ButtonTextStyle()
DeleteButtonTextStyle = ButtonTextStyle()
CancelButtonTextStyle = ButtonTextStyle()
RefreshButtonTextStyle = ButtonTextStyle()


@dataclass(frozen=True)
class Style:
    def to_dict(self):
        return asdict(self)


@dataclass(frozen=True)
class TextStyle(Style):
    color: str
    font_family: str
    size: int
    weight: str


@dataclass(frozen=True)
class PrimaryTextStyle(TextStyle):
    color: str = ColorPalette.TEXT_PRIMARY_DEFAULT
    font_family: str = FontConfig.FAMILY_PRIMARY
    size: int = FontConfig.SIZE_PRIMARY
    weight: str = ft.FontWeight.W_400


@dataclass(frozen=True)
class SecondaryTextStyle(TextStyle):
    color: str = ColorPalette.TEXT_SECONDARY_DEFAULT
    font_family: str = FontConfig.FAMILY_PRIMARY
    size: int = FontConfig.SIZE_SECONDARY
    weight: str = ft.FontWeight.W_400


@dataclass(frozen=True)
class ModalTitle(PrimaryTextStyle):
    weight: str = ft.FontWeight.W_700


@dataclass(frozen=True)
class ModalSubtitle(SecondaryTextStyle):
    weight: str = ft.FontWeight.W_400


@dataclass(frozen=True)
class SidebarLabelHeadingStyle(SecondaryTextStyle):
    size: int = FontConfig.HEADING_SIZE
    weight: str = ft.FontWeight.W_700


@dataclass(frozen=True)
class SidebarLabelStyle(SecondaryTextStyle):
    weight: str = ft.FontWeight.W_400


@dataclass(frozen=True)
class ViewLabellStyle(SecondaryTextStyle):
    size: int = FontConfig.HEADER_SIZE
    weight: str = ft.FontWeight.W_700


@dataclass(frozen=True)
class SliderLabelStyle(SecondaryTextStyle):
    weight: str = ft.FontWeight.W_700


@dataclass(frozen=True)
class SliderValueStyle(SecondaryTextStyle):
    pass


@dataclass(frozen=True)
class FilePickerFileStyle(SecondaryTextStyle):
    size: int = FontConfig.SIZE_TERTIARY


def create_button_style(
    text_color: str, default_bgcolor: str, hover_bgcolor: str, hover_border_color: str
) -> ft.ButtonStyle:
    return ft.ButtonStyle(
        color=text_color,
        bgcolor={
            "": default_bgcolor,
            ft.MaterialState.HOVERED: hover_bgcolor,
            ft.MaterialState.DISABLED: "#7F7F7F",
        },
        # animation_duration=500,
        side={
            ft.MaterialState.HOVERED: ft.BorderSide(2, hover_border_color),
        },
    )


ELEVATED_BUTTON_ADD_STYLE = create_button_style(
    ColorPalette.TEXT_PRIMARY_DEFAULT,
    ButtonColors.ADD_DEFAULT,
    ButtonColors.ADD_BORDER_HOVERED,
    ButtonColors.ADD_BORDER_HOVERED,
)

ELEVATED_BUTTON_UPDATE_STYLE = create_button_style(
    ColorPalette.TEXT_PRIMARY_DEFAULT,
    ButtonColors.UPDATE_DEFAULT,
    ButtonColors.UPDATE_BORDER_HOVERED,
    ButtonColors.UPDATE_BORDER_HOVERED,
)

ELEVATED_BUTTON_DELETE_STYLE = create_button_style(
    ColorPalette.TEXT_PRIMARY_DEFAULT,
    ButtonColors.DELETE_DEFAULT,
    ButtonColors.DELETE_DEFAULT,
    ButtonColors.DELETE_BORDER_HOVERED,
)

ELEVATED_BUTTON_CANCEL_STYLE = create_button_style(
    ColorPalette.TEXT_PRIMARY_DEFAULT,
    ButtonColors.CANCEL_DEFAULT,
    ButtonColors.CANCEL_DEFAULT,
    ButtonColors.CANCEL_BORDER_HOVERED,
)

ELEVATED_BUTTON_REFRESH_STYLE = create_button_style(
    ColorPalette.TEXT_PRIMARY_DEFAULT,
    ButtonColors.REFRESH_DEFAULT,
    ButtonColors.REFRESH_DEFAULT,
    ButtonColors.REFRESH_BORDER_HOVERED,
)


@dataclass(frozen=True)
class ChatWindowStyle(Style):
    width: int = 1125
    height: int = 850
    bgcolor: str = "#141518"
    border_radius: int = 10
    padding: int = 15


@dataclass(frozen=True)
class ChatMessageInputStyle(Style):
    width: int = 1025
    height: int = 540
    border_color: str = "white"
    content_padding: int = 10
    cursor_color: str = "white"
    cursor_height: int = 20
