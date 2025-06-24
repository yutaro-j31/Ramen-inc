# constants/rnd_data.py
from typing import List, Dict, Any

# --- 研究開発(R&D)システム関連 ---
RND_PROJECTS_DATA: List[Dict[str, Any]] = [
    {"id": "RND001", "name": "伝説の黄金中華そば開発", "description": "失われたレシピを再現し、究極のラーメンを開発する。", "cost_to_start": 5_000_000, "research_points_needed": 1000, "max_weekly_funding": 200_000, "min_weeks_duration": 20, "required_department": "rnd", "prerequisites": [], "bonus_effects": [{"type": "new_menu_item", "value": "伝説の黄金中華そば", "description":"新メニュー「伝説の黄金中華そば」が利用可能に"}]},
    {"id": "RND002", "name": "次世代麺打ち製法研究", "description": "全てのラーメンの品質を向上させる新しい麺の製法を研究する。", "cost_to_start": 3_000_000, "research_points_needed": 800, "max_weekly_funding": 150_000, "min_weeks_duration": 26, "required_department": "rnd", "prerequisites": [], "bonus_effects": [{"type": "ramen_shop_quality_boost", "value": 0.05, "description": "全ラーメン店の基本品質5%向上", "is_permanent": True}]},
    {"id": "RND003", "name": "集中仕入れシステム構築", "description": "仕入れルートを最適化し、全ラーメン店の材料費を恒久的に削減する。", "cost_to_start": 10_000_000, "research_points_needed": 1200, "max_weekly_funding": 300_000, "min_weeks_duration": 30, "required_department": "investment", "prerequisites": [], "bonus_effects": [{"type": "ramen_shop_cost_reduction", "value": 0.03, "description": "全ラーメン店の材料費3%削減", "is_permanent": True}]},
    {"id": "RND004", "name": "AI店舗運営効率化システム", "description": "AIを活用して店舗運営の無駄を省き、固定費を削減する。", "cost_to_start": 20_000_000, "research_points_needed": 1500, "max_weekly_funding": 500_000, "min_weeks_duration": 20, "required_department": "rnd", "prerequisites": ["RND003"], "bonus_effects": [{"type": "ramen_shop_fixed_cost_reduction_percent", "value": 0.02, "description": "全ラーメン店の固定費2%削減", "is_permanent": True}]}
]
