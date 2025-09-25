from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder

class KivyGuiApp(App):
    def build(self):
        return root_widget

class MyBox(BoxLayout):
    def print_ids(self, *args):
        print("\nids:")
        for widget in self.walk():
            print("{} -> {}".format(widget, widget.ids))
    def print_names(self, *args):
        print("\nnames:")
        for widget in self.walk():
            print("{} -> {}".format(widget, widget.name))

root_widget = Builder.load_string("""
MyBox:
    id: screen_manager
    name: 'screen_manager'

    SimpleLayout:
        id: simple_layout
        name: 'simple_layout'

<SimpleLayout@BoxLayout>:
    id: simple_layout_rule
    name: 'simple_layout_rule'
    Button:
        id: button_ids
        name: 'button_ids'
        text: 'print ids to console'
        on_release: app.root.print_ids()
    Button:
        id: button_names
        name: 'button_names'
        text: 'print names to console'
        on_release: app.root.print_names()
""")

if __name__ == '__main__':
    KivyGuiApp().run()

