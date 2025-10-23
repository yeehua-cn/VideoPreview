from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.treeview import TreeViewLabel


class TreeBranchLabel(ButtonBehavior, TreeViewLabel):
    def __init__(self, path, **kwargs):
        super(TreeBranchLabel, self).__init__(**kwargs)
        self.path = path
