import cv2
import os
from pathlib import Path
from collections import namedtuple
import time
import logging
from typing import List, Union, Dict
from utils.time_duration_util import TimeDurationFormatter

# 视频信息 元组
VideoInfo = namedtuple('VideoInfo', [
    'path', 'filename', 'width', 'height', 'resolution', 
    'fps', 'frame_count', 'duration', 'time_duration','codec', 'size', 'pretty_size'
])

class OpenCVVideoInfoExtractor:
    """使用OpenCV提取视频文件信息和生成缩略图的工具类"""
    
    def __init__(self):
        """初始化视频信息提取器"""
        pass
    
    def get_video_info(self, video_path):
        """
        获取视频文件的基本信息
        
        Args:
            video_path (str): 视频文件路径
            
        Returns:
            VideoInfo: 包含视频信息的命名元组
            
        Raises:
            FileNotFoundError: 如果视频文件不存在
            ValueError: 如果无法打开视频文件
        """
        video_path = Path(video_path).resolve()
        
        if not video_path.exists():
            raise FileNotFoundError(f"视频文件不存在: {video_path}")
        
        # 打开视频文件
        cap = cv2.VideoCapture(str(video_path))
        
        if not cap.isOpened():
            raise ValueError(f"无法打开视频文件: {video_path}")
        
        try:
            # 获取视频信息
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = round(cap.get(cv2.CAP_PROP_FPS), 2)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # 计算时长（秒）
            duration = round(frame_count / fps, 2) if fps > 0 else 0
            time_duration = TimeDurationFormatter.format_duration(duration, 'colon_short')
            
            # 获取编解码器信息
            fourcc_int = int(cap.get(cv2.CAP_PROP_FOURCC))
            codec = self._fourcc_to_string(fourcc_int)
            
            # 获取文件大小
            file_size = video_path.stat().st_size
            pretty_size = self._format_size(file_size)
            
            # 创建并返回命名元组
            return VideoInfo(
                path=str(video_path),
                filename=video_path.name,
                width=width,
                height=height,
                resolution=f"{width}x{height}",
                fps=fps,
                frame_count=frame_count,
                duration=duration,
                time_duration=time_duration,
                codec=codec,
                size=file_size,
                pretty_size=pretty_size
            )
            
        finally:
            # 确保释放视频捕获对象
            cap.release()
    
    def _fourcc_to_string(self, fourcc_int):
        """
        将FourCC代码转换为可读字符串
        
        Args:
            fourcc_int (int): FourCC整数代码
            
        Returns:
            str: FourCC字符串表示
        """
        return "".join([chr((fourcc_int >> 8 * i) & 0xFF) for i in range(4)])
    
    def _format_size(self, size_bytes):
        """
        格式化文件大小为人类可读格式
        
        Args:
            size_bytes (int): 文件大小（字节）
            
        Returns:
            str: 格式化后的大小字符串
        """
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        size = size_bytes
        
        while size >= 1024 and i < len(size_names) - 1:
            size /= 1024.0
            i += 1
        
        return f"{size:.2f} {size_names[i]}"
    
    def get_video_info_batch(self, video_paths):
        """
        批量获取多个视频文件的信息
        
        Args:
            video_paths (list): 视频文件路径列表
            
        Returns:
            dict: 文件名到视频信息的映射
        """
        results = {}
        for path in video_paths:
            try:
                results[path] = self.get_video_info(path)
            except Exception as e:
                results[path] = f"错误: {str(e)}"
        return results
    
    def get_video_thumbnail(self, video_path, output_path=None, frame_time=5.0):
        """
        获取视频的单个缩略图
        
        Args:
            video_path (str): 视频文件路径
            output_path (str, optional): 缩略图保存路径
            frame_time (float): 提取帧的时间（秒）
            
        Returns:
            numpy.ndarray: 缩略图图像数据，如果失败返回None
        """
        cap = cv2.VideoCapture(str(video_path))
        
        if not cap.isOpened():
            raise ValueError(f"无法打开视频文件: {video_path}")
        
        try:
            # 设置到指定时间点
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_pos = int(frame_time * fps)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
            
            # 读取帧
            ret, frame = cap.read()
            
            if ret and output_path:
                cv2.imwrite(output_path, frame)
                
            return frame if ret else None
            
        finally:
            cap.release()
    
    def generate_thumbnails_at_times(
        self, 
        video_path: str, 
        times: List[Union[float, int]], 
        output_dir: str = None, 
        prefix: str = "thumbnail",
        format: str = "jpg",
        quality: int = 95
    ) -> Dict[float, str]:
        """
        在指定时间点生成多个缩略图
        
        Args:
            video_path (str): 视频文件路径
            times (List[Union[float, int]]): 时间点列表（单位：秒）
            output_dir (str, optional): 输出目录，如果为None则不保存文件
            prefix (str): 缩略图文件名前缀
            format (str): 图像格式（jpg, png等）
            quality (int): JPEG质量（0-100），仅对JPEG格式有效
            
        Returns:
            Dict[float, str]: 时间点到文件路径的映射
            
        Raises:
            ValueError: 如果无法打开视频文件或时间点无效
        """
        video_path = Path(video_path).resolve()
        
        if not video_path.exists():
            raise FileNotFoundError(f"视频文件不存在: {video_path}")
        
        # 打开视频文件
        cap = cv2.VideoCapture(str(video_path))
        
        if not cap.isOpened():
            raise ValueError(f"无法打开视频文件: {video_path}")
        
        try:
            # 获取视频信息
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0
            
            # 验证时间点
            valid_times = []
            for time_point in times:
                if time_point < 0:
                    logging.warning(f"警告: 时间点 {time_point} 小于0，已跳过")
                elif time_point > duration:
                    logging.warning(f"警告: 时间点 {time_point} 超过视频时长 {duration:.2f}s，已跳过")
                else:
                    valid_times.append(time_point)
            
            if not valid_times:
                raise ValueError("没有有效的时间点")
            
            # 准备输出目录
            if output_dir:
                output_dir = Path(output_dir)
                output_dir.mkdir(parents=True, exist_ok=True)
            
            # 生成缩略图
            results = {}
            for time_point in valid_times:
                # 计算帧位置
                frame_pos = int(time_point * fps)
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
                
                # 读取帧
                ret, frame = cap.read()
                
                if ret:
                    if output_dir:
                        # 生成文件名
                        time_str = f"{time_point:.1f}".replace('.', '_')
                        filename = f"{prefix}_{time_str}s.{format}"
                        output_path = output_dir / filename
                        
                        logging.debug(f"generate thumbnails with [{str(output_path)}]")

                        # 保存图像
                        # if format.lower() in ['jpg', 'jpeg']:
                        # 此写法 路径带中文会写入失败
                            # cv2.imwrite(str(output_path), frame, [cv2.IMWRITE_JPEG_QUALITY, quality])
                        # else:
                            # cv2.imwrite(str(output_path), frame)
                        if format.lower() in ['jpg', 'jpeg']:
                            cv2.imencode("." + format, frame, [cv2.IMWRITE_JPEG_QUALITY, quality])[1].tofile(str(output_path))
                        else:
                            cv2.imencode("." + format, frame)[1].tofile(str(output_path))
                        
                        results[time_point] = str(output_path)
                    else:
                        # 如果不保存文件，只返回图像数据（这里简化处理，实际可能需要调整）
                        results[time_point] = frame
                else:
                    logging.warning(f"警告: 无法在时间点 {time_point}s 读取帧")
                    results[time_point] = None
            
            return results
            
        finally:
            cap.release()
    



# 使用示例和测试
if __name__ == "__main__":
    import sys
    
    # 创建视频信息提取器
    extractor = OpenCVVideoInfoExtractor()
    
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
    else:
        video_path = input("请输入视频文件路径: ")
    
    try:
        # 获取视频信息
        video_info = extractor.get_video_info(video_path)
        print(f"视频时长: {video_info.duration:.2f} 秒")
        
        # 示例: 在指定时间点生成缩略图
        print("\n 在指定时间点生成缩略图:")
        specific_times = [0, 10, 20, 30, 60, 120]  # 0s, 10s, 20s, 30s, 1min, 2min
        results = extractor.generate_thumbnails_at_times(
            video_path, specific_times, "thumbnails_specific", "specific"
        )
        
        for time_point, file_path in results.items():
            if file_path:
                print(f"  时间点 {time_point}s: {file_path}")
            else:
                print(f"  时间点 {time_point}s: 生成失败")
        
                
    except Exception as e:
        print(f"处理视频时出错: {e}")