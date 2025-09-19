
from video_preview import VideoPreviewApp

import logging
import os

from dynaconf import Dynaconf


class AppContext:

    def __init__(self):
        self.app_name = "视频预览工具"
        self.settings = None
        self.env = None


APP_CONTEXT = AppContext()


def init_config():
    APP_CONTEXT.settings = Dynaconf(
        root_path="config",
        settings_files=['*.yaml', '*.yml'],
        envvar_prefix="APP",  # 环境变量前缀。设置`APP_FOO='bar'`，使用`settings.FOO`
        environments=True,  # 是否使用多环境
        env_switcher="ENV",  # 用于切换模式的环境变量名称 ENV=production
    )
    APP_CONTEXT.env = os.getenv("ENV")

def clear_logger():
    # 清理已有 handlers
    root_logger = logging.getLogger()
    for h in root_logger.handlers:
        root_logger.removeHandler(h)


def init_logger():
    clear_logger()

    logging.basicConfig(format="%(asctime)s %(name)s:%(levelname)s: %(message)s", datefmt="%y-%m-%d %H:%M:%S")
    logging.getLogger().setLevel(APP_CONTEXT.settings.logger.level)


def print_app_config():
    logging.info("----------- Start application %s -----------", APP_CONTEXT.app_name)
    logging.info("---- ENV: %s ", APP_CONTEXT.env)


def init_app():
    init_config()
    init_logger()
    print_app_config()


if __name__ == '__main__':
   init_app()
   VideoPreviewApp().run()