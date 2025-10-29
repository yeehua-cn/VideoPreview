import json
import logging
import os
from pathlib import Path
from typing import Callable, List, Optional

from core.model import FileInfo, FileInfoTree
from utils.time_util import timestamp_to_str

logger = logging.getLogger(__name__)


class ImageDirectoryReader:
    """目录图片文件读取工具类"""

    # 常见图片文件扩展名
    IMAGE_EXTENSIONS = {
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".tiff",
        ".tif",
        ".webp",
        ".svg",
        ".ico",
        ".raw",
        ".cr2",
        ".nef",
        ".arw",
        ".dng",
        ".heic",
        ".heif",
        ".avif",
        ".jp2",
        ".j2k",
        ".pbm",
        ".pgm",
        ".ppm",
        ".pnm",
        ".hdr",
        ".exr",
        ".psd",
        ".ai",
        ".eps",
    }

    def __init__(self, follow_symlinks: bool = False):
        """
        初始化图片目录读取器

        Args:
            follow_symlinks (bool): 是否跟随符号链接
        """
        self.follow_symlinks = follow_symlinks

    def is_directory(self, path: str) -> bool:
        """
        判断给定路径是否为目录

        Args:
            path (str): 要检查的路径

        Returns:
            bool: 如果是目录则返回True，否则返回False
        """
        try:
            path_obj = Path(path)
            return path_obj.is_dir()
        except (OSError, TypeError):
            return False

    def is_image_file(self, filename: str) -> bool:
        """
        判断文件是否为图片文件

        Args:
            filename (str): 文件名或路径

        Returns:
            bool: 如果是图片文件则返回True
        """
        return Path(filename).suffix.lower() in self.IMAGE_EXTENSIONS

    def get_image_files(
        self,
        directory: str,
        recursive: bool = False,
        sort_by: str = "name",
        reverse: bool = False,
        filter_func: Optional[Callable] = None,
    ) -> List[FileInfo]:
        """
        获取目录下的图片文件列表

        Args:
            directory (str): 目录路径
            recursive (bool): 是否递归搜索子目录
            sort_by (str): 排序方式，可选值: "name", "size", "modified", "extension"
            reverse (bool): 是否反向排序
            filter_func (Callable, optional): 自定义过滤函数

        Returns:
            List[FileInfo]: 图片文件信息列表

        Raises:
            ValueError: 如果目录不存在或不是目录
            PermissionError: 如果没有目录访问权限
        """
        # 检查目录是否存在
        if not self.is_directory(directory):
            return []

        directory_path = Path(directory).resolve()

        # 检查目录访问权限
        if not os.access(directory_path, os.R_OK):
            raise PermissionError(f"没有读取目录的权限: {directory}")

        image_files = []

        try:
            # 根据是否递归选择遍历方法
            if recursive:
                file_iterator = directory_path.rglob("*")
            else:
                file_iterator = directory_path.iterdir()

            for item in file_iterator:
                try:
                    # 跳过目录（除非递归模式下需要处理子目录中的文件）
                    if item.is_dir() and not recursive:
                        continue

                    # 只处理文件
                    if item.is_file() and self.is_image_file(item.name):
                        # 获取文件信息
                        stat = item.stat()
                        file_info = FileInfo(
                            name=item.name,
                            path=str(item),
                            type="file",
                            extension=item.suffix.lower(),
                            size=stat.st_size,
                            pretty_size=SizeFormatter.format_size(stat.st_size),
                            modified_time=stat.st_mtime,
                            pretty_modified_time=timestamp_to_str(stat.st_mtime),
                        )

                        # 应用自定义过滤函数（如果提供）
                        if filter_func is None or filter_func(file_info):
                            image_files.append(file_info)

                except (OSError, PermissionError) as e:
                    # 跳过无法访问的文件
                    logger.warning(f"警告: 无法访问文件 {item}: {e}")
                    continue

        except (OSError, PermissionError) as e:
            raise PermissionError(f"无法读取目录内容: {e}")

        # 排序
        image_files = self._sort_files(image_files, sort_by, reverse)

        return image_files

    def _sort_files(
        self, files: List[FileInfo], sort_by: str, reverse: bool
    ) -> List[FileInfo]:
        """
        对文件列表进行排序

        Args:
            files (List[FileInfo]): 文件列表
            sort_by (str): 排序字段
            reverse (bool): 是否反向排序

        Returns:
            List[FileInfo]: 排序后的文件列表
        """
        if sort_by == "name":
            return sorted(files, key=lambda x: x.name.lower(), reverse=reverse)
        elif sort_by == "size":
            return sorted(files, key=lambda x: x.size, reverse=reverse)
        elif sort_by == "modified":
            return sorted(files, key=lambda x: x.modified_time, reverse=reverse)
        elif sort_by == "extension":
            return sorted(files, key=lambda x: x.extension, reverse=reverse)
        else:
            # 默认按名称排序
            return sorted(files, key=lambda x: x.name.lower(), reverse=reverse)

    def get_image_files_by_extensions(
        self, directory: str, extensions: List[str], recursive: bool = False
    ) -> List[FileInfo]:
        """
        获取指定扩展名的图片文件

        Args:
            directory (str): 目录路径
            extensions (List[str]): 扩展名列表（如 ['.jpg', '.png']）
            recursive (bool): 是否递归搜索子目录

        Returns:
            List[FileInfo]: 图片文件信息列表
        """
        # 规范化扩展名（确保以点开头并小写）
        normalized_extensions = {f".{ext.lstrip('.').lower()}" for ext in extensions}

        # 创建过滤函数
        def extension_filter(file_info):
            return file_info.extension in normalized_extensions

        return self.get_image_files(directory, recursive, filter_func=extension_filter)

    def get_image_files_count(self, directory: str, recursive: bool = False) -> int:
        """
        获取目录中图片文件的数量

        Args:
            directory (str): 目录路径
            recursive (bool): 是否递归搜索子目录

        Returns:
            int: 图片文件数量
        """
        try:
            files = self.get_image_files(directory, recursive)
            return len(files)
        except (ValueError, PermissionError):
            return 0

    def get_image_files_grouped_by_extension(
        self, directory: str, recursive: bool = False
    ) -> dict:
        """
        按扩展名分组返回图片文件

        Args:
            directory (str): 目录路径
            recursive (bool): 是否递归搜索子目录

        Returns:
            dict: 扩展名到文件列表的映射
        """
        files = self.get_image_files(directory, recursive)

        grouped = {}
        for file_info in files:
            if file_info.extension not in grouped:
                grouped[file_info.extension] = []
            grouped[file_info.extension].append(file_info)

        return grouped


# 使用示例和便捷函数
def get_image_files(directory: str, recursive: bool = False) -> List[FileInfo]:
    """
    便捷函数：获取目录下的图片文件列表

    Args:
        directory (str): 目录路径
        recursive (bool): 是否递归搜索子目录

    Returns:
        List[FileInfo]: 图片文件信息列表

    Raises:
        ValueError: 如果目录不存在或不是目录
        PermissionError: 如果没有目录访问权限
    """
    reader = ImageDirectoryReader()
    return reader.get_image_files(directory, recursive)


def is_image_directory(directory: str) -> bool:
    """
    判断目录是否包含图片文件

    Args:
        directory (str): 目录路径

    Returns:
        bool: 如果目录存在且包含图片文件则返回True
    """
    try:
        reader = ImageDirectoryReader()
        return reader.get_image_files_count(directory) > 0
    except (ValueError, PermissionError):
        return False


# 使用示例和测试
def test_image_directory_reader():
    import sys
    from datetime import datetime

    # 创建图片目录读取器
    reader = ImageDirectoryReader()

    if len(sys.argv) > 1:
        target_dir = sys.argv[1]
    else:
        target_dir = input("请输入要扫描的目录路径: ")

    try:
        # 检查目录是否存在
        if not reader.is_directory(target_dir):
            print(f"错误: {target_dir} 不是有效的目录")
            sys.exit(1)

        # 获取图片文件列表
        print(f"\n扫描目录: {target_dir}")
        print("=" * 50)

        image_files = reader.get_image_files(
            target_dir, recursive=True, sort_by="size", reverse=True
        )

        if not image_files:
            print("未找到图片文件")
        else:
            print(f"找到 {len(image_files)} 个图片文件:")
            print("-" * 80)
            print(f"{'文件名':<30} {'大小':<10} {'扩展名':<8} {'修改时间'}")
            print("-" * 80)

            for file_info in image_files[:20]:  # 只显示前20个文件
                size_mb = file_info.size / (1024 * 1024)
                mod_time = datetime.fromtimestamp(file_info.modified_time).strftime(
                    "%Y-%m-%d %H:%M"
                )
                print(
                    f"{file_info.name:<30} {size_mb:.2f}MB {file_info.extension:<8} {mod_time}"
                )

            if len(image_files) > 20:
                print(f"... 还有 {len(image_files) - 20} 个文件未显示")

        # 按扩展名分组统计
        print(f"\n按扩展名分组统计:")
        grouped = reader.get_image_files_grouped_by_extension(
            target_dir, recursive=True
        )
        for ext, files in sorted(grouped.items()):
            print(f"  {ext}: {len(files)} 个文件")

        # 只获取特定扩展名的文件
        print(f"\n只获取JPG和PNG文件:")
        jpg_png_files = reader.get_image_files_by_extensions(
            target_dir, [".jpg", ".png"], recursive=True
        )
        for file_info in jpg_png_files[:5]:  # 只显示前5个
            print(f"  {file_info.name}")

        if len(jpg_png_files) > 5:
            print(f"  ... 还有 {len(jpg_png_files) - 5} 个文件")

    except PermissionError as e:
        print(f"权限错误: {e}")
    except Exception as e:
        print(f"发生错误: {e}")


class SizeFormatter:
    """文件大小格式化工具类"""

    # 国际标准 (1024 进制)
    UNITS_IEC = ["B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB"]
    # 常用标准 (1000 进制，硬盘制造商常用)
    UNITS_SI = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]

    @staticmethod
    def format_size(size_bytes, system="iec", precision=2):
        """
        将字节大小转换为人类可读的格式

        Args:
            size_bytes (int): 文件大小（字节）
            system (str): 使用的单位系统 'iec' (1024进制) 或 'si' (1000进制)
            precision (int): 小数点后精度

        Returns:
            str: 格式化后的大小字符串

        Raises:
            ValueError: 如果提供了无效的系统参数
        """
        if size_bytes == 0:
            return "0 B"

        if system == "iec":
            base = 1024
            units = SizeFormatter.UNITS_IEC
        elif system == "si":
            base = 1000
            units = SizeFormatter.UNITS_SI
        else:
            raise ValueError("系统参数必须是 'iec' 或 'si'")

        # 计算最合适的单位
        import math

        exponent = min(math.floor(math.log(size_bytes, base)), len(units) - 1)
        value = size_bytes / (base**exponent)

        # 格式化数值
        if exponent == 0:  # 字节不需要小数部分
            return f"{int(value)} {units[exponent]}"
        else:
            return f"{value:.{precision}f} {units[exponent]}"

    @staticmethod
    def format_size_auto(size_bytes, precision=2):
        """
        自动选择合适的单位系统格式化大小

        Args:
            size_bytes (int): 文件大小（字节）
            precision (int): 小数点后精度

        Returns:
            str: 格式化后的大小字符串
        """
        # 对于大文件(>1GB)，使用SI单位系统(更符合日常习惯)
        if size_bytes > 1024**3:  # 1 GiB
            return SizeFormatter.format_size(size_bytes, "si", precision)
        else:
            return SizeFormatter.format_size(size_bytes, "iec", precision)

    @staticmethod
    def parse_size(size_str):
        """
        将人类可读的大小字符串解析为字节数

        Args:
            size_str (str): 人类可读的大小字符串(如 "2.5 MB")

        Returns:
            int: 字节数

        Raises:
            ValueError: 如果无法解析字符串
        """
        import re

        # 正则表达式匹配数值和单位
        pattern = r"^\s*(\d+\.?\d*)\s*([a-zA-Z]+)\s*$"
        match = re.match(pattern, size_str)

        if not match:
            raise ValueError(f"无法解析大小字符串: {size_str}")

        value = float(match.group(1))
        unit = match.group(2).upper()

        # 定义单位到乘数的映射
        units = {
            "B": 1,
            "KB": 1000,
            "MB": 1000**2,
            "GB": 1000**3,
            "TB": 1000**4,
            "PB": 1000**5,
            "KIB": 1024,
            "MIB": 1024**2,
            "GIB": 1024**3,
            "TIB": 1024**4,
            "PIB": 1024**5,
        }

        # 处理可能的单位变体
        if unit not in units:
            # 尝试添加'B'后缀(如K->KB, M->MB)
            if unit + "B" in units:
                unit += "B"
            elif unit in ["K", "M", "G", "T", "P"]:
                unit += "B"  # 假设是SI单位
            else:
                raise ValueError(f"无法识别的单位: {unit}")

        if unit not in units:
            raise ValueError(f"无法识别的单位: {unit}")

        return int(value * units[unit])


# 示例用法和测试
def test_size_formatter():
    # 测试各种大小的格式化
    test_sizes = [
        0,
        512,
        1024,
        1048576,  # 1 MiB
        1073741824,  # 1 GiB
        1099511627776,  # 1 TiB
        1125899906842624,  # 1 PiB
        5000000000,  # 5e9 字节 ≈ 4.66 GiB
    ]

    print("大小格式化示例:")
    print("=" * 40)
    for size in test_sizes:
        iec_fmt = SizeFormatter.format_size(size, "iec")
        si_fmt = SizeFormatter.format_size(size, "si")
        auto_fmt = SizeFormatter.format_size_auto(size)
        print(
            f"{size:>20} bytes = {iec_fmt:>10} (IEC) = {si_fmt:>10} (SI) = {auto_fmt:>10} (Auto)"
        )

    # 测试解析功能
    print("\n\n大小解析示例:")
    print("=" * 40)
    test_strings = ["512 B", "1.5 KB", "2.5 MB", "1 GiB", "2.5 GB"]

    for size_str in test_strings:
        try:
            bytes_value = SizeFormatter.parse_size(size_str)
            print(f"{size_str:>10} = {bytes_value:>15,} bytes")
        except ValueError as e:
            print(f"{size_str:>10} -> 错误: {e}")


# 常见视频文件扩展名
VIDEO_EXTENSIONS = {
    ".mp4",
    ".avi",
    ".mov",
    ".wmv",
    ".flv",
    ".webm",
    ".mkv",
    ".m4v",
    ".mpg",
    ".mpeg",
    ".3gp",
    ".3g2",
    ".mts",
    ".m2ts",
    ".vob",
    ".ogv",
    ".divx",
    ".rm",
    ".rmvb",
    ".asf",
    ".amv",
    ".m4p",
    ".m4v",
    ".svi",
    ".nsv",
    ".f4v",
    ".f4p",
    ".f4a",
    ".f4b",
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
        tree = FileInfoTree(
            name=directory.name,
            path=str(directory),
            type="directory",
            children=[],
        )

        try:
            items = sorted(os.listdir(directory), key=lambda x: x.lower())
        except (OSError, PermissionError) as e:
            raise PermissionError(f"无法读取目录内容: {e}")

        for item in items:
            item_path = directory / item
            try:
                if item_path.is_dir():
                    # 递归处理子目录
                    subtree = self._traverse_directory(item_path)
                    if subtree.children:  # 只包含有视频文件的目录
                        tree.children.append(subtree)
                elif item_path.is_file() and self.is_video_file(item_path):
                    # 添加视频文件
                    tree.children.append(
                        FileInfo(
                            name=item,
                            path=str(item_path),
                            type="file",
                            extension=item_path.suffix.lower(),
                            size=item_path.stat().st_size,
                            pretty_size=SizeFormatter.format_size(
                                item_path.stat().st_size
                            ),
                            modified_time=item_path.stat().st_mtime,
                            pretty_modified_time=timestamp_to_str(
                                item_path.stat().st_mtime
                            ),
                        )
                    )
            except (OSError, PermissionError) as e:
                # 处理无法访问的文件或目录
                raise PermissionError(f"无法读取目录内容: {e}")

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
        logger.debug(prefix + connector + node.name)

        if node.type == "directory":
            # 更新前缀用于子节点
            new_prefix = prefix + ("    " if is_last else "│   ")

            # 打印所有子节点
            for i, child in enumerate(node.children):
                self.print_tree(child, new_prefix, i == len(node.children) - 1)


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


def test_video_tree():
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
        if save_json == "y":
            json_output = tree_builder.to_json()
            output_file = "video_tree.json"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(json_output)
            print(f"树形结构已保存到 {output_file}")

    except Exception as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    # test_size_formatter()
    # test_image_directory_reader()
    test_video_tree()
