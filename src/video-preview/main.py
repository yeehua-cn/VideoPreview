import logging
import os
import sys
from configparser import ConfigParser
from pathlib import Path

from dynaconf import Dynaconf
from kivy.config import Config


def get_source_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        # 表示程序运行在打包后
        base_path = sys._MEIPASS
    else:
        # 表示程序还未打包
        base_path = os.path.abspath(".")
    logging.debug(" base_path: %s ", base_path)
    return os.path.join(base_path, relative_path)


def init_kivy_config():
    font_path = get_source_path("data\\fonts\\SourceHanSansSC-Normal-2.otf")
    config_path = get_source_path("config\\config.ini")

    logging.debug(" font_path: %s ", font_path)
    logging.debug(" config_path: %s ", config_path)
    # 读取config文件，并修改其默认字体
    config = ConfigParser()
    config.read(config_path, encoding="UTF-8")
    config.set("kivy", "default_font", str(["SourceHanSansSC-Normal", font_path]))

    with open(config_path, "w") as configfile:
        config.write(configfile)

    # 将config读入并运用到全局
    Config.read(config_path)


init_kivy_config()


from video_preview import VideoPreviewApp


class AppContext:

    def __init__(self):
        self.app_name = "视频预览工具"
        self.settings = None
        self.env = None


APP_CTX = AppContext()


def init_config():
    APP_CTX.settings = Dynaconf(
        root_path="config",
        settings_files=["*.yaml", "*.yml"],
        envvar_prefix="APP",  # 环境变量前缀。设置`APP_FOO='bar'`，使用`settings.FOO`
        environments=True,  # 是否使用多环境
        env_switcher="ENV",  # 用于切换模式的环境变量名称 ENV=production
    )
    APP_CTX.env = os.getenv("ENV")


def clear_logger():
    # 清理已有 handlers
    root_logger = logging.getLogger()
    for h in root_logger.handlers:
        root_logger.removeHandler(h)


def init_logger():
    clear_logger()

    logging.basicConfig(
        format="%(asctime)s %(name)s:%(levelname)s: %(message)s",
        datefmt="%y-%m-%d %H:%M:%S",
    )
    logging.getLogger().setLevel(APP_CTX.settings.logger.level)


def print_app_config():
    logging.info("----------- Start application %s -----------", APP_CTX.app_name)
    logging.info("---- ENV: %s ", APP_CTX.env)


def init_app():
    init_config()
    init_logger()
    print_app_config()


if __name__ == "__main__":
    init_app()
    VideoPreviewApp().run()
