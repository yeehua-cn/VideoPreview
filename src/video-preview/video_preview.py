import _thread
import logging
import os

from core.preview_image import PreviewImage
from gui.base.progress_viewer import ProgressViewer
from gui.file.file_browser import FileBrowser, get_home_directory
from gui.file.file_list import FileTreeViewer
from gui.image.image_viewer import ImagesViewer, Thumbnail
from kivy.app import App
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from utils.file_util import get_video_tree
from utils.video_meta_util import VideoInfoExtractor

Window.size = (1366, 768)


class Root(FloatLayout):
    videoInfoExtractor = VideoInfoExtractor()
    folder = None
    choose_video_info = None
    choose_video_meta_info = None
    video_treeview = None
    generate_thumbnails_array = []
    video_thumbnails_widget_list = []

    def dismiss_popup(self):
        self._popup.dismiss()

    def filebrowser_dismiss_popup(self, instance):
        self._popup.dismiss()

    def show_choose_folder(self):
        user_path = os.path.join(get_home_directory(), "Documents")
        browser = FileBrowser(
            select_string="选择",
            cancel_string="取消",
            favorites=[(user_path, "Documents")],
            filters=["!*"],
            dirselect=True,
        )
        browser.bind(
            on_success=self.choose_folder, on_canceled=self.filebrowser_dismiss_popup
        )
        self._popup = Popup(title="选择文件夹", content=browser, size_hint=(0.9, 0.9))
        self._popup.open()

    def show_setting(self):
        logging.info(f"pop setting")

    def show_preview_image(self, instance):
        # 显示视频缩略图
        viewer = ImagesViewer(
            images=self.generate_thumbnails_array, index=instance.index
        )
        viewer.bind(on_canceled=self.dismiss_popup)

        self._popup = Popup(title="预览图片", content=viewer, size_hint=(0.9, 0.9))
        self._popup.open()

    def choose_folder(self, instance):
        logging.info(
            f"choose_folder: path={instance.path}, filename={instance.filename}"
        )
        self.folder = instance.filename
        if self.video_treeview is not None:
            self.ids.file_tree_layout_view.remove_widget(self.video_treeview)

        self.dismiss_popup()
        self.load_video_tree(self.folder)

    def load_video_tree(self, path):
        video_tree_data = get_video_tree(path)
        self.video_viewer = FileTreeViewer(
            tree_size=self.parent.size,
            tree_data=video_tree_data,
            on_selected=self.choose_video_file,
        )
        self.video_treeview = self.video_viewer.get_treeview()
        self.ids.file_tree_layout_view.add_widget(self.video_treeview)

    def choose_video_file(self, file_info):
        logging.info(f"Video file: [{file_info.path}] has been chosen !")
        if file_info.type == "directory":
            return

        self.choose_video_info = file_info
        self.ids.video_player.state = "stop"
        self.show_video_info(file_info)

        thumbnails_array = PreviewImage.load_video_thumbnails(file_info.path)
        self.generate_thumbnails_array = thumbnails_array
        self.render_thumbnails(thumbnails_array)

    def show_video_info(self, file_info):
        self.choose_video_meta_info = self.videoInfoExtractor.get_video_info(
            file_info.path
        )

        logging.info(f"video_meta_info: {self.choose_video_meta_info}")
        self.ids.show_video_name.text = self.choose_video_meta_info.filename
        self.ids.show_video_type.text = file_info.extension
        self.ids.show_video_size.text = self.choose_video_meta_info.pretty_size
        self.ids.show_video_duration.text = self.choose_video_meta_info.time_duration
        self.ids.show_video_resolution.text = self.choose_video_meta_info.resolution
        self.ids.show_video_fps.text = str(self.choose_video_meta_info.fps)
        self.play_video(file_info.path)

    def play_video(self, path):
        self.ids.video_player.source = path
        self.ids.video_player.state = "play"
        self.ids.video_player.options = {"eos": "loop"}
        self.ids.video_player.allow_stretch = True

    def generate_thumbnail(self):
        # 生成 视频预览图片
        if self.choose_video_info is None:
            logging.warning(f"Please choose a video file first !")
            return

        self.ids.video_player.state = "stop"
        self.show_generate_thumbnails_process()
        _thread.start_new_thread(self.do_generate_thumbnail, ())

    def do_generate_thumbnail(self):
        self.generate_thumbnails_array = PreviewImage.generate_thumbnails(
            self.videoInfoExtractor, self.choose_video_meta_info
        )

    def show_generate_thumbnails_process(self):
        self.progress_viewer = ProgressViewer(
            title_text="生成预览图进度",
            on_update_value=self.update_generate_progress,
            on_complete=self.video_thumbnails_generate_complete,
        )

    def update_generate_progress(self):
        # 生成预览图进度更新
        progress = self.videoInfoExtractor.get_generate_thumbnails_at_times_progress()
        logging.debug(f" update_generate_progress: {progress}")
        self.progress_viewer.update_progress_value(progress)

    def video_thumbnails_generate_complete(self):
        self.render_thumbnails(self.generate_thumbnails_array)

    def render_thumbnails(self, thumbnails_array):
        self.ids.video_thumbnails_layout.bind(
            minimum_width=self.ids.video_thumbnails_layout.setter("width")
        )

        # 清理已经加载的缩略图列表
        for thumbnail_image in self.video_thumbnails_widget_list:
            self.ids.video_thumbnails_layout.remove_widget(thumbnail_image)

        self.video_thumbnails_widget_list.clear()

        # 重新加载的缩略图列表
        index = 0
        for thumbnail in thumbnails_array:
            logging.debug(f"  add thumbnail: {thumbnail}")
            thumbnail_image = Thumbnail(
                index=index,
                source=thumbnail,
                size_hint=(None, 1),
                on_release=self.show_preview_image,
            )
            self.video_thumbnails_widget_list.append(thumbnail_image)
            self.ids.video_thumbnails_layout.add_widget(thumbnail_image)
            index += 1


class VideoPreviewApp(App):
    pass


Factory.register("Root", cls=Root)
Factory.register("ImagesViewer", cls=ImagesViewer)


if __name__ == "__main__":
    VideoPreviewApp().run()
