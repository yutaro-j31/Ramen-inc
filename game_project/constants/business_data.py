# constants/business_data.py
# 省略なしの完全なコードです。

from typing import List, Dict, Any, Tuple
from models.staff import Staff
from models.game_time import GameTime

# --- 立地データ ---
LOCATIONS_DATA: List[Dict[str, Any]] = [
    {"name": "駅前通り", "setup_multiplier": 1.5, "rent_base": 70_000, "sales_modifier": 1.20, "description": "人通りが多く高収益期待、ただし費用も高い。", "base_weekly_customer_pool": 1500},
    {"name": "商店街", "setup_multiplier": 1.0, "rent_base": 45_000, "sales_modifier": 1.00, "description": "地元客が多く安定した集客が見込めるが、大きな成長は難しい。", "base_weekly_customer_pool": 800},
    {"name": "オフィス街", "setup_multiplier": 1.2, "rent_base": 60_000, "sales_modifier": 1.10, "description": "平日ランチタイムは非常に混雑するが、夜間や休日は閑散としがち。", "base_weekly_customer_pool": 1200},
    {"name": "郊外ロードサイド", "setup_multiplier": 0.8, "rent_base": 30_000, "sales_modifier": 0.90, "description": "家賃は安いが、集客には工夫が必要。車での来店が主。", "base_weekly_customer_pool": 600},
    {"name": "湾岸倉庫街", "setup_multiplier": 0.7, "rent_base": 20_000, "sales_modifier": 0.80, "description": "物流拠点。特殊な需要があるが一般向けではない。", "base_weekly_customer_pool": 200},
    {"name": "高級住宅街", "setup_multiplier": 2.0, "rent_base": 150_000, "sales_modifier": 1.30, "description": "富裕層が多く、高単価なビジネスが成り立つ可能性。", "base_weekly_customer_pool": 700},
    {"name": "新興開発エリア", "setup_multiplier": 1.3, "rent_base": 50_000, "sales_modifier": 1.05, "description": "今後人口増加が見込まれる成長エリア。", "base_weekly_customer_pool": 900},
]

# --- 店舗運営関連 ---
DEFAULT_RAMEN_SHOP_TYPE_NAME: str = "ミライラーメン" # ★この行を追記しました
DEFAULT_EQUIPMENT_LEVEL: int = 1
BASE_SHOP_SETUP_COST: int = 7_000_000
EQUIPMENT_UPGRADE_COST_BASE: Dict[str, int] = { "ミライラーメン": 500_000 }
EQUIPMENT_UPGRADE_COST_FACTOR: Dict[str, int] = { "ミライラーメン": 1_000_000 }
MAX_EQUIPMENT_LEVEL: Dict[str, int] = { "ミライラーメン": 5 }
AVG_SPEND_PER_CUSTOMER_RAMEN_SHOP: float = 900.0
ATTRACTIVENESS_WEIGHTS: Dict[str, float] = { "equipment": 0.4, "menu_variety": 0.2, "staff_efficiency": 0.2, "rnd_quality": 0.2}
ATTRACTIVENESS_BASE_EQUIPMENT_SCORE: float = 10.0
ATTRACTIVENESS_BASE_MENU_ITEM_SCORE: float = 2.0
ATTRACTIVENESS_STAFF_EFFICIENCY_FACTOR: float = 50.0
ATTRACTIVENESS_RND_QUALITY_FACTOR: float = 100.0

# --- スタッフ候補 ---
STAFF_CANDIDATES: List[Staff] = [
    Staff(name="田中太郎", role="見習い", weekly_salary=20_000, efficiency_modifier=0.90),
    Staff(name="鈴木一郎", role="一般スタッフ", weekly_salary=30_000, efficiency_modifier=1.00),
    Staff(name="佐藤花子", role="熟練スタッフ", weekly_salary=45_000, efficiency_modifier=1.15),
    Staff(name="山田次郎", role="見習い", weekly_salary=22_000, efficiency_modifier=0.85),
    Staff(name="高橋三郎", role="一般スタッフ", weekly_salary=32_000, efficiency_modifier=1.05),
    Staff(name="伊藤さくら", role="店長候補", weekly_salary=60_000, efficiency_modifier=1.25),
]

# --- メニューアイテムマスターデータ ---
AVAILABLE_MENU_ITEMS_MASTER_DATA: List[Dict[str, Any]] = [
    {"name": "基本の醤油ラーメン", "price": 750, "cost": 225, "description": "昔ながらのあっさり醤油味。"},
    {"name": "濃厚味噌ラーメン", "price": 850, "cost": 290, "description": "数種類の味噌をブレンドした深みのある味わい。"},
    {"name": "豚骨ラーメン", "price": 800, "cost": 320, "description": "じっくり煮込んだ濃厚豚骨スープ。"},
    {"name": "塩ラーメン", "price": 780, "cost": 250, "description": "鶏と魚介の旨味を活かした透き通るスープ。"},
    {"name": "つけ麺", "price": 900, "cost": 300, "description": "濃厚魚介豚骨スープと太麺の組み合わせ。"},
    {"name": "チャーシュー丼", "price": 400, "cost": 150, "description": "特製タレで煮込んだチャーシューがたっぷり。"},
    {"name": "餃子 (5個)", "price": 350, "cost": 100, "description": "パリッとジューシーな自家製餃子。"},
    {"name": "瓶ビール", "price": 600, "cost": 250, "description": "キンキンに冷えたクラシックなビール。"},
    {"name": "味付け玉子", "price": 120, "cost": 40, "description": "ラーメンのトッピングに最適。"},
    {"name": "メンマ", "price": 100, "cost": 30, "description": "こだわりの極太メンマ。"},
    {"name": "ライス", "price": 150, "cost": 50, "description": "ラーメンのお供に。"},
    {"name": "激辛ラーメン", "price": 950, "cost": 350, "description": "挑戦者求む!"},
    {"name": "伝説の黄金中華そば", "price": 1500, "cost": 500, "description": "R&D限定: 厳選素材と秘伝の製法が生み出す至高の一杯。", "is_rnd_unlockable": True, "rnd_project_id_unlock": "RND001"},
]
DEFAULT_MENU_ITEMS_DATA: List[Dict[str, Any]] = [
    {"name": "基本の醤油ラーメン", "price": 750, "cost": 225},
    {"name": "濃厚味噌ラーメン", "price": 850, "cost": 290},
    {"name": "餃子 (5個)", "price": 350, "cost": 100}
]

# --- 本部関連コスト ---
HQ_RENTED_INITIAL_COST: int = 15_000_000
HQ_RENTED_WEEKLY_RENT: int = 1_500_000
HQ_OWNED_CONSTRUCTION_COST: int = 800_000_000

# --- 部門設置コスト ---
INVESTMENT_DEPT_SETUP_COST: int = 5_000_000
HR_DEPT_SETUP_COST: int = 4_000_000
RND_DEPT_SETUP_COST: int = 6_000_000
MARKETING_DEPT_SETUP_COST: int = 3_500_000

# --- 役員報酬関連 ---
MAX_PLAYER_WEEKLY_SALARY_PRIVATE_COMPANY_RATIO_TO_CASH: float = 0.01 
MAX_PLAYER_WEEKLY_SALARY_PUBLIC_COMPANY_RATIO_TO_PROFIT: float = 0.1 
MIN_PLAYER_WEEKLY_SALARY: float = 0

# --- 研究開発(R&D)システム関連 ---
RND_PROJECTS_DATA: List[Dict[str, Any]] = [
    {"id": "RND001", "name": "伝説の黄金中華そば開発", "description": "失われたレシピを再現し、究極のラーメンを開発する。", "cost_to_start": 5_000_000, "research_points_needed": 1000, "max_weekly_funding": 200_000, "min_weeks_duration": 20, "required_department": "rnd", "prerequisites": [], "bonus_effects": [{"type": "new_menu_item", "value": "伝説の黄金中華そば", "description":"新メニュー「伝説の黄金中華そば」が利用可能に"}]},
    {"id": "RND002", "name": "次世代麺打ち製法研究", "description": "全てのラーメンの品質を向上させる新しい麺の製法を研究する。", "cost_to_start": 3_000_000, "research_points_needed": 800, "max_weekly_funding": 150_000, "min_weeks_duration": 26, "required_department": "rnd", "prerequisites": [], "bonus_effects": [{"type": "ramen_shop_quality_boost", "value": 0.05, "description": "全ラーメン店の基本品質5%向上", "is_permanent": True}]},
    {"id": "RND003", "name": "集中仕入れシステム構築", "description": "仕入れルートを最適化し、全ラーメン店の材料費を恒久的に削減する。", "cost_to_start": 10_000_000, "research_points_needed": 1200, "max_weekly_funding": 300_000, "min_weeks_duration": 30, "required_department": "investment", "prerequisites": [], "bonus_effects": [{"type": "ramen_shop_cost_reduction", "value": 0.03, "description": "全ラーメン店の材料費3%削減", "is_permanent": True}]},
    {"id": "RND004", "name": "AI店舗運営効率化システム", "description": "AIを活用して店舗運営の無駄を省き、固定費を削減する。", "cost_to_start": 20_000_000, "research_points_needed": 1500, "max_weekly_funding": 500_000, "min_weeks_duration": 20, "required_department": "rnd", "prerequisites": ["RND003"], "bonus_effects": [{"type": "ramen_shop_fixed_cost_reduction_percent", "value": 0.02, "description": "全ラーメン店の固定費2%削減", "is_permanent": True}]}
]

# --- 競合他社システム関連 ---
NUMBER_OF_INITIAL_COMPETITORS: int = 3
COMPETITOR_NAME_TEMPLATES: List[str] = ["麺屋「{kanji_name}」", "ラーメン {latin_name}", "{place_name}の虎", "究極ラーメン {unique_word}"]
COMPETITOR_NAME_KANJI: List[str] = ["龍", "虎", "鳳凰", "王様", "一番", "無双", "匠"]
COMPETITOR_NAME_LATIN: List[str] = ["MAX", "KING", "ACE", "GOLD", "STAR", "ULTIMATE"]
COMPETITOR_NAME_PLACE: List[str] = ["渋谷", "新宿", "池袋", "銀座", "博多", "札幌"]
COMPETITOR_NAME_UNIQUE_WORD: List[str] = ["魂", "維新", "旋風", "伝説", "革命"]
COMPETITOR_INITIAL_CASH_RANGE: Tuple[int, int] = (50_000_000, 200_000_000)
COMPETITOR_INITIAL_SHOP_COUNT_RANGE: Tuple[int, int] = (1, 3)
COMPETITOR_WEEKLY_ACTION_PROBABILITY: float = 0.25
COMPETITOR_EXPANSION_PROBABILITY: float = 0.3
COMPETITOR_UPGRADE_PROBABILITY: float = 0.4
COMPETITOR_INVESTMENT_PROBABILITY: float = 0.2
COMPETITOR_TAKE_PROFIT_THRESHOLD: float = 1.3  
COMPETITOR_STOP_LOSS_THRESHOLD: float = 0.8   
COMPETITOR_MA_PROBABILITY: float = 0.05 

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

# --- 競合AIの難易度設定 ---
COMPETITOR_DIFFICULTY_SETTINGS = {
    # ★★★ 5段階評価に変更 ★★★
    1: {'name': "最弱", 'cash_range': (10_000_000, 50_000_000), 'action_prob': 0.15},
    2: {'name': "簡単", 'cash_range': (30_000_000, 100_000_000), 'action_prob': 0.20},
    3: {'name': "普通", 'cash_range': (80_000_000, 250_000_000), 'action_prob': 0.28},
    4: {'name': "困難", 'cash_range': (150_000_000, 500_000_000), 'action_prob': 0.35},
    5: {'name': "最恐", 'cash_range': (300_000_000, 800_000_000), 'action_prob': 0.45}
}
