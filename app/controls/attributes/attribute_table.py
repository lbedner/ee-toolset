from typing import Optional

from icecream import ic

import app.core.styles as styles
import app.models as models
import flet as ft

from .buttons import (
    BaseElevatedButton,
    ElevatedAddButton,
    ElevatedCancelButton,
    ElevatedDeleteButton,
    ElevatedUpdateButton,
)
from .snack_bar import SuccessSnackBar

ic.configureOutput(includeContext=True)


class AttributeTable(ft.UserControl):
    def __init__(self, page: ft.Page, **kwargs):
        super().__init__(**kwargs)
        self.page = page
        self.attributes = models.Attributes.load()
        self.columns = self._get_columns(
            exclude=(
                "MinimumValue",
                "MaximumValue",
            )
        )
        self.selected_rows: set[str] = set()
        self.rows = self._create_rows()
        self.table = self._create_table()
        self.action_bar: Optional[ActionBar] = None

    def add_row(self, attribute_key: str, attribute: models.Attribute):
        cells = [
            self._create_cell(column, attribute_key, attribute.model_dump())
            for column in self.columns
        ]
        new_row = ft.DataRow(
            cells=cells,
            on_select_changed=lambda e, key=attribute_key: self.on_row_select_changed(
                e, key
            ),
        )

        # Update the rows list and the DataTable
        self.rows.append(new_row)

        if self.table.sort_column_index is not None:
            self.sort_rows(
                self.columns[self.table.sort_column_index],
                self.table.sort_ascending,
            )
        self.table.rows = self.rows

        # Update the Attributes model and dump to file
        self.attributes.add(attribute_key, attribute)

    def remove_row(self, attribute_key: str):
        # Find the index of the row to be removed
        row_index = next(
            (
                index
                for index, row in enumerate(self.rows)
                if row.cells[0].content.value == attribute_key
            ),
            None,
        )

        # If found, remove the row from the rows list and the DataTable
        if row_index is not None:
            del self.rows[row_index]
            self.table.rows = self.rows

            # Update the Attributes model and dump to file
            self.attributes.remove(attribute_key)

    def update_row(self, attribute_key: str, attribute: models.Attribute):
        # Find the index of the row to be updated
        row_index = self.find_row_index(attribute_key)

        # If found, update the cells in the row with the new attribute data
        if row_index is not None:
            new_key = attribute.Type
            if new_key != attribute_key:
                # Update key in the root dictionary
                self.attributes.root[new_key] = self.attributes.root.pop(attribute_key)
                # Update the key in the table row as well
                self.table.rows[row_index].cells[0].content.value = new_key
            for column_index, column in enumerate(self.columns):
                new_cell_content = self._create_cell(
                    column, attribute.Type, attribute.model_dump()
                )
                self.table.rows[row_index].cells[column_index] = new_cell_content

            # Update the Attributes model and dump to file
            self.attributes.update(new_key, attribute)

            # Update the DataTable and the page to reflect the changes
            self.table.update()
            self.page.update()

    def update_table(self, search_query: str):
        # Convert the search query to lowercase for case-insensitive searching
        search_query = search_query.lower()

        # Filter the rows based on the search query
        filtered_rows = [
            row
            for row in self.rows
            if search_query in row.cells[0].content.value.lower()
        ]

        # Update the DataTable's rows
        self.table.rows = filtered_rows

        # Update the page to reflect the changes
        self.table.update()

    def sort_table(self, column_name: str, ascending: bool = True):
        self.sort_rows(column_name, ascending)

        # Update the DataTable's rows to reflect the sorted order
        self.table.rows = self.rows
        self.table.update()
        self.page.update()

    def sort_rows(self, column_name: str, ascending: bool = True):
        # Convert column name to the index, assuming column names are unique
        column_index = self.columns.index(column_name)

        # Sort rows based on the content of the specified column
        self.rows.sort(
            key=lambda row: row.cells[column_index].content.value,
            reverse=not ascending,  # reverse is False for ascending, True for descending
        )

    def _get_columns(self, exclude: tuple[str, ...] = ()) -> list[str]:
        return [
            col for col in models.Attribute.model_fields.keys() if col not in exclude
        ] + ["Action"]

    def _create_rows(self):
        rows = []
        for attribute_key, attribute in self.attributes.model_dump().items():
            cells = [
                self._create_cell(column, attribute_key, attribute)
                for column in self.columns
            ]
            rows.append(
                ft.DataRow(
                    cells=cells,
                    on_select_changed=lambda e, key=attribute_key: self.on_row_select_changed(  # noqa
                        e, key
                    ),
                )
            )
        rows.sort(
            key=lambda row: row.cells[0].content.value,
            reverse=False,  # reverse is False for ascending, True for descending
        )
        return rows

    def _create_cell(self, column, attribute_key, attribute):
        if column == "Action":
            cell_content = ft.Row(
                controls=[
                    ft.IconButton(
                        icon=ft.icons.EDIT_OUTLINED,
                        selected_icon=ft.icons.EDIT_ROUNDED,
                        on_click=lambda _: self.show_edit_attribute_alert_dialog(
                            self.page,
                            self.attributes,
                            attribute_key,
                        ),
                        icon_color="#2D89EF",
                        tooltip="Edit Attribute",
                    ),
                    ft.IconButton(
                        icon=ft.icons.DELETE_OUTLINE_ROUNDED,
                        selected_icon=ft.icons.DELETE_ROUNDED,
                        on_click=lambda _: self.show_delete_attribute_alert_dialog(
                            attribute_key,
                        ),
                        icon_color=styles.ColorPalette.ACCENT_STOP,
                        tooltip="Delete Attribute",
                    ),
                ],
            )
        else:
            cell_content = ft.Text(
                attribute.get(column, ""),
                font_family=styles.FontConfig.FAMILY_PRIMARY,
                size=styles.FontConfig.SIZE_PRIMARY,
                color=styles.ColorPalette.TEXT_PRIMARY_DEFAULT,
            )
        return ft.DataCell(cell_content)

    def _create_table(self):
        def on_sort_callback(e: ft.ControlEvent):
            self.table.sort_ascending = e.ascending
            self.sort_table(self.columns[e.column_index], e.ascending)

        return ft.DataTable(
            data_row_min_height=50,
            divider_thickness=0,
            border_radius=100,
            sort_column_index=0,
            sort_ascending=True,
            heading_row_color=styles.ColorPalette.BG_SECONDARY,
            heading_row_height=60,
            data_row_color={"hovered": styles.ColorPalette.ACCENT},
            show_checkbox_column=True,
            columns=[
                ft.DataColumn(
                    ft.Text(
                        column,
                        text_align=ft.TextAlign.CENTER,
                        weight=ft.FontWeight.BOLD,
                        font_family=styles.FontConfig.FAMILY_PRIMARY,
                        color=styles.ColorPalette.TEXT_PRIMARY_DEFAULT,
                    ),
                    on_sort=on_sort_callback,
                )
                for column in self.columns
            ],
            rows=self.rows,
            on_select_all=self.on_select_all,
        )

    def str_to_bool(self, s: str) -> bool:
        return s.lower() == "true"

    def on_row_select_changed(self, e: ft.ControlEvent, attribute_key: str):
        row_index = self.find_row_index(attribute_key)
        is_selected = self.str_to_bool(e.data)
        if row_index is not None:
            self.table.rows[
                row_index
            ].selected = is_selected  # Update the selected property
        if is_selected:
            self.selected_rows.add(attribute_key)
        else:
            self.selected_rows.discard(attribute_key)
        self.update_delete_button()
        self.update()

    def on_select_all(self, e: ft.ControlEvent):
        is_selected = self.str_to_bool(e.data)
        for row in self.table.rows:
            row.selected = is_selected  # Update the selected property of each row
        if is_selected:
            self.selected_rows = set(self.attributes.model_dump().keys())
        else:
            self.selected_rows.clear()
        self.update_delete_button()
        self.update()

    def update_delete_button(self):
        delete_button = self.action_bar.delete_button
        if delete_button:
            delete_button.disabled = not self.selected_rows
            delete_button.update()
            self.page.update()

    def confirm_delete_selected_attributes(self):
        def on_confirm():
            for attribute_key in self.selected_rows:
                self.remove_row(attribute_key)
            self.selected_rows.clear()
            self.update()
            self.page.dialog.open = False
            self.page.update()

        def on_click_close_dialog():
            self.page.dialog.open = False
            self.page.update()

        alert_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirm Deletion", **styles.ModalTitle().to_dict()),
            content=ft.Text(
                "Are you sure you want to delete the selected attributes?",
                **styles.ModalSubtitle().to_dict(),
            ),
            actions=[
                ElevatedCancelButton(on_click_close_dialog),
                ElevatedDeleteButton(on_confirm),
            ],
        )
        self.page.show_dialog(alert_dialog)
        self.page.dialog = alert_dialog
        alert_dialog.open = True
        self.page.update()

    def find_row_index(self, attribute_key: str) -> Optional[int]:
        for index, row in enumerate(self.table.rows):
            if row.cells[0].content.value == attribute_key:
                return index
        return None  # Return None if the row was not found

    def build(self):
        return ft.Container(
            ft.Column(
                controls=[
                    ft.Text(
                        "Attributes",
                        **styles.ViewLabellStyle().to_dict(),
                    ),
                    ActionBar(self.page, self.attributes, self),
                    ft.Container(
                        # padding=100,
                        content=self.table,
                        # bgcolor="#282828",
                        border_radius=15,
                    ),
                ],
                # scroll="always",
                # on_scroll=lambda _: ic("on_scroll"),
                # alignment=ft.MainAxisAlignment.START,
                # horizontal_alignment=ft.CrossAxisAlignment.,
            ),
            expand=True,
            width=2000,
            alignment=ft.alignment.center_right,
        )

    def show_attribute_alert_dialog(
        self,
        page: ft.Page,
        attributes: models.Attributes,
        title_text: str,
        form_class,
        attribute_key: str = None,
    ):
        # Create a new AlertDialog
        alert_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title_text, style=styles.ModalTitle().to_dict()),
            content=form_class(page, attributes, self, attribute_key),
        )

        # Show the AlertDialog
        page.show_dialog(alert_dialog)
        page.dialog = alert_dialog
        alert_dialog.open = True
        page.update()

    def show_add_attribute_alert_dialog(
        self, page: ft.Page, attributes: models.Attributes
    ):
        self.show_attribute_alert_dialog(
            page, attributes, "Add New Attribute", AddAttributeForm
        )

    def show_edit_attribute_alert_dialog(
        self, page: ft.Page, attributes: models.Attributes, attribute_key: str
    ):
        self.show_attribute_alert_dialog(
            page,
            attributes,
            "Edit Attribute",
            EditAttributeForm,
            attribute_key,
        )

    def show_delete_attribute_alert_dialog(self, attribute_key: str):
        def on_click_delete_attribute():
            self.page.dialog.open = False
            self.remove_row(attribute_key)
            self.page.snack_bar = SuccessSnackBar(
                "Attribute Was Deleted Successfully."
            ).build()
            self.page.snack_bar.open = True
            self.update()
            self.page.update()

        def on_click_close_dialog():
            self.page.dialog.open = False
            self.update()
            self.page.update()

        # Create a new AlertDialog
        alert_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirm Deletion", **styles.ModalTitle().to_dict()),
            content=ft.Text(
                f"Are you sure you want to delete the attribute {attribute_key}?",
                **styles.ModalSubtitle().to_dict(),
            ),
            actions=[
                ElevatedCancelButton(on_click_callable=on_click_close_dialog),
                ElevatedDeleteButton(
                    on_click_callable=on_click_delete_attribute,
                ),
            ],
        )

        # Show the AlertDialog
        self.page.show_dialog(alert_dialog)
        self.page.dialog = alert_dialog
        alert_dialog.open = True
        self.page.update()


class ActionBar(ft.UserControl):
    def __init__(
        self,
        page: ft.Page,
        attributes: models.Attributes,
        table: AttributeTable,
    ):
        super().__init__()
        self.page = page
        self.attributes = attributes
        self.table = table
        self.table.action_bar = self

    def on_search_change(self, e: ft.ControlEvent):
        self.table.update_table(e.control.value)

    def build(self):
        search_text_field = ft.TextField(
            label="Search",
            prefix_icon=ft.icons.SEARCH,
            color=styles.ColorPalette.TEXT_SECONDARY_DEFAULT,
            hint_text="Search Attributes...",
            bgcolor=styles.ColorPalette.BG_SECONDARY,
            text_size=styles.FontConfig.SIZE_SECONDARY,
            border=ft.Border(2, "#444444"),
            border_radius=15,
            on_change=self.on_search_change,
        )
        add_buton = ft.ElevatedButton(
            text="ADD",
            icon=ft.icons.ADD_CIRCLE_OUTLINE_ROUNDED,
            on_click=lambda _: self.table.show_add_attribute_alert_dialog(
                self.page, self.attributes
            ),
            style=styles.ELEVATED_BUTTON_ADD_STYLE,
        )
        self.delete_button = ft.ElevatedButton(
            text="DELETE",
            icon=ft.icons.DELETE_OUTLINE_ROUNDED,
            on_click=lambda _: self.table.confirm_delete_selected_attributes(),
            style=styles.ELEVATED_BUTTON_DELETE_STYLE,
            disabled=True,
        )
        return ft.Row(
            controls=[
                ft.Container(
                    content=search_text_field,
                    # TODO: Figure out how to align the search bar to the right
                    # alignment=ft.MainAxisAlignment.END,
                ),
                add_buton,
                self.delete_button,
            ],
        )


class BaseAttributeForm(ft.UserControl):
    def __init__(
        self,
        page: ft.Page,
        attributes: models.Attributes,
        table: AttributeTable,
        attribute_key: str = None,
    ):
        super().__init__()
        self.page = page
        self.attributes = attributes
        self.table = table
        self.attribute_key = attribute_key
        self.attribute = (
            attributes.root[attribute_key] if attribute_key else None
        )  # noqa

    def build(self):
        self.create_common_fields()
        self.create_specific_fields()
        return self.create_layout()

    def create_common_fields(self, default_values: dict = None):
        default_values = default_values or {}
        self.name = self.create_text_field(
            "Name",
            "Enter name (eg. Strength)",
            value=default_values.get("Name"),
        )
        self.short_name = self.create_text_field(
            "Short Name",
            "Enter short name (eg. STR)",
            value=default_values.get("ShortName"),
        )
        self.tooltip = self.create_text_field(
            "Tooltip",
            "Enter tooltip (eg. Strength is a measure of physical power)",
            keyboard_type=ft.KeyboardType.MULTILINE,
            capitalization=ft.TextCapitalization.SENTENCES,
            value=default_values.get("ToolTip"),
        )
        self.minimum_value = self.create_text_field(
            "Minimum Value",
            "Enter minimum value (eg. 3)",
            keyboard_type=ft.KeyboardType.NUMBER,
            value=default_values.get("MinimumValue", 0),
        )
        self.maximum_value = self.create_text_field(
            "Maximum Value",
            "Enter maximum value (eg. 20)",
            keyboard_type=ft.KeyboardType.NUMBER,
            value=default_values.get("MaximumValue", 20),
        )

    def create_specific_fields(self):
        # To be implemented by subclasses
        pass

    def create_text_field(self, label, hint_text, **kwargs):
        return ft.TextField(
            label=label,
            width=480,
            height=70,
            bgcolor=styles.ColorPalette.BG_SECONDARY,
            border=ft.border.all(2, "#444444"),
            hint_text=hint_text,
            text_size=styles.FontConfig.SIZE_SECONDARY,
            on_change=self.validate_text,
            **kwargs,
        )

    def create_layout(self):
        # To be implemented by subclasses
        pass

    def type_conversion(self, value):
        return value.replace(" ", "_").upper()

    def common_layout(self, action_button: BaseElevatedButton):
        self.action_button = action_button
        self.action_button.disabled = True
        return ft.Column(
            spacing=16,
            width=480,
            height=450,
            controls=[
                self.name,
                self.short_name,
                self.tooltip,
                self.minimum_value,
                self.maximum_value,
                ft.Row(
                    controls=[
                        ElevatedCancelButton(self.on_click_close_dialog),
                        action_button,
                    ]
                ),
            ],
        )

    def on_click_close_dialog(self):
        self.page.dialog.open = False
        self.page.update()

    def validate_text(self, e: ft.ControlEvent):
        text = e.control.value

        if e.control == self.minimum_value or e.control == self.maximum_value:
            self.validate_integer_field(e.control, text)
        else:
            # Assuming a simple validation that the text must be non-empty
            if not text:
                e.control.error_text = "This field cannot be empty"
            elif text.isnumeric():
                e.control.error_text = "This field cannot contain numbers"
            else:
                e.control.error_text = None

        # Update the page to reflect changes
        self.check_validation_status()

    def validate_integer_field(self, control: ft.TextField, text: str):
        try:
            value = int(text)
            if value < 0:
                control.error_text = "Value must be non-negative"
            else:
                control.error_text = None
        except ValueError:
            control.error_text = "Value must be an integer"
        self.check_validation_status()

    def check_validation_status(self):
        fields_have_values = all(
            [
                self.name.value,
                self.short_name.value,
                self.tooltip.value,
                str(self.minimum_value.value),
                str(self.maximum_value.value),
            ]
        )

        no_errors = all(
            [
                not self.name.error_text,
                not self.short_name.error_text,
                not self.tooltip.error_text,
                not self.minimum_value.error_text,
                not self.maximum_value.error_text,
            ]
        )

        all_valid = fields_have_values and no_errors
        self.action_button.disabled = not all_valid
        self.update()


class AddAttributeForm(BaseAttributeForm):
    def create_specific_fields(self):
        self.add_button = ElevatedAddButton(self.on_click_add_attribute)

    def create_layout(self):
        return self.common_layout(self.add_button)

    def on_click_add_attribute(self):
        type_ = self.type_conversion(self.name.value)
        attribute = models.Attribute(
            Type=type_,
            Name=self.name.value,
            ShortName=self.short_name.value,
            ToolTip=self.tooltip.value,
            MinimumValue=self.minimum_value.value,
            MaximumValue=self.maximum_value.value,
        )
        self.table.add_row(type_, attribute)

        # Close the dialog and show a success snack bar
        self.page.dialog.open = False
        self.page.snack_bar = SuccessSnackBar(
            "Attribute Was Added Successfully."
        ).build()
        self.page.snack_bar.open = True

        # Update the page and table
        self.page.update()
        self.table.update()


class EditAttributeForm(BaseAttributeForm):
    def create_common_fields(self):
        default_values = {
            "Name": self.attribute.Name,
            "ShortName": self.attribute.ShortName,
            "ToolTip": self.attribute.ToolTip,
            "MinimumValue": self.attribute.MinimumValue,
            "MaximumValue": self.attribute.MaximumValue,
        }
        super().create_common_fields(default_values)

    def create_specific_fields(self):
        self.update_button = ElevatedUpdateButton(self.on_click_edit_attribute)

    def create_layout(self):
        return self.common_layout(self.update_button)

    def on_click_edit_attribute(self):
        type_ = self.type_conversion(self.name.value)
        attribute = models.Attribute(
            Type=type_,
            Name=self.name.value,
            ShortName=self.short_name.value,
            ToolTip=self.tooltip.value,
            MinimumValue=self.minimum_value.value,
            MaximumValue=self.maximum_value.value,
        )
        self.table.update_row(self.attribute_key, attribute)

        # Close the dialog and show a success snack bar
        self.page.dialog.open = False
        self.page.snack_bar = SuccessSnackBar(
            "Attribute Was Updated Successfully."
        ).build()
        self.page.snack_bar.open = True

        # Update the page and table
        self.page.update()
        self.table.update()
