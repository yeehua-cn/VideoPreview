from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.colorpicker import ColorPicker
from kivy.core.window import Window

Window.size = (720, 350)


class ColorPickApp(App):
    def build(self):
        self.layout = GridLayout(cols=1, padding=10)
        self.l1 = Label(
            text="www.colorpick.com", font_size=32, color=[0.8, 0.6, 0.4, 1]
        )
        self.layout.add_widget(self.l1)
        self.button = Button(text="Click Here")
        self.layout.add_widget(self.button)
        self.button.bind(on_press=self.onButtonPress)
        return self.layout

    def onButtonPress(self, button):
        layout = GridLayout(cols=1, padding=10)

        self.clr = ColorPicker()
        closeButton = Button(text="OK", size_hint=(0.1, 0.05))

        layout.add_widget(self.clr)
        layout.add_widget(closeButton)

        self.popup = Popup(title="Hello", content=layout, auto_dismiss=False)
        self.popup.open()

        closeButton.bind(on_press=self.on_close)

    def on_close(self, event):
        self.l1.color = self.clr.hex_color
        self.popup.dismiss()


ColorPickApp().run()
