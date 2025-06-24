# models/target_company.py
import uuid
from typing import Tuple, List, Dict, Any

class TargetCompany:
    """買収対象となる非上場企業を表すクラス"""
    def __init__(self, name: str, industry: str,
                 estimated_annual_revenue: float,
                 estimated_net_profit_margin: float, # 年間売上に対する純利益率の目安
                 employee_count: int,
                 asking_price_min: float, # 希望買収価格(下限)
                 asking_price_max: float, # 希望買収価格(上限)
                 description: str = "詳細不明の非公開企業。",
                 synergy_notes: List[str] | None = None, # 買収によるシナジー効果のヒントなど
                 weeks_on_market: int = 0): # 市場に出てからの経過週数

        self.company_id: str = str(uuid.uuid4()) # ユニークID
        self.name: str = name
        self.industry: str = industry
        self.estimated_annual_revenue: float = estimated_annual_revenue
        self.estimated_net_profit_margin: float = estimated_net_profit_margin
        self.employee_count: int = employee_count
        self.asking_price_min: float = asking_price_min
        self.asking_price_max: float = asking_price_max
        self.description: str = description
        self.synergy_notes: List[str] = synergy_notes if synergy_notes is not None else []
        self.weeks_on_market: int = weeks_on_market

        # デューデリジェンスで明らかになる情報 (初期値は不明または推定)
        self.dd_revealed_strength: str | None = None
        self.dd_revealed_weakness: str | None = None
        self.dd_revealed_financial_health_comment: str | None = None # 例: "キャッシュフローは安定している模様"
        self.dd_performed: bool = False

    def get_estimated_net_profit(self) -> float:
        """推定年間純利益を計算"""
        return self.estimated_annual_revenue * self.estimated_net_profit_margin

    def __str__(self) -> str:
        return (f"企業名: {self.name} (ID: ...{self.company_id[-6:]})\n"
                f"  業種: {self.industry}\n"
                f"  推定年間売上: ¥{self.estimated_annual_revenue:,.0f}\n"
                f"  推定年間純利益: ¥{self.get_estimated_net_profit():,.0f} (利益率: {self.estimated_net_profit_margin*100:.1f}%)\n"
                f"  従業員数: {self.employee_count}人\n"
                f"  希望買収価格帯: ¥{self.asking_price_min:,.0f} ~ ¥{self.asking_price_max:,.0f}\n"
                f"  概要: {self.description}")

    def get_detailed_str(self) -> str:
        """デューデリジェンス後の詳細情報を文字列で返す"""
        base_info = self.__str__()
        dd_info_lines = ["\n  --- デューデリジェンス情報 ---"]
        if self.dd_performed:
            dd_info_lines.append(f"    強み(推定): {self.dd_revealed_strength if self.dd_revealed_strength else '特筆事項なし'}")
            dd_info_lines.append(f"    弱み(推定): {self.dd_revealed_weakness if self.dd_revealed_weakness else '特筆事項なし'}")
            dd_info_lines.append(f"    財務健全性コメント: {self.dd_revealed_financial_health_comment if self.dd_revealed_financial_health_comment else '追加情報なし'}")
            if self.synergy_notes:
                dd_info_lines.append(f"    シナジー可能性: {', '.join(self.synergy_notes)}")
        else:
            dd_info_lines.append("    デューデリジェンス未実施のため、詳細情報は不明です。")
        return base_info + "\n" + "\n".join(dd_info_lines)
