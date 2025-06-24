# constants/hr_data.py
from typing import List, Dict, Any

# --- CXO(経営幹部)関連 ---
CXO_TYPES: Dict[str, Dict[str, Any]] = {
    "CFO": {"display_name": "CFO (最高財務責任者)", "description": "会社の財務戦略、資金調達、予算管理を統括する。", 
            "base_weekly_salary_range": (800_000, 2_000_000), 
            "skill_levels": {"S": 1.5, "A": 1.2, "B": 1.0, "C": 0.8}, 
            "effects": [
                {"type": "loan_interest_reduction", "value_percent_reduction": 0.1, "skill_level_needed": "A", "description": "ローン金利0.1%軽減"}, 
                {"type": "overall_cost_reduction_percentage", "value": 0.01, "skill_level_needed": "S", "description": "全社コスト1%削減"}
            ]},
    "CMO": {"display_name": "CMO (最高マーケティング責任者)", "description": "マーケティング戦略、広告、ブランド管理を担当する。", 
            "base_weekly_salary_range": (700_000, 1_800_000), 
            "skill_levels": {"S": 1.5, "A": 1.2, "B": 1.0, "C": 0.8}, 
            "effects": [
                {"type": "marketing_effectiveness_boost", "value": 0.2, "skill_level_needed": "A", "description": "マーケティング効果20%増"}, 
                {"type": "brand_awareness_increase_rate", "value": 0.05, "skill_level_needed": "S", "description": "ブランド認知度上昇率5%アップ"}
            ]},
    "CTO": {"display_name": "CTO (最高技術責任者)", "description": "技術戦略、研究開発の方向性を決定し、イノベーションを推進する。", 
            "base_weekly_salary_range": (900_000, 2_200_000), 
            "skill_levels": {"S": 1.5, "A": 1.2, "B": 1.0, "C": 0.8}, 
            "effects": [
                {"type": "rnd_speed_boost", "value": 0.25, "skill_level_needed": "A", "description": "R&D速度25%向上"}, 
                {"type": "rnd_success_chance_boost", "value": 0.1, "skill_level_needed": "S", "description": "R&D成功確率10%向上"}
            ]},
    "COO": {"display_name": "COO (最高執行責任者)", "description": "日々の事業運営を統括し、効率化と最適化を図る。", 
            "base_weekly_salary_range": (1_000_000, 2_500_000), 
            "skill_levels": {"S": 1.5, "A": 1.2, "B": 1.0, "C": 0.8}, 
            "effects": [
                {"type": "all_business_units_fixed_cost_reduction_percent", "value": 0.03, "skill_level_needed": "A", "description": "全事業所固定費3%削減"}, 
                {"type": "all_business_units_efficiency_boost", "value": 0.05, "skill_level_needed": "S", "description": "全事業所運営効率5%向上"}
            ]}
}
CXO_NAME_LIST: List[str] = ["影山敏夫", "一ノ瀬翔太", "橘美咲", "高城賢吾", "早乙女あきら", "黒木辰也", "白鳥エリカ", "龍崎司"]
CXO_RECRUITMENT_COST_BASE: float = 5_000_000
CXO_RECRUITMENT_COST_SKILL_MULTIPLIER: Dict[str, float] = {"S": 3.0, "A": 2.0, "B": 1.0, "C": 0.7}
MAX_CXOS_PER_COMPANY: int = 3
WEEKS_TO_REFRESH_CXO_MARKET: int = 26
