import flet as ft
from icecream import ic


class SideBarControl(ft.UserControl):
    def __init__(self):
        super().__init__()

    def create_destination(self, icon_outlined, icon, label):
        ic(icon_outlined, icon, label)
        return ft.NavigationRailDestination(
            icon_content=ft.Icon(icon_outlined, tooltip=label),
            selected_icon_content=ft.Icon(icon, tooltip=label),
        )

    def create_destinations(self, destinations):
        return [self.create_destination(*d) for d in destinations]

    def build(self):
        destinations = (
            (ft.icons.SAVE_OUTLINED, ft.icons.SAVE, "Save Game Editor"),
            (ft.icons.HANDYMAN_OUTLINED, ft.icons.HANDYMAN, "Attributes"),
            (ft.icons.KEY_OUTLINED, ft.icons.KEY, "Items"),
            (
                ft.icons.LOCAL_FIRE_DEPARTMENT_OUTLINED,
                ft.icons.LOCAL_FIRE_DEPARTMENT,
                "Abilities",
            ),
            (ft.icons.MAN_OUTLINED, ft.icons.MAN, "Units"),
            (ft.icons.LIBRARY_MUSIC_OUTLINED, ft.icons.LIBRARY_MUSIC, "Audio"),
            (ft.icons.MAP_OUTLINED, ft.icons.MAP, "Codex"),
            (ft.icons.CHAT_BUBBLE_OUTLINE, ft.icons.CHAT_BUBBLE, "Illiana"),
        )
        # destinations = sorted(destinations, key=lambda d: d.label_content.text)
        return ft.NavigationRail(
            height=1300,
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=400,
            # leading=ft.FloatingActionButton(icon=ft.icons.CREATE, text="Managers"),
            group_alignment=-1.0,
            destinations=self.create_destinations(destinations),
            on_change=lambda e: ic("Selected destination:", e.control.selected_index),
        )
