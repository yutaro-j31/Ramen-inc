# constants/venture_data.py
from typing import List, Dict, Any

VENTURE_SECTORS_INFO: Dict[str, Dict[str, Any]] = {
    "AI": {"summary_keywords": ["データ分析", "自動化", "予測モデル", "自然言語処理", "機械学習プラットフォーム"], "team_strength_bias": 0.1, "market_potential_bias": 0.2, "initial_valuation_base_multiplier": 1.2},
    "FinTech": {"summary_keywords": ["オンライン決済", "ブロックチェーン", "ロボアドバイザー", "レンディング", "モバイルバンキング"], "team_strength_bias": 0.15, "market_potential_bias": 0.15, "initial_valuation_base_multiplier": 1.1},
    "BioTech": {"summary_keywords": ["創薬", "遺伝子治療", "再生医療", "医療機器開発", "個別化医療"], "team_strength_bias": 0.2, "market_potential_bias": 0.25, "initial_valuation_base_multiplier": 1.5},
    "SaaS": {"summary_keywords": ["クラウド業務システム", "サブスクリプションモデル", "BtoBソリューション", "業務効率化ツール"], "team_strength_bias": 0.05, "market_potential_bias": 0.15, "initial_valuation_base_multiplier": 1.0},
    "エンタメテック": {"summary_keywords": ["VR/ARコンテンツ", "オンラインゲーム開発", "動画配信プラットフォーム", "インタラクティブアート"], "team_strength_bias": 0.1, "market_potential_bias": 0.2, "initial_valuation_base_multiplier": 1.1},
}

VENTURE_DD_INFO_SNIPPETS: Dict[str, List[str]] = {
    "business_summary": [
        "{sector}分野に革命を起こすべく設立されたスタートアップ。",
        "独自の技術で{sector}市場に新たな価値を提案する。",
        "未開拓の{sector}ニッチ市場をターゲットとする野心的な事業計画を持つ。"
    ],
    "financial_outlook_summary": [
        "高い成長率を見込んでおり、3年以内に市場シェア15%を目指す。",
        "初期投資回収は5年以内を計画、その後は安定したキャッシュフローを見込む。",
        "収益モデルは確立済みで、顧客獲得コストの低減が今後の鍵。",
        "ニッチ市場での独占的地位を背景に、高利益率を維持する戦略。",
        "赤字先行投資フェーズだが、ユーザーベース拡大により数年後の黒字化は確実視。"
    ],
    "key_risks_summary": [
        "主要技術者の離脱リスク。", "法規制変更による事業モデルへの影響。",
        "競合他社の模倣や価格競争の激化。", "資金調達の遅延による開発スケジュールの遅れ。",
        "市場の需要予測の誤り。", "特定の太客への依存度が高い。"
    ],
    "founder_background_snippet": [
        "連続起業家であり、過去に2社を成功させた実績を持つ。", "当該分野で15年以上の経験を持つ専門家チームが率いる。",
        "著名な研究機関出身のエンジニアが技術開発を担当。", "大手企業でのマネジメント経験豊富なリーダーシップ。",
        "若手ながら革新的なアイデアと情熱でチームを牽引。"
    ],
    "detailed_financial_projections": [
        "今後3年間で売上高500%成長、5年後の営業利益率20%を計画。",
        "ARR(年間経常収益)は現在1億円、来期は3億円を見込む。",
        "ユニットエコノミクスは健全で、LTV/CAC比は4.5を達成。"
    ],
    "competitor_overview": [
        "市場は寡占状態だが、弊社の技術は既存企業の牙城を崩すポテンシャルを持つ。",
        "競合は存在するが、ターゲット層が異なり、直接的な競合は少ない。",
        "先行者利益を活かし、ブランド認知度で競合を圧倒する戦略。"
    ],
    "ip_status": [
        "コア技術に関する基本特許を2件出願済み。",
        "関連技術について複数の特許ポートフォリオを構築中。",
        "特許戦略については専門の弁理士と顧問契約を締結済み。"
    ],
    "customer_traction_details": [
        "β版のユーザー数は1万人を突破し、エンゲージメント率は業界平均を上回る。",
        "主要顧客3社と長期契約を締結済み。",
        "口コミによるオーガニックな顧客獲得が順調に推移している。"
    ],
    "full_cap_table_summary": [
        "創業者チームが株式の70%を保有し、経営の安定性は高い。",
        "エンジェル投資家が複数参加しているが、議決権は限定的。",
        "従業員向けストックオプションプールを20%確保済み。"
    ],
    "exit_strategy_discussion": [
        "5年以内のNASDAQへの上場を最有力な目標としている。",
        "大手企業数社から既にM&Aの打診を受けている。",
        "事業拡大後、戦略的パートナーとの資本業務提携も視野に入れている。"
    ]
}

VENTURE_EVENT_PROBABILITIES: Dict[str, float] = {
    "NEXT_ROUND": 0.60,
    "EARLY_ACQUISITION": 0.20,
    "EARLY_IPO": 0.05,
    "STAGNATION_OR_FAILURE": 0.15
}

VENTURE_ROUND_DEFINITIONS: List[Dict[str, Any]] = [
    {"id": "SEED", "display_name": "シード", "order": 0, "valuation_base_range_jpy": (20_000_000, 200_000_000), "typical_funding_ask_percent_of_valuation": (0.1, 0.3), "weeks_to_next_eval_range": (30, 60), "success_modifier": 0.7, "required_dd_level": 1, "exit_possibility_modifier": 0.5, "player_equity_offer_percent_range": (0.10, 0.25)},
    {"id": "SERIES_A", "display_name": "シリーズA", "order": 1, "valuation_multiplier_from_previous_range": (1.5, 4.0), "typical_funding_ask_percent_of_valuation": (0.1, 0.25), "weeks_to_next_eval_range": (40, 70), "success_modifier": 0.85, "required_dd_level": 2, "exit_possibility_modifier": 0.7, "player_equity_offer_percent_range": (0.07, 0.20)},
    {"id": "SERIES_B", "display_name": "シリーズB", "order": 2, "valuation_multiplier_from_previous_range": (1.8, 3.5), "typical_funding_ask_percent_of_valuation": (0.08, 0.20), "weeks_to_next_eval_range": (52, 78), "success_modifier": 1.0, "required_dd_level": 2, "exit_possibility_modifier": 0.9, "player_equity_offer_percent_range": (0.03, 0.15)},
    {"id": "SERIES_C", "display_name": "シリーズC", "order": 3, "valuation_multiplier_from_previous_range": (2.0, 4.0), "typical_funding_ask_percent_of_valuation": (0.05, 0.15), "weeks_to_next_eval_range": (52, 90), "success_modifier": 1.1, "required_dd_level": 3, "exit_possibility_modifier": 1.1, "player_equity_offer_percent_range": (0.02, 0.10)},
    {"id": "SERIES_D", "display_name": "シリーズD", "order": 4, "valuation_multiplier_from_previous_range": (1.5, 3.0), "typical_funding_ask_percent_of_valuation": (0.03, 0.10), "weeks_to_next_eval_range": (52, 90), "success_modifier": 1.15, "required_dd_level": 3, "exit_possibility_modifier": 1.2, "player_equity_offer_percent_range": (0.01, 0.07)},
    {"id": "SERIES_E", "display_name": "シリーズE", "order": 5, "valuation_multiplier_from_previous_range": (1.2, 2.5), "typical_funding_ask_percent_of_valuation": (0.02, 0.08), "weeks_to_next_eval_range": (0,0), "success_modifier": 1.2, "required_dd_level": 3, "exit_possibility_modifier": 1.3, "player_equity_offer_percent_range": (0.01, 0.05)},
]
VENTURE_EXIT_PROBABILITIES = {"IPO": 0.15, "M_AND_A_HIGH": 0.25, "M_AND_A_LOW": 0.20, "STAGNATION": 0.25, "BANKRUPTCY": 0.15}
VENTURE_IPO_RETURN_MULTIPLIER_RANGE = (8.0, 30.0)
VENTURE_M_AND_A_HIGH_RETURN_MULTIPLIER_RANGE = (3.0, 10.0)
VENTURE_M_AND_A_LOW_RETURN_MULTIPLIER_RANGE = (1.1, 2.5)
VENTURE_STAGNATION_RETURN_MULTIPLIER_RANGE = (0.5, 1.0)
VENTURE_DD_LEVELS_INFO: Dict[int, Dict[str, Any]] = {
    0: {"name": "情報なし", "cost": 0, "duration_weeks": 0, "info_keys_revealed": ["company_name", "sector", "business_summary", "initial_valuation_estimate"]},
    1: {"name": "簡易DD", "cost": 500_000, "duration_weeks": 1, "info_keys_revealed": ["market_rating", "team_rating", "financial_outlook_summary", "funding_ask_range", "equity_offered_range"]},
    2: {"name": "標準DD", "cost": 2_500_000, "duration_weeks": 2, "info_keys_revealed": ["key_risks_summary", "founder_background_snippet", "detailed_financial_projections", "competitor_overview"]},
    3: {"name": "詳細DD", "cost": 8_000_000, "duration_weeks": 4, "info_keys_revealed": ["ip_status", "customer_traction_details", "full_cap_table_summary", "exit_strategy_discussion"]}
}
VENTURE_DD_DISPLAY_NAMES: Dict[str, str] = { "market_rating": "市場評価", "team_rating": "経営チーム評価", "financial_outlook_summary": "財務見通し概要", "funding_ask_range": "要求資金額レンジ", "equity_offered_range": "提供株式割合レンジ", "key_risks_summary": "主要リスク概要", "founder_background_snippet": "創業者経歴概要", "detailed_financial_projections": "詳細財務予測", "competitor_overview": "競合状況概要", "ip_status": "知的財産状況", "customer_traction_details": "顧客獲得状況詳細", "full_cap_table_summary": "資本構成サマリー", "exit_strategy_discussion": "出口戦略議論"}
VENTURE_PLAYER_MAJOR_SHAREHOLDER_THRESHOLD: float = 0.20
