from typing import List, Union
import numpy as np

class SequenceGenerator:
    """数字序列生成器"""
    
    @staticmethod
    def generate_uniform_sequence(
        total: int, 
        count: int, 
        start_from_zero: bool = True
    ) -> List[int]:
        """
        生成均匀分布的整数序列
        
        Args:
            total (int): 总数（序列的最大值）
            count (int): 要生成的数字数量
            start_from_zero (bool): 是否从0开始
            
        Returns:
            List[int]: 均匀分布的整数序列
        """
        if count <= 0:
            raise ValueError("数量必须大于0")
        
        if total <= 0:
            raise ValueError("总数必须大于0")
        
        if count > total + (0 if start_from_zero else 1):
            raise ValueError("数量不能超过可用值的范围")
        
        if count == 1:
            return [total // 2] if start_from_zero else [1]
        
        # 计算步长（使用整数除法）
        if start_from_zero:
            step = total // (count - 1) if count > 1 else 0
            return [i * step for i in range(count)]
        else:
            step = (total - 1) // (count - 1) if count > 1 else 0
            return [1 + i * step for i in range(count)]
 

# 使用示例和测试
if __name__ == "__main__":
    print("数字序列生成器示例:")
    print("=" * 60)
    
    # 示例: 生成均匀分布的整数序列
    print("\n 均匀分布的整数序列:")
    seq = SequenceGenerator.generate_uniform_sequence(10560, 5)
    print(f"   0到10560之间均匀分布5个整数: {seq}")