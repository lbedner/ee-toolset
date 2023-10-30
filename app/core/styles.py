from dataclasses import dataclass, asdict

import flet as ft


@dataclass(frozen=True)
class ColorPalette:
    BG_PRIMARY: str = "#1E1E1E"
    BG_SECONDARY: str = "#343434"
    TEXT_PRIMARY_DEFAULT: str = "#E5E5E5"
    TEXT_SECONDARY_DEFAULT: str = "#B0B0B0"
    ACCENT: str = "#4A90E2"
    ACCENT_SUCCESS: str = "#52D869"


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


@dataclass(frozen=True)
class FontConfig:
    FAMILY_PRIMARY: str = "Roboto"
    SIZE_PRIMARY: int = 16
    SIZE_SECONDARY: int = 14
    HEADER_SIZE: int = 24


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


@dataclass(frozen=True)
class ModalTitle:
    color: str = ColorPalette.TEXT_PRIMARY_DEFAULT
    font_family: str = FontConfig.FAMILY_PRIMARY
    size: int = FontConfig.SIZE_PRIMARY
    weight: str = ft.FontWeight.W_700

    def to_dict(self):
        return asdict(self)


@dataclass(frozen=True)
class ModalSubtitle:
    color: str = ColorPalette.TEXT_SECONDARY_DEFAULT
    font_family: str = FontConfig.FAMILY_PRIMARY
    size: int = FontConfig.SIZE_SECONDARY
    weight: str = ft.FontWeight.W_400

    def to_dict(self):
        return asdict(self)


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