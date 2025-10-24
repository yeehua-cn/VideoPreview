import logging

from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import ListProperty, NumericProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image

logger = logging.getLogger(__name__)

Builder.load_string(
    """

<ImagesViewer>:
    BoxLayout:
        size: root.size
        pos: root.pos
        orientation: "vertical"
        Carousel:
            id: images_carousel
            direction:'right'

"""
)


# 缩略图片
class Thumbnail(ButtonBehavior, Image):
    def __init__(self, index, **kwargs):
        super(Thumbnail, self).__init__(**kwargs)
        self.index = index


# 图片列表预览
class ImagesViewer(FloatLayout):
    __events__ = ("on_canceled", "on_confirmed")
    images = ListProperty([])
    index = NumericProperty(0)

    def __init__(self, images, index=0, **kwargs):
        super(ImagesViewer, self).__init__(**kwargs)
        self.images = images
        self.index = index
        # 请求键盘监听
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down)
        # 渲染图片
        self._render_images()
        self.show_images(self.index)

    def on_canceled(self):
        pass

    def on_confirmed(self):
        pass

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_key_down)
        self._keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        logger.debug(f"keycode: {keycode}, text: {text}, modifiers: {modifiers}")
        if keycode[1] == "left":
            self.ids.images_carousel.load_previous()
        elif keycode[1] == "right":
            self.ids.images_carousel.load_next(mode="next")
        else:
            return False

    def _render_images(self):
        for image in self.images:
            logger.debug(f"Render image: {image}")
            self.ids.images_carousel.add_widget(Image(source=image, fit_mode="contain"))

    def show_images(self, index):
        self.ids.images_carousel.index = index
