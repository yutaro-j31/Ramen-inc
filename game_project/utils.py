# utils.py
from typing import Optional

def get_integer_input(prompt: str, min_val: Optional[int] = None, max_val: Optional[int] = None) -> Optional[int]:
    """プレイヤーから整数入力を受け付ける共通関数"""
    while True:
        try:
            value_str = input(prompt).strip()
            if not value_str:
                # Enterキーのみの場合はNoneを返してキャンセル扱いにする
                return None
            
            value = int(value_str)
            
            if (min_val is not None and value < min_val) or \
               (max_val is not None and value > max_val):
                # 範囲指定がある場合、エラーメッセージを表示
                range_parts = []
                if min_val is not None: range_parts.append(f"{min_val}以上")
                if max_val is not None: range_parts.append(f"{max_val}以下")
                print(f"入力範囲外です ({'かつ'.join(range_parts)})。")
            else:
                return value
        except ValueError:
            print("有効な数値を入力してください。")
