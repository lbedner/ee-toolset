import flet as ft

from app.controls.attributes.attribute_table import AttributeTable
import app.core.constants as constants
import app.core.styles as styles


def main(page: ft.Page):
    page.window_height = constants.PAGE_WINDOW_HEIGHT
    page.window_width = constants.PAGE_WINDOW_WIDTH
    page.scroll = ft.ScrollMode.AUTO
    page.bgcolor = styles.ColorPalette.BG_PRIMARY
    # page.theme = ft.Theme(color_scheme_seed=styles.ColorPalette.BG_SECONDARY)
    page.add(
        ft.Text(
            "Attribues",
            color=styles.ColorPalette.TEXT_PRIMARY_DEFAULT,
            size=styles.FontConfig.HEADER_SIZE,
            font_family=styles.FontConfig.FAMILY_PRIMARY,
            weight=ft.FontWeight.W_700,
        )
    )

    tab_names = ("All", "Units", "Items", "Abilities")
    tabs = ft.Tabs(
        selected_index=0,
        # scrollable=False,
        tabs=[ft.Tab(text=name) for name in tab_names],
    )

    table = AttributeTable(page=page)

    # page.add(action_bar, table)
    page.add(table)
    page.update()


ft.app(target=main)
