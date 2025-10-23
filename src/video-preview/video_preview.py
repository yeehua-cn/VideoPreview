import _thread
import logging
import os
import time

from gui.file.file_browser import FileBrowser, get_home_directory
from gui.file.file_list import TreeBranchLabel
from gui.image.image_viewer import ThumbnailImage, ViewPreviewImageDialog
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.treeview import TreeView
from kivy.uix.videoplayer import VideoPlayer
from utils.file_util import get_image_files
from utils.sequence_generator import SequenceGenerator
from utils.video_file_util import VideoFileTree
from utils.video_meta_util import OpenCVVideoInfoExtractor

Window.size = (1366, 768)


class Root(FloatLayout):
    videoInfoExtractor = OpenCVVideoInfoExtractor()
    sequenceGenerator = SequenceGenerator()
    folder = None
    choose_video_info = None
    choose_video_meta_info = None
    video_info_dict = {}
    video_treeview = None
    processModalView = None
    generateProgressBar = None
    generateProgressBarEvent = None
    viewPreviewImageDialog = None
    generate_thumbnails_array = []
    video_thumbnails_widget_list = []

    def dismiss_popup(self):
        self._popup.dismiss()

    def filebrowser_dismiss_popup(self, instance):
        self._popup.dismiss()

    def show_choose_folder(self):
        user_path = os.path.join(get_home_directory(), "Documents")
        content = FileBrowser(
            select_string="选择",
            cancel_string="取消",
            favorites=[(user_path, "Documents")],
            filters=["!*"],
            dirselect=True,
        )
        content.bind(
            on_success=self.choose_folder, on_canceled=self.filebrowser_dismiss_popup
        )
        self._popup = Popup(title="选择文件夹", content=content, size_hint=(0.9, 0.9))
        self._popup.open()

    def show_setting(self):
        logging.info(f"pop setting")

    def show_preview_image(self, instance):
        # 显示视频缩略图
        content = ViewPreviewImageDialog(close=self.dismiss_popup)
        content.render_images(self.generate_thumbnails_array)
        content.show_images(instance.index)
        self._popup = Popup(title="预览图片", content=content, size_hint=(0.9, 0.9))
        self._popup.open()

    def choose_folder(self, instance):
        logging.info(
            f"choose_folder: path={instance.path}, filename={instance.filename}"
        )
        self.folder = instance.filename
        self.video_info_dict = {}
        if self.video_treeview is not None:
            self.ids.file_tree_layout_view.remove_widget(self.video_treeview)

        self.dismiss_popup()
        self.load_video_tree(self.folder)

    def load_video_tree(self, path):
        tree_builder = VideoFileTree(path)
        video_tree_data = tree_builder.build_tree()
        # tree_builder.print_tree()
        self._render_video_tree(video_tree_data)

    def _render_video_tree(self, video_tree_data):
        self.video_treeview = TreeView(
            hide_root=True,
            size_hint=(None, None),
            size=(self.parent.width, self.parent.height),
        )
        self.video_treeview.bind(minimum_height=self.video_treeview.setter("height"))
        self.video_treeview.bind(minimum_width=self.video_treeview.setter("width"))
        self._populate_video_tree(self.video_treeview, None, video_tree_data)

        self.ids.file_tree_layout_view.add_widget(self.video_treeview)

    def _populate_video_tree(self, tree_view, parent, node_data):
        logging.debug(
            f"_populate_video_tree: parent={parent}, node={node_data['name']}, path={node_data['path']}"
        )

        path_node = TreeBranchLabel(
            path=node_data["path"],
            text=node_data["name"],
            is_open=True,
        )
        path_node.bind(on_press=self.choose_video_file)

        if parent is None:
            tree_node = tree_view.add_node(path_node)
        else:
            tree_node = tree_view.add_node(path_node, parent)

        if node_data["type"] == "directory" and "children" in node_data:
            for child_node in node_data["children"]:
                self._populate_video_tree(tree_view, tree_node, child_node)
        else:
            self.video_info_dict[node_data["path"]] = node_data

    def choose_video_file(self, path):
        logging.info(f"Video file: [{path}] has been chosen !")
        self.ids.video_player.state = "stop"
        self.show_video_info(path)
        self.load_video_thumbnails(path)

    def show_video_info(self, path):
        if path not in self.video_info_dict:
            return

        self.choose_video_info = self.video_info_dict[path]
        self.choose_video_meta_info = self.videoInfoExtractor.get_video_info(path)

        logging.info(
            f"video_file_info: {self.choose_video_info} . choose_video_meta_info: {self.choose_video_meta_info}"
        )
        self.ids.show_video_name.text = self.choose_video_meta_info.filename
        self.ids.show_video_type.text = self.choose_video_info["extension"]
        self.ids.show_video_size.text = self.choose_video_meta_info.pretty_size
        self.ids.show_video_duration.text = self.choose_video_meta_info.time_duration
        self.ids.show_video_resolution.text = self.choose_video_meta_info.resolution
        self.ids.show_video_fps.text = str(self.choose_video_meta_info.fps)
        self.play_video(path)

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
        seq = self.get_video_time_seq()
        file_name = self.choose_video_info["name"]
        output_dir = self.get_thumbnails_folder(self.choose_video_info["path"])
        logging.info(
            f"Generate thumbnails for video seq : {seq} , output_dir: {output_dir}"
        )

        thumbnails = self.videoInfoExtractor.generate_thumbnails_at_times(
            self.choose_video_info["path"],
            seq,
            output_dir,
            prefix=file_name + "-" + "thumbnail",
            format="jpg",
            quality=95,
        )
        logging.info(f"Generate thumbnails: {thumbnails}")
        self.generate_thumbnails_array = []
        for time_point, file_path in thumbnails.items():
            self.generate_thumbnails_array.append(file_path)

    def show_generate_thumbnails_process(self):
        # 显示生成进度
        self.processModalView = ModalView(
            auto_dismiss=False, size_hint=(None, None), size=(400, 50)
        )
        processGrid = GridLayout(cols=1, padding=10)
        processGrid.add_widget(
            Label(
                text="生成预览图进度",
                font_size=12,
            )
        )
        self.generateProgressBar = ProgressBar(max=1, value=0)
        processGrid.add_widget(self.generateProgressBar)
        self.processModalView.add_widget(processGrid)
        self.processModalView.open()
        self.generateProgressBarEvent = Clock.schedule_interval(
            self.update_generate_progress, 1.0
        )

    def update_generate_progress(self, dt):
        # 生成预览图进度更新
        progress = self.videoInfoExtractor.get_generate_thumbnails_at_times_progress()
        self.generateProgressBar.value = progress
        logging.debug(f" update_generate_progress: {progress}")
        if progress >= 1:
            if self.generateProgressBarEvent is not None:
                self.generateProgressBarEvent.cancel()

            self.render_thumbnails(self.generate_thumbnails_array)
            self.processModalView.dismiss()

    def get_thumbnails_folder(self, video_path):
        # 预览图存储目录
        return video_path + "-" + "thumbnails"

    def load_video_thumbnails(self, video_path):
        # 获取目录下的所有图片文件
        image_files = get_image_files(self.get_thumbnails_folder(video_path))
        logging.info(f"  load exists thumbnails: {image_files}")

        thumbnails_array = []
        for image_info in image_files:
            thumbnails_array.append(image_info.path)

        self.render_thumbnails(thumbnails_array)
        self.generate_thumbnails_array = thumbnails_array

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
            thumbnail_image = ThumbnailImage(
                index=index,
                source=thumbnail,
                size_hint=(None, 1),
                on_release=self.show_preview_image,
            )
            self.video_thumbnails_widget_list.append(thumbnail_image)
            self.ids.video_thumbnails_layout.add_widget(thumbnail_image)
            index += 1

    def get_video_time_seq(self):
        #  生成视频预览图片的时间序列
        logging.info(
            f"choose video time duration: {self.choose_video_meta_info.duration}"
        )
        if self.choose_video_meta_info.duration <= 3:
            return self.sequenceGenerator.generate_uniform_sequence(
                self.choose_video_meta_info.duration, 1
            )
        if self.choose_video_meta_info.duration <= 30:
            return self.sequenceGenerator.generate_uniform_sequence(
                self.choose_video_meta_info.duration, 3
            )
        elif self.choose_video_meta_info.duration <= 300:
            return self.sequenceGenerator.generate_uniform_sequence(
                self.choose_video_meta_info.duration, 6
            )
        else:
            return self.sequenceGenerator.generate_uniform_sequence(
                self.choose_video_meta_info.duration, 10
            )


class VideoPreviewApp(App):
    pass


Factory.register("Root", cls=Root)
Factory.register("ViewPreviewImageDialog", cls=ViewPreviewImageDialog)


if __name__ == "__main__":
    VideoPreviewApp().run()
