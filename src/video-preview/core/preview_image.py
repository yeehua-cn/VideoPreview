import logging

from utils.file_util import get_image_files
from utils.sequence_generator import SequenceGenerator
from utils.video_meta_util import OpenCVVideoInfoExtractor, VideoInfo

logger = logging.getLogger(__name__)


# 预览图
class PreviewImage:

    @staticmethod
    def get_video_time_seq(video_duration):
        #  生成视频预览图片的时间序列
        logger.info(f"Video time duration: {video_duration}")

        if video_duration <= 5:
            seq = SequenceGenerator.generate_uniform_sequence(video_duration, 1)
        if video_duration <= 30:
            seq = SequenceGenerator.generate_uniform_sequence(video_duration, 5)
        elif video_duration <= 300:
            seq = SequenceGenerator.generate_uniform_sequence(video_duration, 10)
        else:
            seq = SequenceGenerator.generate_uniform_sequence(video_duration, 16)

        logger.info(f"Video time sequence: {seq}")
        return seq

    @staticmethod
    def generate_thumbnails(extractor: OpenCVVideoInfoExtractor, video_info: VideoInfo):
        logger.info(f"Generate video thumbnails from: {video_info}")

        seq = PreviewImage.get_video_time_seq(int(video_info.duration))
        output_dir = PreviewImage.get_thumbnails_folder(video_info.path)
        logger.info(
            f"Generate thumbnails for video time sequence : {seq} , output_dir: {output_dir}"
        )

        thumbnails = extractor.generate_thumbnails_at_times(
            video_info.path,
            seq,
            output_dir,
            prefix=video_info.filename + "-" + "thumbnail",
            format="jpg",
            quality=95,
        )
        logger.info(f"Generate video thumbnails: {thumbnails}")
        thumbnails_array = []
        for time_point, file_path in thumbnails.items():
            thumbnails_array.append(file_path)
        return thumbnails_array

    @staticmethod
    def get_thumbnails_folder(path):
        # 预览图存储目录
        return path + "-" + "thumbnails"

    @staticmethod
    def load_video_thumbnails(video_path):
        # 获取目录下的所有图片文件
        folder = PreviewImage.get_thumbnails_folder(video_path)
        image_files = get_image_files(folder)
        logger.info(f"Load exists thumbnails: {image_files}")

        images = []
        for image_info in image_files:
            images.append(image_info.path)

        return images
