import app.core.styles as styles
import flet as ft


class Slider(ft.UserControl):
    def __init__(self, label: str, min_value: int, max_value: int, tooltip: str = None):
        super().__init__()
        self.text_value = ft.Text(
            value=str(min_value), **styles.SliderValueStyle().to_dict()
        )
        self.slider = ft.Slider(
            value=min_value,
            min=min_value,
            max=max_value,
            divisions=max_value - min_value,
            height=50,
            width=350,
            thumb_color=styles.ColorPalette.ACCENT,
            on_change=lambda event: self.slider_changed(event),
            tooltip=tooltip,
        )
        self.label = label

    def build(self):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(self.label, **styles.SliderLabelStyle().to_dict()),
                            self.text_value,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    self.slider,
                ],
            ),
        )


class TemperatureSlider(Slider):
    def __init__(self):
        super().__init__(
            label="Temperature",
            min_value=0.0,
            max_value=1.0,
            tooltip="""Controls randomness: Lowering results in less random\ncompletions. As the temperature approaches zero, the\nmodel will become deterministic and repetitive. Higher\ntemperature nresults in more random completions.""",  # noqa
        )

    def slider_changed(self, event: ft.ControlEvent):
        self.text_value.value = str(round(event.control.value, 2))
        self.update()


class MaximumLengthSlider(Slider):
    def __init__(self):
        super().__init__(
            label="Maximum length",
            min_value=1,
            max_value=4096,
            tooltip="""Controls the maximum number of tokens that the\ncompletion may contain. Tokens are roughly equal to\nwords.""",  # noqa
        )

    def slider_changed(self, event: ft.ControlEvent):
        self.text_value.value = int(event.control.value)
        self.update()
