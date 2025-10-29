import logging

from core.model import FileInfoTree
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.treeview import TreeView, TreeViewLabel
from kivy.uix.widget import Widget

logger = logging.getLogger(__name__)


# 树枝标签
class TreeBranchLabel(ButtonBehavior, TreeViewLabel):
    def __init__(self, path, **kwargs):
        super(TreeBranchLabel, self).__init__(**kwargs)
        self.path = path


# 文件树预览
class FileTreeViewer(Widget):
    on_selected = ObjectProperty()

    def __init__(self, tree_size, tree_data: FileInfoTree, on_selected, **kwargs):
        super(FileTreeViewer, self).__init__(**kwargs)
        self.tree_size = tree_size
        self.tree_data = tree_data
        self.on_selected = on_selected
        self.file_info_dict = {}
        # 渲染文件树
        self._render_tree(self.tree_data)

    def _render_tree(self, tree_data: FileInfoTree):
        self.treeview = TreeView(
            hide_root=True,
            size_hint=(None, None),
            size=self.tree_size,
        )
        logging.debug(f"FileTreeViewer tree_size: {self.tree_size}")
        self.treeview.bind(minimum_height=self.treeview.setter("height"))
        self.treeview.bind(minimum_width=self.treeview.setter("width"))
        self._populate_tree(None, tree_data)

    def _populate_tree(self, parent, node_data):
        logging.debug(
            f"_populate_tree: parent={parent}, node={node_data.name}, path={node_data.path}"
        )

        node_label = TreeBranchLabel(
            text=node_data.name,
            path=node_data.path,
            is_open=True,
        )
        node_label.bind(on_press=self._on_selected)

        if parent is None:
            tree_node = self.treeview.add_node(node_label)
        else:
            tree_node = self.treeview.add_node(node_label, parent)

        if node_data.type == "directory":
            for child_node in node_data.children:
                self._populate_tree(tree_node, child_node)

        self.file_info_dict[node_data.path] = node_data

    def _on_selected(self, instance):
        # logging.debug(f"File info: [{instance.path}] has been selected !")
        select_file_info = self.file_info_dict[instance.path]
        logging.debug(
            f"Select file info: path = [{select_file_info.path}], type = [{select_file_info.type}]"
        )
        if self.on_selected:
            self.on_selected(select_file_info)

    def get_treeview(self):
        return self.treeview
