import datetime
import logging
import time
from typing import Optional, Union

from dateutil import tz

logger = logging.getLogger(__name__)


class TimestampConverter:
    """时间戳转换工具类"""

    @staticmethod
    def detect_timestamp_type(timestamp: Union[int, float]) -> str:
        """
        检测时间戳类型（秒级或毫秒级）

        Args:
            timestamp (Union[int, float]): 时间戳

        Returns:
            str: "seconds" 或 "milliseconds"
        """
        # 如果时间戳大于一个较大的值（比如 10^12），则认为是毫秒级
        if timestamp > 1e12:
            return "milliseconds"
        else:
            return "seconds"

    @staticmethod
    def normalize_timestamp(timestamp: Union[int, float]) -> float:
        """
        标准化时间戳为秒级

        Args:
            timestamp (Union[int, float]): 时间戳

        Returns:
            float: 秒级时间戳
        """
        timestamp_type = TimestampConverter.detect_timestamp_type(timestamp)

        if timestamp_type == "milliseconds":
            return timestamp / 1000.0
        else:
            return float(timestamp)

    @staticmethod
    def timestamp_to_datetime(
        timestamp: Union[int, float], timezone: Optional[str] = None
    ) -> datetime.datetime:
        """
        将时间戳转换为datetime对象

        Args:
            timestamp (Union[int, float]): 时间戳
            timezone (str, optional): 时区，如 "UTC", "Asia/Shanghai"等

        Returns:
            datetime.datetime: 对应的datetime对象
        """
        # 标准化时间戳
        normalized_timestamp = TimestampConverter.normalize_timestamp(timestamp)

        # 创建datetime对象（本地时间）
        dt = datetime.datetime.fromtimestamp(normalized_timestamp)

        # 应用时区
        if timezone:
            try:
                tz_info = tz.gettz(timezone)
                if tz_info:
                    dt = dt.replace(tzinfo=tz.gettz("UTC")).astimezone(tz_info)
                else:
                    logger.warning(f"警告: 无法识别的时区 '{timezone}'，使用本地时区")
            except Exception as e:
                logger.warning(f"警告: 时区处理错误: {e}，使用本地时区")

        return dt

    @staticmethod
    def format_timestamp(
        timestamp: Union[int, float],
        format_style: str = "standard",
        timezone: Optional[str] = None,
    ) -> str:
        """
        将时间戳格式化为可读字符串

        Args:
            timestamp (Union[int, float]): 时间戳
            format_style (str): 格式样式，可选值:
                - "standard": 标准格式 (YYYY-MM-DD HH:MM:SS)
                - "short": 短格式 (YYYY-MM-DD)
                - "full": 完整格式 (YYYY年MM月DD日 HH时MM分SS秒)
                - "relative": 相对时间 (如 "2小时前")
                - "iso": ISO格式
                - "custom": 自定义格式（需配合custom_format参数）
            timezone (str, optional): 时区

        Returns:
            str: 格式化后的时间字符串
        """
        dt = TimestampConverter.timestamp_to_datetime(timestamp, timezone)

        if format_style == "standard":
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        elif format_style == "short":
            return dt.strftime("%Y-%m-%d")
        elif format_style == "full":
            return dt.strftime("%Y年%m月%d日 %H时%M分%S秒")
        elif format_style == "iso":
            return dt.isoformat()
        elif format_style == "relative":
            return TimestampConverter._get_relative_time(timestamp)
        else:
            # 默认使用标准格式
            return dt.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def _get_relative_time(timestamp: Union[int, float]) -> str:
        """
        获取相对时间描述（如 "2小时前"）

        Args:
            timestamp (Union[int, float]): 时间戳

        Returns:
            str: 相对时间描述
        """
        # 标准化时间戳
        normalized_timestamp = TimestampConverter.normalize_timestamp(timestamp)

        # 当前时间
        now = time.time()
        diff = now - normalized_timestamp

        if diff < 0:
            # 未来时间
            diff = abs(diff)
            if diff < 60:
                return "片刻后"
            elif diff < 3600:
                minutes = int(diff / 60)
                return f"{minutes}分钟后"
            elif diff < 86400:
                hours = int(diff / 3600)
                return f"{hours}小时后"
            elif diff < 2592000:  # 30天
                days = int(diff / 86400)
                return f"{days}天后"
            else:
                months = int(diff / 2592000)
                return f"{months}个月后"
        else:
            # 过去时间
            if diff < 60:
                return "刚刚"
            elif diff < 3600:
                minutes = int(diff / 60)
                return f"{minutes}分钟前"
            elif diff < 86400:
                hours = int(diff / 3600)
                return f"{hours}小时前"
            elif diff < 2592000:  # 30天
                days = int(diff / 86400)
                return f"{days}天前"
            elif diff < 31536000:  # 365天
                months = int(diff / 2592000)
                return f"{months}个月前"
            else:
                years = int(diff / 31536000)
                return f"{years}年前"

    @staticmethod
    def format_timestamp_custom(
        timestamp: Union[int, float], format_string: str, timezone: Optional[str] = None
    ) -> str:
        """
        使用自定义格式字符串格式化时间戳

        Args:
            timestamp (Union[int, float]): 时间戳
            format_string (str): 自定义格式字符串
            timezone (str, optional): 时区

        Returns:
            str: 格式化后的时间字符串
        """
        dt = TimestampConverter.timestamp_to_datetime(timestamp, timezone)
        return dt.strftime(format_string)

    @staticmethod
    def get_timestamp_info(timestamp: Union[int, float]) -> dict:
        """
        获取时间戳的详细信息

        Args:
            timestamp (Union[int, float]): 时间戳

        Returns:
            dict: 包含时间详细信息的字典
        """
        dt = TimestampConverter.timestamp_to_datetime(timestamp)

        return {
            "timestamp_original": timestamp,
            "timestamp_seconds": TimestampConverter.normalize_timestamp(timestamp),
            "timestamp_milliseconds": TimestampConverter.normalize_timestamp(timestamp)
            * 1000,
            "year": dt.year,
            "month": dt.month,
            "day": dt.day,
            "hour": dt.hour,
            "minute": dt.minute,
            "second": dt.second,
            "weekday": dt.weekday(),  # 0=周一, 6=周日
            "isoweekday": dt.isoweekday(),  # 1=周一, 7=周日
            "is_leap_year": (dt.year % 4 == 0 and dt.year % 100 != 0)
            or (dt.year % 400 == 0),
            "day_of_year": dt.timetuple().tm_yday,
            "week_number": dt.isocalendar()[1],
            "timezone": str(dt.tzinfo) if dt.tzinfo else "本地时区",
        }


# 便捷函数
def timestamp_to_str(
    timestamp: Union[int, float], format_style: str = "standard"
) -> str:
    """
    便捷函数：将时间戳转换为可读字符串

    Args:
        timestamp (Union[int, float]): 时间戳
        format_style (str): 格式样式

    Returns:
        str: 格式化后的时间字符串
    """
    return TimestampConverter.format_timestamp(timestamp, format_style)


def get_current_timestamp(unit: str = "seconds") -> float:
    """
    获取当前时间戳

    Args:
        unit (str): 返回单位，"seconds" 或 "milliseconds"

    Returns:
        float: 当前时间戳
    """
    current = time.time()

    if unit == "milliseconds":
        return current * 1000
    else:
        return current


# 使用示例和测试
def test_timestamp_converter():
    # 测试用例
    test_timestamps = [
        0,  # 1970-01-01 00:00:00 UTC
        1609459200,  # 2021-01-01 00:00:00 UTC
        1640995200,  # 2022-01-01 00:00:00 UTC
        1640995200000,  # 毫秒级时间戳 (2022-01-01 00:00:00 UTC)
        time.time(),  # 当前时间
        time.time() - 3600,  # 1小时前
        time.time() - 86400,  # 1天前
    ]

    print("时间戳转换示例:")
    print("=" * 80)
    print(
        f"{'原始时间戳':<20} {'检测类型':<12} {'标准格式':<20} {'短格式':<12} {'完整格式':<25} {'相对时间':<12}"
    )
    print("-" * 80)

    for ts in test_timestamps:
        ts_type = TimestampConverter.detect_timestamp_type(ts)
        standard = TimestampConverter.format_timestamp(ts, "standard")
        short = TimestampConverter.format_timestamp(ts, "short")
        full = TimestampConverter.format_timestamp(ts, "full")
        relative = TimestampConverter.format_timestamp(ts, "relative")

        print(
            f"{ts:<20} {ts_type:<12} {standard:<20} {short:<12} {full:<25} {relative:<12}"
        )

    # 自定义格式示例
    print("\n自定义格式示例:")
    custom_format = TimestampConverter.format_timestamp_custom(
        time.time(), "%Y年%m月%d日 %A %H:%M:%S"
    )
    print(f"当前时间: {custom_format}")

    # 时区转换示例
    print("\n时区转换示例:")
    current_ts = time.time()
    utc_time = TimestampConverter.format_timestamp(current_ts, "standard", "UTC")
    shanghai_time = TimestampConverter.format_timestamp(
        current_ts, "standard", "Asia/Shanghai"
    )
    newyork_time = TimestampConverter.format_timestamp(
        current_ts, "standard", "America/New_York"
    )

    print(f"本地时间: {TimestampConverter.format_timestamp(current_ts, 'standard')}")
    print(f"UTC时间: {utc_time}")
    print(f"上海时间: {shanghai_time}")
    print(f"纽约时间: {newyork_time}")

    # 详细信息示例
    print("\n时间戳详细信息示例:")
    info = TimestampConverter.get_timestamp_info(current_ts)
    for key, value in info.items():
        print(f"  {key}: {value}")

    # 使用便捷函数
    print("\n使用便捷函数:")
    print(f"当前时间戳: {get_current_timestamp()}")
    print(f"当前时间: {timestamp_to_str(get_current_timestamp(), 'full')}")


class TimeDurationFormatter:
    """时长格式化工具类"""

    @staticmethod
    def seconds_to_hms(total_seconds):
        """
        将秒数转换为小时、分钟、秒的元组

        Args:
            total_seconds (int): 总秒数

        Returns:
            tuple: (小时, 分钟, 秒) 的元组
        """
        if not isinstance(total_seconds, (int, float)):
            raise ValueError("输入必须是数字类型")

        if total_seconds < 0:
            total_seconds = 0

        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)

        return hours, minutes, seconds

    @staticmethod
    def format_duration(total_seconds, style="colon"):
        """
        将秒数格式化为可读的时长字符串

        Args:
            total_seconds (int): 总秒数
            style (str): 输出样式，可选值：
                - 'colon': 使用冒号分隔 (HH:MM:SS)
                - 'colon_short': 短格式冒号分隔 (H:MM:SS 或 MM:SS)
                - 'text': 文本描述 (X小时Y分钟Z秒)
                - 'text_short': 短格式文本描述 (Xh Ym Zs)
                - 'auto': 自动选择最合适的格式

        Returns:
            str: 格式化后的时长字符串
        """
        hours, minutes, seconds = TimeDurationFormatter.seconds_to_hms(total_seconds)

        if style == "colon":
            # 固定格式 HH:MM:SS
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        elif style == "colon_short":
            # 智能格式，省略不必要的部分
            if hours > 0:
                return f"{hours}:{minutes:02d}:{seconds:02d}"
            else:
                return f"{minutes}:{seconds:02d}"

        elif style == "text":
            # 完整文本描述
            parts = []
            if hours > 0:
                parts.append(f"{hours}小时")
            if minutes > 0:
                parts.append(f"{minutes}分钟")
            if seconds > 0 or not parts:  # 如果没有其他部分，至少显示秒数
                parts.append(f"{seconds}秒")

            return "".join(parts)

        elif style == "text_short":
            # 短文本描述
            parts = []
            if hours > 0:
                parts.append(f"{hours}h")
            if minutes > 0:
                parts.append(f"{minutes}m")
            if seconds > 0 or not parts:
                parts.append(f"{seconds}s")

            return " ".join(parts)

        elif style == "auto":
            # 自动选择最合适的格式
            if hours > 0:
                return TimeDurationFormatter.format_duration(
                    total_seconds, "colon_short"
                )
            elif minutes > 10:
                return TimeDurationFormatter.format_duration(
                    total_seconds, "colon_short"
                )
            else:
                return TimeDurationFormatter.format_duration(
                    total_seconds, "text_short"
                )

        else:
            raise ValueError(f"不支持的样式: {style}")

    @staticmethod
    def format_duration_human(total_seconds, precision=1):
        """
        将秒数格式化为人类友好的时长描述

        Args:
            total_seconds (int): 总秒数
            precision (int): 精度（小数点后位数）

        Returns:
            str: 人类友好的时长描述
        """
        if total_seconds < 60:
            return f"{total_seconds:.{precision}f}秒"
        elif total_seconds < 3600:
            minutes = total_seconds / 60
            return f"{minutes:.{precision}f}分钟"
        elif total_seconds < 86400:
            hours = total_seconds / 3600
            return f"{hours:.{precision}f}小时"
        else:
            days = total_seconds / 86400
            return f"{days:.{precision}f}天"


# 测试和使用示例
def test_time_duration_formatter():
    # 测试用例
    test_seconds = [0, 45, 90, 125, 3600, 3661, 7200, 86400, 90061]

    print("时长格式化示例:")
    print("=" * 60)
    print(
        f"{'秒数':<10} {'冒号格式':<10} {'短冒号':<10} {'文本格式':<15} {'短文本':<10} {'自动':<10} {'人类友好':<10}"
    )
    print("-" * 60)

    for seconds in test_seconds:
        colon = TimeDurationFormatter.format_duration(seconds, "colon")
        colon_short = TimeDurationFormatter.format_duration(seconds, "colon_short")
        text = TimeDurationFormatter.format_duration(seconds, "text")
        text_short = TimeDurationFormatter.format_duration(seconds, "text_short")
        auto = TimeDurationFormatter.format_duration(seconds, "auto")
        human = TimeDurationFormatter.format_duration_human(seconds)

        print(
            f"{seconds:<10} {colon:<10} {colon_short:<10} {text:<15} {text_short:<10} {auto:<10} {human:<10}"
        )

    # 集成到视频信息提取器的示例
    print("\n集成到视频信息提取器的示例:")
    print("=" * 40)

    # 模拟视频时长
    video_durations = [125, 3661, 7205, 54321]

    for duration in video_durations:
        formatted = TimeDurationFormatter.format_duration(duration, "auto")
        print(f"视频时长 {duration}秒 -> {formatted}")


if __name__ == "__main__":
    test_time_duration_formatter()
    test_timestamp_converter()
