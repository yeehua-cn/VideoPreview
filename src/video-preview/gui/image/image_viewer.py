import logging

from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image

Builder.load_string(
    """

<ViewPreviewImageDialog>:
    BoxLayout:
        size: root.size
        pos: root.pos
        orientation: "vertical"
        Carousel:
            id: preview_image_carousel
            direction:'right'

"""
)


class ThumbnailImage(ButtonBehavior, Image):
    def __init__(self, index, **kwargs):
        super(ThumbnailImage, self).__init__(**kwargs)
        self.index = index


class ViewPreviewImageDialog(FloatLayout):
    close = ObjectProperty(None)

    def render_images(self, images_array):
        for thumbnail in images_array:
            logging.debug(f"  render video thumbnail: {thumbnail}")
            self.ids.preview_image_carousel.add_widget(
                Image(source=thumbnail, fit_mode="contain")
            )

    def show_images(self, index):
        self.ids.preview_image_carousel.index = index
