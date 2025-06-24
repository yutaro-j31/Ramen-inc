# constants/finance_data.py
from typing import List, Dict, Any, Tuple

# --- 銀行ローン商品 ---
BANK_LOAN_PRODUCTS: List[Dict[str, Any]] = [
    {"bank_name": "ミライ銀行", "product_name": "事業拡大ローンS", "max_amount": 50_000_000, "interest_rate_weekly": 0.001, "repayment_weeks": 156},
    {"bank_name": "ミライ銀行", "product_name": "短期運転資金ローン", "max_amount": 20_000_000, "interest_rate_weekly": 0.0008, "repayment_weeks": 52},
    {"bank_name": "アオゾラ信金", "product_name": "地域応援ローン", "max_amount": 30_000_000, "interest_rate_weekly": 0.0012, "repayment_weeks": 104},
    {"bank_name": "グローバル・バンク", "product_name": "大型設備投資ローン", "max_amount": 1_000_000_000, "interest_rate_weekly": 0.0005, "repayment_weeks": 520},
    {"bank_name": "グローバル・バンク", "product_name": "不動産担保ローン", "max_amount": 5_000_000_000, "interest_rate_weekly": 0.0004, "repayment_weeks": 1040},
]

# --- 信用格付けシステム関連 ---
CREDIT_RATING_TIERS: Dict[str, int] = {
    "AAA": 900, "AA": 800, "A": 700, "BBB": 600, "BB": 500,
    "B": 400, "CCC": 300, "CC": 200, "C": 100, "D": 0
}
CREDIT_RATING_LOAN_MODIFIERS: Dict[str, Dict[str, float]] = {
    "AAA": {"interest_rate_adjustment": -0.0002, "max_loan_multiplier": 1.5},
    "AA":  {"interest_rate_adjustment": -0.0001, "max_loan_multiplier": 1.3},
    "A":   {"interest_rate_adjustment":  0.0,     "max_loan_multiplier": 1.1},
    "BBB": {"interest_rate_adjustment":  0.0001,  "max_loan_multiplier": 1.0},
    "BB":  {"interest_rate_adjustment":  0.0003,  "max_loan_multiplier": 0.8},
    "B":   {"interest_rate_adjustment":  0.0005,  "max_loan_multiplier": 0.6},
    "CCC": {"interest_rate_adjustment":  0.0010,  "max_loan_multiplier": 0.4},
    "CC":  {"interest_rate_adjustment":  0.0020,  "max_loan_multiplier": 0.2},
    "C":   {"interest_rate_adjustment":  0.0030,  "max_loan_multiplier": 0.1},
    "D":   {"interest_rate_adjustment":  0.0050,  "max_loan_multiplier": 0.0} 
}

# --- 社債発行関連 ---
BOND_ISSUANCE_FEE_RATE: float = 0.01 
BOND_MATURITY_YEARS_OPTIONS: List[int] = [3, 5, 10] 
BOND_BASE_YIELD: float = 0.03
BOND_CREDIT_SPREADS: Dict[str, float] = {
    "AAA": 0.000, "AA": 0.002, "A": 0.005, "BBB": 0.010,
    "BB":  0.020, "B":  0.035, "CCC": 0.050
}

# --- 信用取引関連 ---
MARGIN_ACCOUNT_OPENING_COST: int = 1_000_000
MARGIN_ACCOUNT_MIN_CREDIT_SCORE: int = 500 # BB以上
MARGIN_INTEREST_RATE_WEEKLY: float = 0.0003 
INITIAL_MARGIN_REQUIREMENT_RATIO: float = 0.5 
MAINTENANCE_MARGIN_REQUIREMENT_RATIO: float = 0.3
SHORT_SELLING_INTEREST_RATE_WEEKLY: float = 0.0005

# --- 一般株式市場関連 ---
NUMBER_OF_LISTED_COMPANIES: int = 300
STOCK_SECTORS: List[str] = ["テクノロジー", "金融", "ヘルスケア", "一般消費財", "資本財・サービス", "エネルギー", "素材", "電気通信サービス", "公益事業", "不動産"]
MARKET_CAP_TIERS: Dict[str, Dict[str, float]] = {
    "小型株": {"min": 5e9, "max": 1e11}, 
    "中型株": {"min": 1e11, "max": 1e12},
    "大型株": {"min": 1e12, "max": 5e13},
    "超大型株": {"min": 5e13, "max": 2e14}
}
MARKET_CAP_TIER_WEIGHTS: Dict[str, float] = {"小型株": 0.40, "中型株": 0.35, "大型株": 0.20, "超大型株": 0.05}
INITIAL_STOCK_PRICE_RANGE: Tuple[float, float] = (100.0, 5000.0)
BASE_WEEKLY_STOCK_PRICE_VOLATILITY: Tuple[float, float] = (-0.03, 0.035)
COMPANY_NAME_ELEMENTS_PREFIX: List[str] = ["日本", "東京", "グローバル", "ミライ", "パシフィック", "デジタル", "フロンティア", "ワールド", "サンライズ", "スター"]
COMPANY_NAME_ELEMENTS_MIDDLE: List[str] = ["産業", "テクノロジー", "製薬", "食品", "銀行", "重工", "不動産", "システム", "ネットワーク", "ライフサイエンス", "マテリアル", "オート", "コミュニケーションズ"]
COMPANY_NAME_ELEMENTS_SUFFIX: List[str] = ["株式会社", "ホールディングス", "グループ", "コーポレーション", "Inc.", "Ltd."]
TICKER_SYMBOL_LENGTH: int = 4
TARGET_ANNUAL_DIVIDEND_YIELD_RANGE: Tuple[float, float] = (0.005, 0.06)
STOCK_NEWS_IMPACT_RANGE: Tuple[float, float] = (-0.10, 0.10) 
STOCK_NEWS_EVENT_PROBABILITY_WEEKLY: float = 0.02 
INITIAL_PBR_MULTIPLIER_RANGE: Tuple[float, float] = (0.7, 3.0)
STOCK_MARKET_ECONOMIC_IMPACT_WEEKLY: Dict[str, Tuple[float, float]] = {
    "好景気": (0.0005, 0.0020), 
    "普通": (-0.0002, 0.0010), 
    "不景気": (-0.0020, -0.0005)
}
STOCK_NEWS_EVENT_CHANCE_PLAYER_VC: float = 0.03 
STOCK_NEWS_POSITIVE_IMPACT_PLAYER_VC: Tuple[float, float] = (0.03, 0.15)
STOCK_NEWS_NEGATIVE_IMPACT_PLAYER_VC: Tuple[float, float] = (-0.15, -0.03)

COMPANY_DESCRIPTION_TEMPLATES: List[str] = [
    "{sector}セクターにおける革新的な技術で知られるリーディングカンパニー。{founded_year}年の設立以来、安定した成長を続けている。",
    "高品質な製品群で高い市場シェアを誇る、{sector}分野の中核企業。グローバル展開も積極的に推進中。",
    "{founded_year}年創業の老舗企業。伝統と革新を両立させ、{sector}業界内で独自の地位を築いている。",
    "急成長中の{sector}市場において、破壊的なビジネスモデルで注目を集める新進気鋭の企業。",
    "環境技術に強みを持ち、持続可能な社会の実現に貢献する{sector}企業。ESG投資家からの評価も高い。"
]

MAJOR_SHAREHOLDER_NAMES: List[str] = [
    "日本マスタートラスト信託銀行株式会社",
    "株式会社日本カストディ銀行",
    "グローバル・アセット・マネジメント",
    "ミライ・インベストメント",
    "パシフィック・キャピタル",
    "創業者一族",
    "サンライズ・ファンド"
]
