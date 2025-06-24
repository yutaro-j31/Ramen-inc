# constants/game_settings.py
from typing import List, Dict, Any

# --- ゲーム基本設定 ---
INITIAL_PERSONAL_MONEY: int = 100_000_000
INITIAL_COMPANY_MONEY: int = 100_000_000
INITIAL_PLAYER_WEEKLY_SALARY: float = 0.0

# --- 役員報酬関連 ---
MAX_PLAYER_WEEKLY_SALARY_PRIVATE_COMPANY_RATIO_TO_CASH: float = 0.01 
MAX_PLAYER_WEEKLY_SALARY_PUBLIC_COMPANY_RATIO_TO_PROFIT: float = 0.1 
MIN_PLAYER_WEEKLY_SALARY: float = 0

# --- 個人資産の使い道: 贅沢品 ---
LUXURY_GOODS_DATA: List[Dict[str, Any]] = [ 
    {"id": "lux_watch_001", "name": "ミレニアムウォッチ エグゼクティブモデル", "category": "LUX_WATCH", "price": 25_000_000, "weekly_upkeep_cost": 50_000, "description": "熟練の技が光る、成功者の証。"},
    {"id": "lux_car_001", "name": "フェニックス自動車 GT-X", "category": "LUX_SUPERCAR", "price": 80_000_000, "weekly_upkeep_cost": 300_000, "description": "公道の野獣と称される圧倒的な加速力。"},
    {"id": "lux_estate_001", "name": "コートダジュール プライベートヴィラ", "category": "LUX_REAL_ESTATE", "price": 1_200_000_000, "weekly_upkeep_cost": 1_000_000, "description": "紺碧の海を望む、選ばれし者のための隠れ家。"},
    {"id": "lux_art_001", "name": "ゴッホンタ・ヌンシー作「夜明けのラーメンパーカー」", "category": "LUX_ART", "price": 150_000_000, "weekly_upkeep_cost": 10_000, "description": "印象派の巨匠が描いたとされる幻の一品。"}
]
