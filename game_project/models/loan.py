# models/loan.py
# 省略なしの完全なコードです。

import uuid

class Loan:
    """
    個別のローン契約の情報を保持するデータクラス。
    """
    def __init__(self, principal: float, weekly_rate: float, total_weeks: int, issued_week: int, lender_name: str, product_name: str):
        self.loan_id: str = f"LOAN-{str(uuid.uuid4())[:8]}"
        self.principal_borrowed: float = principal  # 当初借入元本
        self.remaining_principal: float = principal # 元本残高
        self.weekly_rate: float = weekly_rate # 週利
        self.total_weeks: int = total_weeks # 総返済週数
        self.weeks_repaid: int = 0 # これまで返済した週数
        self.issued_week: int = issued_week # 借入時の総経過週数
        self.lender_name: str = lender_name # 貸し手銀行名
        self.product_name: str = product_name # ローン商品名

    def calculate_interest(self) -> float:
        """このローンの週次の支払利息を計算する。"""
        return self.remaining_principal * self.weekly_rate

    def __str__(self) -> str:
        """ローン情報を分かりやすく文字列で返す。"""
        return (f"ID: ...{self.loan_id[-6:]} | {self.lender_name}「{self.product_name}」 "
                f"(残高: ¥{self.remaining_principal:,.0f}, 週利: {self.weekly_rate:.4%})")
