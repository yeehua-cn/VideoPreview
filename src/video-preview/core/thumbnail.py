from PIL import Image
import cv2  # 若需使用OpenCV

def generate_thumbnail(video_path: str, output_path: str, time_sec: int = 10):
    # 使用FFmpeg或OpenCV提取关键帧
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_MSEC, time_sec * 1000)
    success, frame = cap.read()
    if success:
        Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).save(output_path)