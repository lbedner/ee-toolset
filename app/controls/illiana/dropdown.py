import app.core.styles as styles
import flet as ft
from app.core.log import logger


class DropdownControl(ft.UserControl):
    def __init__(
        self,
        options,
        label,
        width,
        on_change,
        height=50,
        default_value=None,
        hint_text=None,
        disabled=False,
    ):
        super().__init__()
        self.options = options
        self.label = label
        self.width = width
        self.height = height
        self.on_change = on_change
        self.default_value = default_value
        self.hint_text = hint_text
        self.disabled = disabled
        self.dropdown = ft.Dropdown(
            options=[ft.dropdown.Option(name) for name in self.options],
            label=self.label,
            width=self.width,
            height=self.height,
            hint_text=self.hint_text,
            bgcolor=styles.ColorPalette.BG_SECONDARY,
            border_width=1,
            border_color="#444444",
            border_radius=10,
            color=styles.ColorPalette.TEXT_PRIMARY_DEFAULT,
            text_size=styles.FontConfig.SIZE_SECONDARY,
            on_change=self.on_change,
            focused_border_color=styles.ColorPalette.ACCENT,
            focused_border_width=2,
        )

    def add_option(self, option: str, set_selected=False):
        self.dropdown.options.append(ft.dropdown.Option(option))
        if set_selected:
            self.dropdown.value = option
        self.update()

    def remove_option(self, option: str):
        # Find the option object in the dropdown options
        option_to_remove: ft.dropdown.Option = None
        logger.debug(
            "dropdown.options",
            option=option,
            options=[opt.key for opt in self.dropdown.options],
        )
        for opt in self.dropdown.options:
            if opt.key == option:
                logger.debug("dropdown.option.found", option=opt.key)
                option_to_remove = opt
                break

        # Remove the option if it exists
        if option_to_remove:
            logger.debug("dropdown.option.remove", option=option_to_remove)
            self.dropdown.options.remove(option_to_remove)
            self.dropdown.value = self.dropdown.options[0].key
            self.update()
        else:
            # Optionally, log or handle the case where the option does not exist
            logger.warning("dropdown.option.missing", option=option)

    def get_dropdown_value(self) -> str:
        return self.dropdown.value

    def build(self):
        if self.default_value:
            self.dropdown.value = self.default_value
        self.dropdown.disabled = self.disabled
        return self.dropdown
