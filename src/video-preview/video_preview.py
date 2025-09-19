from kivy.app import App
from kivy.core.window import Window
from kivy.uix.treeview import TreeView, TreeViewNode,TreeViewLabel
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from utils.video_file_util import VideoFileTree

import os

import logging

Window.size = (1366, 768)


class ChooseFolderDialog(FloatLayout):
    choose = ObjectProperty(None)
    cancel = ObjectProperty(None)


class SaveDialog(FloatLayout):
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)


class TreeViewButton(Button, TreeViewNode):
    def __init__(self, **kwargs):
        super(TreeViewButton, self).__init__(**kwargs)
        self.file_path = None


class Root(FloatLayout):
    folder = None
    video_treeview = None
    loadfile = ObjectProperty(None)
    savefile = ObjectProperty(None)
    text_input = ObjectProperty(None)

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_choose_folder(self):
        content = ChooseFolderDialog(choose=self.choose_folder, cancel=self.dismiss_popup)
        self._popup = Popup(title="选择文件夹", content=content, size_hint=(0.9, 0.9))
        self._popup.open()

    def show_setting(self):
        logging.info(f"pop setting")

    def show_save(self):
        content = SaveDialog(save=self.save, cancel=self.dismiss_popup)
        self._popup = Popup(title="Save file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def choose_folder(self, path, filename):
        self.folder = path
        logging.info(f"choose_folder: path={self.folder}, filename={filename}")
        if self.video_treeview is not None:
            self.ids.video_tree_layout.remove_widget(self.video_treeview)
        self.dismiss_popup()
        self.load_video_tree(self.folder)
        # self.ids.file_layout_view.bind(minimum_height=self.ids.file_layout_view.setter('height'))

    def load_video_tree(self,path):
        tree_builder = VideoFileTree(path)
        video_tree = tree_builder.build_tree()
        # tree_builder.print_tree()
        self._render_video_tree(video_tree)
        
    def _render_video_tree(self, video_tree):
        self.video_treeview=TreeView(hide_root=True)
        self.ids.video_tree_layout.add_widget( self.video_treeview)
        self._populate_video_tree( self.video_treeview, None, video_tree)

    def _populate_video_tree(self,tree_view, parent, node):
        logging.debug(f"_populate_video_tree: parent={parent}, node={node['name']}")
        if parent is None:
            tree_node = tree_view.add_node(TreeViewLabel(text=node['name'],is_open=True))
        else:
            tree_node = tree_view.add_node(TreeViewLabel(text=node['name'],is_open=True), parent)

        if node['type'] == 'directory' and 'children' in node:
            for child_node in node['children']:
                self._populate_video_tree(tree_view, tree_node, child_node)


    def save(self, path, filename):
        with open(os.path.join(path, filename), 'w') as stream:
            stream.write(self.text_input.text)

        self.dismiss_popup()


    def select_file(self, path, filename):
        logging.info(f"select_file:")


class VideoPreviewApp(App):
    pass


Factory.register('Root', cls=Root)
Factory.register('ChooseFolderDialog', cls=ChooseFolderDialog)
Factory.register('SaveDialog', cls=SaveDialog)



if __name__ == '__main__':
    VideoPreviewApp().run()