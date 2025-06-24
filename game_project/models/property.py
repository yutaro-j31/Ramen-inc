# models/property.py
# 省略なしの完全なコードです。

import uuid
import random
from typing import List, Optional, Tuple

class Property:
    """
    不動産物件を表すクラス。
    """
    def __init__(self, name: str, property_type: str, location: str, purchase_price: int, weekly_rent_income: int, weekly_maintenance_cost: int):
        self.property_id: str = f"PROP-{str(uuid.uuid4())[:8]}"
        self.name: str = name
        self.property_type: str = property_type
        self.location: str = location
        self.purchase_price: int = purchase_price
        self.current_value: float = float(purchase_price)
        self.weekly_rent_income: int = weekly_rent_income
        self.weekly_maintenance_cost: int = weekly_maintenance_cost
        self.historical_values: List[float] = [self.current_value]

    def update_weekly_value(self, economic_impact: float):
        """週ごとに物件の現在価値を更新する。"""
        # 経済状況とランダムな変動要因で価値を更新
        change_rate = economic_impact + (random.uniform(-0.005, 0.006))
        self.current_value *= (1 + change_rate)
        self.historical_values.append(self.current_value)
        if len(self.historical_values) > 52: # 1年分のみ保持
            self.historical_values.pop(0)

    def get_gross_yield(self) -> float:
        """表面利回り(年間家賃収入 ÷ 物件価格)を計算する。"""
        # GameTimeクラスの定数を参照するように修正
        from models.game_time import GameTime
        annual_rent = self.weekly_rent_income * GameTime.WEEKS_PER_YEAR
        if self.purchase_price > 0:
            return annual_rent / self.purchase_price
        return 0.0
