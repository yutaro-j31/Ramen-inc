# models/bond.py
import uuid
from typing import Dict, Any

class Bond:
    """
    発行された社債の情報を保持するデータクラス。
    """
    def __init__(self, principal: float, annual_coupon_rate: float, maturity_weeks: int, issued_week: int):
        self.bond_id: str = f"BOND-{str(uuid.uuid4())[:8]}"
        self.principal: float = principal  # 借入元本 (額面)
        self.annual_coupon_rate: float = annual_coupon_rate  # 年間利率 (クーポンレート)
        self.maturity_weeks: int = maturity_weeks # 発行から満期までの週数
        self.issued_week: int = issued_week # 発行された週
        self.redemption_week: int = issued_week + maturity_weeks # 償還(満期返済)が行われる週
        self.is_redeemed: bool = False # 償還済みフラグ

    @property
    def weekly_interest_payment(self) -> float:
        """毎週支払う利息額を計算する。"""
        # 1年は52週として計算
        from .game_time import GameTime
        weekly_rate = self.annual_coupon_rate / GameTime.WEEKS_PER_YEAR
        return self.principal * weekly_rate

    def to_dict(self) -> Dict[str, Any]:
        """社債の情報を辞書形式で返す。"""
        return {
            "bond_id": self.bond_id,
            "principal": self.principal,
            "annual_coupon_rate": self.annual_coupon_rate,
            "weekly_interest_payment": self.weekly_interest_payment,
            "maturity_weeks": self.maturity_weeks,
            "issued_week": self.issued_week,
            "redemption_week": self.redemption_week,
            "is_redeemed": self.is_redeemed
        }

    def __str__(self) -> str:
        return (f"社債 (ID: {self.bond_id[-6:]}): 額面 ¥{self.principal:,.0f}, "
                f"年利 {self.annual_coupon_rate:.2%}, "
                f"満期まで残り {self.redemption_week - self.issued_week}週")
