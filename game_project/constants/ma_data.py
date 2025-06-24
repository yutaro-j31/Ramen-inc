# constants/ma_data.py
from typing import List, Dict, Any, Tuple

# --- M&A / TOB 関連 ---
TOB_PREMIUM_RANGE_SUGGESTED: Tuple[float, float] = (0.20, 0.50)
TOB_BASE_SUCCESS_CHANCE: float = 0.60
TOB_ADVISORY_FEE_RATE_ON_FAILURE: float = 0.005 
MA_DD_COST_LISTED_COMPANY_TOB: int = 2_000_000 
MA_PRIVATE_COMPANY_DD_COST: int = 1_000_000 
WEEKS_TO_REFRESH_PRIVATE_MA_MARKET: int = 26 
PRIVATE_COMPANY_INDUSTRIES: List[str] = ["地域密着型ラーメンチェーン", "ローカルレストラン", "食品卸売業", "小規模ECサイト", "アプリ開発会社(小)", "デザイン事務所", "地域清掃サービス", "地域配送サービス"]
PRIVATE_COMPANY_SIZE_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "零細": {"annual_revenue_range": (10_000_000, 100_000_000), "net_profit_margin_range": (0.02, 0.10), "employee_count_range": (1, 10), "asking_price_revenue_multiplier_range": (0.3, 0.8)},
    "小規模": {"annual_revenue_range": (100_000_000, 500_000_000), "net_profit_margin_range": (0.03, 0.12), "employee_count_range": (10, 50), "asking_price_revenue_multiplier_range": (0.5, 1.2)},
    "中規模": {"annual_revenue_range": (500_000_000, 2_000_000_000), "net_profit_margin_range": (0.05, 0.15), "employee_count_range": (50, 200), "asking_price_revenue_multiplier_range": (0.8, 2.0)},
}
PRIVATE_COMPANY_NAME_EXAMPLES: Dict[str, List[str]] = {
    "地域密着型ラーメンチェーン": ["麺屋きずな", "一番軒", "地元家ラーメン", "こだわり亭", "ラーメン太陽"],
    "ローカルレストラン": ["キッチンひまわり", "味処さとやま", "海鮮料理かもめ", "グリル・サンセット"],
    "食品卸売業": ["フレッシュフーズ卸", "食材センターABC", "全国食材流通", "まごころ食材"],
    "小規模ECサイト": ["お取り寄せマート", "こだわり逸品店", "オンライン雑貨ポコ"],
    "アプリ開発会社(小)": ["スマホアプリ工房", "コードクリエイト", "デジタルソリューションズNEXT"],
    "デザイン事務所": ["アトリエ・デザイン", "クリエイティブスタジオ結", "ビジュアルワークス"],
    "地域清掃サービス": ["クリーンサポートみらい", "おそうじ本舗ローカル", "街美化サービス"],
    "地域配送サービス": ["クイックデリバリーつばめ", "ラストワンマイル便", "ご近所お届けサービス"]
}
PRIVATE_MA_STRENGTH_SNIPPETS: List[str] = ["地域での高い知名度と固定客", "独自の仕入れルートと品質管理", "経験豊富なベテラン従業員", "ニッチ市場での強固なポジション", "特定の技術やノウハウに強み", "安定したリピート顧客"]
PRIVATE_MA_WEAKNESS_SNIPPETS: List[str] = ["経営者の高齢化と後継者不在", "資金調達力に乏しく成長が頭打ち", "マーケティング戦略の不在", "旧態依然とした業務プロセス", "大手資本の参入による競争激化の懸念", "人材育成の遅れ"]
PRIVATE_MA_SYNERGY_SNIPPETS: List[str] = ["貴社の販売網活用で売上増期待", "共同仕入れによるコスト削減効果", "貴社のブランド力で信用向上", "既存事業との顧客層重複によるクロスセル", "技術・ノウハウの共有による新サービス開発", "バックオフィス業務の共通化による効率アップ"]
ACQUIRED_RAMEN_CHAIN_SHOPS_PER_EMPLOYEE_RANGE: Tuple[float, float] = (0.1, 0.3)
ACQUIRED_RAMEN_CHAIN_SHOPS_PER_REVENUE_RANGE: Tuple[float, float] = (20_000_000, 100_000_000)
ACQUIRED_RAMEN_CHAIN_MAX_NEW_SHOPS: int = 5
ACQUISITION_SYNERGY_EFFECTS: Dict[str, Dict[str, Any]] = {
    "食品卸売業": {"effect_type": "material_cost_reduction", "value": 0.05, "duration_weeks": 52 * 3, "description": "全店舗の材料費5%削減(3年間)"},
    "地域配送サービス": {"effect_type": "fixed_cost_reduction_total", "value_weekly_amount": 50000, "duration_weeks": 52 * 2, "description": "会社全体の固定費週5万円削減(2年間)"},
}

