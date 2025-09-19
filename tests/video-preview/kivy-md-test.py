from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from kivy.uix.bubble import Bubble, BubbleButton
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.slider import Slider
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.switch import Switch
from kivy.uix.progressbar import ProgressBar
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button

Window.clearcolor = (0.9, 0.9, 0.9, 1)  # R,G,B,A
class LabelWidget(BoxLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        # 最简单的Label
        label1 = Label(text='Hello Kivy!')
        
        # 带样式的Label
        label2 = Label(
            text='Styled Text',
            font_size='24sp',
            color=(1, 0, 0, 1)  # RGBA格式颜色
        )
        label3 = Label(
            text='[b]Bold[/b] [i]Italic[/i] [color=ff0000]Red[/color]',
            markup=True
        )
        
        self.add_widget(label1)
        self.add_widget(label2)
        self.add_widget(label3)
 
class DropDownWidget(FloatLayout):

    def get_dropdown(self):
                # create a dropdown with 10 buttons
        dropdown = DropDown()
        for index in range(10):
            # When adding widgets, we need to specify the height manually
            # (disabling the size_hint_y) so the dropdown can calculate
            # the area it needs.

            btn = Button(text='Value %d' % index, size_hint_y=None, height=44)

            # for each button, attach a callback that will call the select() method
            # on the dropdown. We'll pass the text of the button as the data of the
            # selection.
            btn.bind(on_release=lambda btn: dropdown.select(btn.text))

            # then add the button inside the dropdown
            dropdown.add_widget(btn)
        return dropdown

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.dropdown = self.get_dropdown()
        # create a big main button
        mainbutton = Button(text='Hello', size_hint=(None, None), pos_hint={'center_x': 0.5, 'center_y': 0.5})
            # show the dropdown menu when the main button is released
            # note: all the bind() calls pass the instance of the caller (here, the
            # mainbutton instance) as the first argument of the callback (here,
            # dropdown.open.).
        mainbutton.bind(on_release=self.dropdown.open)

        self.add_widget(mainbutton)
            # one last thing, listen for the selection in the dropdown list and
            # assign the data to the button text.
        self.dropdown.bind(on_select=lambda instance, x: setattr(mainbutton, 'text', x))

class MyPopup(Popup):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.title="弹框"
        self.size_hint_x = 0.9
        self.size_hint_y = 0.9
        bx = BoxLayout()
        bx.orientation = 'vertical'
        bx.add_widget(Button(text="啥也没有的按钮"))
        cl = Button(text="close")
        cl.bind(on_press=self.dismiss)
        bx.add_widget(cl)

        self.add_widget(bx)

        self.bind(on_dismiss=lambda enx: print(enx))



class PopupWidget(BoxLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'

        self.add_widget(Widget())
        bt = Button(text="popup")
        bt.size_hint_y=0.2

        self.add_widget(bt)

        bt.bind(on_press=self.clicked)
    def clicked(self, ins):
        MyPopup().open()

    


class SpinnerWidget(BoxLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        spinner = Spinner(
            # default value shown
            text='Home',
            # available values
            values=('Home', 'Work', 'Other', 'Custom'),
            # just for positioning in our example
            size_hint=(None, None),
            size=(100, 44),
            pos_hint={'center_x': .8, 'center_y': .1})
        spinner.bind(text=self.show_selected_value)
        self.add_widget(spinner)

    def show_selected_value(self, spinner, text):
        print('The spinner', spinner, 'has text', text)

class ProgressBarWidget(BoxLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.i = 0

        self.orientation = 'vertical'
        pb = ProgressBar(max=100, value=50)
        self.add_widget(pb)
        btn = Button(text="add value")
        btn.bind(on_press=self.clicked)
        self.add_widget(btn)
        
        btn2 = Button(text="减小 value")
        btn2.bind(on_press=self.clicked2)
        self.add_widget(btn2)


        self.btn = btn
        self.pb = pb

 
    def clicked(self, arg):
       self.pb.value += 1
       print(self.pb.value )
    def clicked2(self, arg):
       self.pb.value -= 1
       print(self.pb.value )


class SwitchWidget(BoxLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        switch = Switch(active=True)
        switch.bind(active=self.callback)
        self.add_widget(switch)
    def callback(self, instance, value):
        print('the switch', instance, 'is', value)


class CheckBoxWidget(BoxLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        checkbox = CheckBox(color=(1,1,.2,1), active=True)
        checkbox.bind(active=self.on_checkbox_active)
        self.add_widget(checkbox)

        
        checkbox2 = CheckBox(color=(1,0.1,.2,1), active=True)
        checkbox2.bind(active=self.on_checkbox_active)
        self.add_widget(checkbox2)

        bx = BoxLayout()

        btn1 = ToggleButton(text='Male', group='sex',)
        btn2 = ToggleButton(text='Female', group='sex', state='down')
        btn3 = ToggleButton(text='Mixed', group='sex')
        bx.add_widget(btn1)
        bx.add_widget(btn2)
        bx.add_widget(btn3)
        self.add_widget(bx)

    def on_checkbox_active(self,checkbox,value):
        if value:
            print('The checkbox',checkbox,'is active')
        else:
            print('the checkbox',checkbox,'is inactive')

from kivy.uix.textinput import TextInput
class TextInputWidget(BoxLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.orientation='vertical'
        ti = TextInput(text='copy.com', size_hint=(0.1, 0.1))  # 占父容器的80%宽度和20%高度)
        self.add_widget(ti)
        textinput = TextInput(
            multiline=False,
            size_hint=(None, None),  # 禁用自动尺寸
            size=(300, 50),         # 固定宽度300px，高度50px
        )
        self.add_widget(textinput)
        self.add_widget(Widget())

class SliderWidget(BoxLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.orientation='vertical'
 
        sl = Slider(min = 0,max = 100)
        sl.value_track = True
        sl.value_track_width = '5dp'
        sl.value_track_color = (1, 0, 0 , 1)
        self.add_widget(sl)
        label = Label(text=f"范围: {sl.min}-{sl.max}")
        sl.bind(value=self.update_range)
        self.add_widget(label)
        self.label = label

    def update_range(self, instance, value):
        self.label.text = f"范围: {instance.min}-{instance.max} currnt value: {value:.2f}"

class BubbleWidget(Bubble):
    def __init__(self, **kwargs):
        super(BubbleWidget, self).__init__(**kwargs)
        
        # 创建布局容器
        layout = BoxLayout(orientation='horizontal')
        
        # 添加多个按钮到布局
        btn1 = BubbleButton(text='Button 1')
        btn1.bind(on_release=lambda x: print('Button 1'))
        
        btn2 = BubbleButton(text='Button 2', color=(1,0,0,1))
        btn2.bind(on_release=lambda x: print('Button 2'))
        
        layout.add_widget(btn1)
        layout.add_widget(btn2)
        
        # 将布局（唯一子控件）添加到 Bubble
        self.add_widget(layout)

class MyTabbedPanel(TabbedPanel):
    def __init__(self, **kwargs):
        super(MyTabbedPanel, self).__init__(**kwargs)
        self.do_default_tab = False

        # 设置标签页位置 (默认在顶部)
        self.tab_pos = 'top_left'
        self.tab_width = '100dp'
        self.background_image = '1.png'
        # 设置选项卡条颜色
        self.strip_color = (0, 1, 0, 1 )  # 蓝绿色
 
        # 添加标签页
        tab1 = TabbedPanelItem(text='Bubble')
        tab1.background_color=(0.5,0.5,0.5,1)
        bw = BubbleWidget()
        tab1.add_widget(bw)
        self.add_widget(tab1)

        self.add_tab('Slider', SliderWidget())
        self.add_tab('TextInput', TextInputWidget())
        self.add_tab('CheckBox', CheckBoxWidget())
        self.add_tab('Switch', SwitchWidget())
        self.add_tab('ProgressBar', ProgressBarWidget())
        self.add_tab('Spinner', SpinnerWidget())
        self.add_tab('Popup', PopupWidget())
        self.add_tab('DropDown', DropDownWidget())
        self.add_tab('Label', LabelWidget())

        self.default_tab = tab1

    def add_tab(self, t, widg):
        tab = TabbedPanelItem(text=t)
        tab.add_widget(widg)
        self.add_widget(tab)

class TabbedPanelApp(App):
    def build(self):
        return MyTabbedPanel()

if __name__ == '__main__':
    TabbedPanelApp().run()
