import logging

from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.progressbar import ProgressBar

logger = logging.getLogger(__name__)


# 进度展示
class ProgressViewer(BoxLayout):
    title_text = StringProperty("Progress")
    on_update_value = ObjectProperty()
    on_complete = ObjectProperty()

    def __init__(self, title_text, on_update_value, on_complete, **kwargs):
        super(ProgressViewer, self).__init__(**kwargs)

        self.modal_view = ModalView(
            auto_dismiss=False, size_hint=(None, None), size=(400, 50)
        )
        self.progress_bar = ProgressBar(max=1, value=0)

        self.grid = GridLayout(cols=1, padding=10)
        self.grid.add_widget(
            Label(
                text=title_text,
                font_size=12,
            )
        )
        self.grid.add_widget(self.progress_bar)
        self.modal_view.add_widget(self.grid)
        self.modal_view.open()
        self.on_update_value = on_update_value
        self.on_complete = on_complete
        self.update_event = Clock.schedule_interval(self._update_value, 1.0)

    def update_progress_value(self, value):
        self.progress_bar.value = value

    def on_dismiss(self):
        if self.update_event is not None:
            self.update_event.cancel()
        self.modal_view.dismiss()

    def _update_value(self, dt):
        self.on_update_value()
        logger.debug(f"Progress viewer value : {self.progress_bar.value}")
        if self.progress_bar.value >= 1:
            self.on_complete()
            self.on_dismiss()
