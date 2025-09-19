import os
import json
from pathlib import Path
from collections import defaultdict
import logging
   
# 常见视频文件扩展名
VIDEO_EXTENSIONS = {
        '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv',
        '.m4v', '.mpg', '.mpeg', '.3gp', '.3g2', '.mts', '.m2ts',
        '.vob', '.ogv', '.divx', '.rm', '.rmvb', '.asf', '.amv',
        '.m4p', '.m4v', '.svi', '.nsv', '.f4v', '.f4p', '.f4a', '.f4b'
    }


class VideoFileTree:
    """遍历目录并生成视频文件的树形数据结构"""
    def __init__(self, root_dir):
        self.root_dir = Path(root_dir).expanduser().resolve()
        self.tree = {}
        
    def is_video_file(self, path):
        """检查文件是否为视频文件"""
        return path.suffix.lower() in VIDEO_EXTENSIONS
    
    def build_tree(self):
        """构建视频文件树形结构"""
        self.tree = self._traverse_directory(self.root_dir)
        return self.tree
    
    def _traverse_directory(self, directory):
        """递归遍历目录并构建树结构"""
        tree = {
            'name': directory.name,
            'path': str(directory),
            'type': 'directory',
            'children': []
        }
        
        try:
            items = sorted(os.listdir(directory), key=lambda x: x.lower())
        except PermissionError:
            tree['error'] = 'Permission denied'
            return tree
        
        for item in items:
            item_path = directory / item
            try:
                if item_path.is_dir():
                    # 递归处理子目录
                    subtree = self._traverse_directory(item_path)
                    if subtree['children']:  # 只包含有视频文件的目录
                        tree['children'].append(subtree)
                elif item_path.is_file() and self.is_video_file(item_path):
                    # 添加视频文件
                    tree['children'].append({
                        'name': item,
                        'path': str(item_path),
                        'type': 'file',
                        'extension': item_path.suffix.lower(),
                        'size': item_path.stat().st_size
                    })
            except (OSError, PermissionError) as e:
                # 处理无法访问的文件或目录
                error_node = {
                    'name': item,
                    'path': str(item_path),
                    'type': 'error',
                    'error': str(e)
                }
                tree['children'].append(error_node)
        
        return tree
    
    def to_json(self, indent=2):
        """将树结构转换为JSON格式"""
        return json.dumps(self.tree, indent=indent, ensure_ascii=False)
    
    def print_tree(self, node=None, prefix="", is_last=True):
        """以树形格式打印目录结构"""
        if node is None:
            node = self.tree
            
        # 当前节点的显示
        connector = "└── " if is_last else "├── "
        logging.debug(prefix + connector + node['name'])
        
        if node['type'] == 'directory' and 'children' in node:
            # 更新前缀用于子节点
            new_prefix = prefix + ("    " if is_last else "│   ")
            
            # 打印所有子节点
            for i, child in enumerate(node['children']):
                self.print_tree(child, new_prefix, i == len(node['children']) - 1)


def get_video_tree(root_dir):
    """
    便捷函数：获取指定目录的视频文件树
    
    Args:
        root_dir (str): 要遍历的根目录路径
        
    Returns:
        dict: 视频文件的树形结构
    """
    tree_builder = VideoFileTree(root_dir)
    return tree_builder.build_tree()


if __name__ == "__main__":
    # 使用示例
    import sys
    
    if len(sys.argv) > 1:
        target_dir = sys.argv[1]
    else:
        target_dir = input("请输入要遍历的目录路径: ")
    
    try:
        # 创建树形结构
        tree_builder = VideoFileTree(target_dir)
        video_tree = tree_builder.build_tree()
        
        # 打印树形结构
        print(f"\n视频文件树形结构 ({target_dir}):")
        print("=" * 50)
        tree_builder.print_tree()
        
        # 可选：保存为JSON文件
        save_json = input("\n是否保存为JSON文件? (y/N): ").lower()
        if save_json == 'y':
            json_output = tree_builder.to_json()
            output_file = "video_tree.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(json_output)
            print(f"树形结构已保存到 {output_file}")
            
    except Exception as e:
        print(f"错误: {e}")