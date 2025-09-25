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
    def format_duration(total_seconds, style='colon'):
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
        
        if style == 'colon':
            # 固定格式 HH:MM:SS
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        elif style == 'colon_short':
            # 智能格式，省略不必要的部分
            if hours > 0:
                return f"{hours}:{minutes:02d}:{seconds:02d}"
            else:
                return f"{minutes}:{seconds:02d}"
        
        elif style == 'text':
            # 完整文本描述
            parts = []
            if hours > 0:
                parts.append(f"{hours}小时")
            if minutes > 0:
                parts.append(f"{minutes}分钟")
            if seconds > 0 or not parts:  # 如果没有其他部分，至少显示秒数
                parts.append(f"{seconds}秒")
            
            return "".join(parts)
        
        elif style == 'text_short':
            # 短文本描述
            parts = []
            if hours > 0:
                parts.append(f"{hours}h")
            if minutes > 0:
                parts.append(f"{minutes}m")
            if seconds > 0 or not parts:
                parts.append(f"{seconds}s")
            
            return " ".join(parts)
        
        elif style == 'auto':
            # 自动选择最合适的格式
            if hours > 0:
                return TimeDurationFormatter.format_duration(total_seconds, 'colon_short')
            elif minutes > 10:
                return TimeDurationFormatter.format_duration(total_seconds, 'colon_short')
            else:
                return TimeDurationFormatter.format_duration(total_seconds, 'text_short')
        
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
if __name__ == "__main__":
    # 测试用例
    test_seconds = [0, 45, 90, 125, 3600, 3661, 7200, 86400, 90061]
    
    print("时长格式化示例:")
    print("=" * 60)
    print(f"{'秒数':<10} {'冒号格式':<10} {'短冒号':<10} {'文本格式':<15} {'短文本':<10} {'自动':<10} {'人类友好':<10}")
    print("-" * 60)
    
    for seconds in test_seconds:
        colon = TimeDurationFormatter.format_duration(seconds, 'colon')
        colon_short = TimeDurationFormatter.format_duration(seconds, 'colon_short')
        text = TimeDurationFormatter.format_duration(seconds, 'text')
        text_short = TimeDurationFormatter.format_duration(seconds, 'text_short')
        auto = TimeDurationFormatter.format_duration(seconds, 'auto')
        human = TimeDurationFormatter.format_duration_human(seconds)
        
        print(f"{seconds:<10} {colon:<10} {colon_short:<10} {text:<15} {text_short:<10} {auto:<10} {human:<10}")
    
    # 集成到视频信息提取器的示例
    print("\n集成到视频信息提取器的示例:")
    print("=" * 40)
    
    # 模拟视频时长
    video_durations = [125, 3661, 7205, 54321]
    
    for duration in video_durations:
        formatted = TimeDurationFormatter.format_duration(duration, 'auto')
        print(f"视频时长 {duration}秒 -> {formatted}")