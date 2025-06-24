# systems/venture_system.py (完全版)
import random
import uuid
from typing import List, Dict, Any, Optional

from models.player import Player
from models.game_time import GameTime
import constants
import utils

# --- モジュールレベル変数 ---
available_venture_deals: List[Dict[str, Any]] = []
MAX_DEALS_ON_MARKET = 5
WEEKS_TO_REFRESH_VENTURE_MARKET = 13
last_venture_market_refresh_week = -WEEKS_TO_REFRESH_VENTURE_MARKET


# --- 案件生成・市場更新 ---
def _generate_random_venture_deal(game_time: GameTime) -> Optional[Dict[str, Any]]:
    """ランダムなベンチャー投資案件を1件生成する"""
    if not constants.VENTURE_SECTORS_INFO or not constants.VENTURE_ROUND_DEFINITIONS:
        return None

    sector_key = random.choice(list(constants.VENTURE_SECTORS_INFO.keys()))
    sector_data = constants.VENTURE_SECTORS_INFO[sector_key]
    current_round_data = constants.VENTURE_ROUND_DEFINITIONS[0]

    base_valuation = random.uniform(current_round_data["valuation_base_range_jpy"][0], current_round_data["valuation_base_range_jpy"][1])
    valuation = base_valuation * sector_data.get("initial_valuation_base_multiplier", 1.0)
    valuation = round(valuation / 1_000_000) * 1_000_000

    funding_ask_percent = random.uniform(current_round_data["typical_funding_ask_percent_of_valuation"][0], current_round_data["typical_funding_ask_percent_of_valuation"][1])
    investment_amount_required = round(valuation * funding_ask_percent / 100_000) * 100_000
    
    equity_offer_percent = random.uniform(current_round_data["player_equity_offer_percent_range"][0], current_round_data["player_equity_offer_percent_range"][1])

    company_name = f"{random.choice(constants.COMPANY_NAME_ELEMENTS_PREFIX)}{random.choice(constants.COMPANY_NAME_ELEMENTS_MIDDLE)}{random.choice(['・テック','・ソリューションズ','・イノベーション'])}"
    deal_id = f"VCDEAL-{str(uuid.uuid4())[:8]}"

    deal = {
        "id": deal_id, "company_name": company_name, "sector": sector_key,
        "growth_stage": current_round_data["display_name"], "current_round_id": current_round_data["id"],
        "business_summary": random.choice(constants.VENTURE_DD_INFO_SNIPPETS.get("business_summary",[""])).format(sector=sector_key),
        "investment_amount_required": investment_amount_required,
        "offered_share_percent": round(equity_offer_percent * 100, 1),
        "current_valuation_jpy": valuation, "dd_level_performed": 0,
        "revealed_info": {key: False for level_info in constants.VENTURE_DD_LEVELS_INFO.values() for key in level_info["info_keys_revealed"]},
        "market_rating": random.choice(["★☆☆☆☆", "★★☆☆☆", "★★★☆☆", "★★★★☆", "★★★★★"]),
        "team_rating": random.choice(["Dランク", "Cランク", "Bランク", "Aランク", "Sランク"]),
        "financial_outlook_summary": random.choice(constants.VENTURE_DD_INFO_SNIPPETS['financial_outlook_summary']),
        "key_risks_summary": random.choice(constants.VENTURE_DD_INFO_SNIPPETS['key_risks_summary']),
        "founder_background_snippet": random.choice(constants.VENTURE_DD_INFO_SNIPPETS['founder_background_snippet']),
        "detailed_financial_projections": random.choice(constants.VENTURE_DD_INFO_SNIPPETS.get("detailed_financial_projections",[""])),
        "competitor_overview": random.choice(constants.VENTURE_DD_INFO_SNIPPETS.get("competitor_overview",[""])),
        "ip_status": random.choice(constants.VENTURE_DD_INFO_SNIPPETS.get("ip_status",[""])),
        "customer_traction_details": random.choice(constants.VENTURE_DD_INFO_SNIPPETS.get("customer_traction_details",[""])),
        "full_cap_table_summary": random.choice(constants.VENTURE_DD_INFO_SNIPPETS.get("full_cap_table_summary",[""])),
        "exit_strategy_discussion": random.choice(constants.VENTURE_DD_INFO_SNIPPETS.get("exit_strategy_discussion",[""])),
    }
    for key in constants.VENTURE_DD_LEVELS_INFO[0]["info_keys_revealed"]:
        if key in deal["revealed_info"]: deal["revealed_info"][key] = True
    return deal

def refresh_venture_deal_market(game_time: GameTime):
    global available_venture_deals, last_venture_market_refresh_week
    if game_time.total_weeks_elapsed < last_venture_market_refresh_week + WEEKS_TO_REFRESH_VENTURE_MARKET and available_venture_deals:
        return
    available_venture_deals = []
    for _ in range(MAX_DEALS_ON_MARKET):
        deal = _generate_random_venture_deal(game_time)
        if deal: available_venture_deals.append(deal)
    last_venture_market_refresh_week = game_time.total_weeks_elapsed
    if available_venture_deals: print(f"ベンチャー投資市場に新たに{len(available_venture_deals)}件の案件が登場しました。")


# --- ここからが追加された関数 ---

def get_deals_seeking_follow_on(player: Player) -> List[Dict[str, Any]]:
    """プレイヤーが投資済みで、追加投資を求めている案件のリストを返す"""
    deals_seeking_funding = []
    # 会社のポートフォリオをチェック
    for deal_id, deal in player.company_portfolio.active_venture_investments.items():
        if "追加資金調達ラウンド" in deal.get("current_status", ""):
            deals_seeking_funding.append(deal)
    # 個人のポートフォリオをチェック
    for deal_id, deal in player.personal_portfolio.active_venture_investments.items():
        if "追加資金調達ラウンド" in deal.get("current_status", ""):
            deals_seeking_funding.append(deal)
    return deals_seeking_funding

def get_available_deals_for_market() -> List[Dict[str, Any]]:
    """市場に出ている新規の投資案件リストを返す"""
    global available_venture_deals
    return available_venture_deals

def perform_dd(player: Player, deal_data: Dict[str, Any], dd_level: int) -> bool:
    """指定されたレベルのデューデリジェンスを実行する"""
    dd_info = constants.VENTURE_DD_LEVELS_INFO.get(dd_level)
    if not dd_info:
        return False
        
    cost = dd_info['cost']
    if player.finance.get_cash() < cost:
        print("デューデリジェンス費用が不足しています。")
        return False
        
    player.finance.record_expense(cost, 'venture_dd')
    
    # DDレベルと開示情報を更新
    deal_data['dd_level_performed'] = dd_level
    for key_to_reveal in dd_info["info_keys_revealed"]:
        if key_to_reveal in deal_data["revealed_info"]:
            deal_data["revealed_info"][key_to_reveal] = True
            
    return True

def execute_investment(player: Player, deal_data: Dict[str, Any], owner_type: str, game_time: GameTime) -> bool:
    """指定された案件に投資を実行する"""
    if player.invest_in_venture(owner_type, deal_data, game_time.total_weeks_elapsed):
        # 投資が成功したら、市場リストから案件を削除
        global available_venture_deals
        available_venture_deals = [d for d in available_venture_deals if d["id"] != deal_data["id"]]
        return True
    return False

# --- ここまでが追加された関数 ---


# --- UIおよびアクション関数 (CUI用) ---

def display_venture_deal_summary(deal_data: Dict[str, Any]):
    print(f"  企業名: {deal_data['company_name']} (ID: ...{deal_data['id'][-6:]})")
    print(f"  セクター: {deal_data['sector']}, 現在のラウンド: {deal_data['growth_stage']}")
    if deal_data["revealed_info"].get("business_summary"): print(f"  事業概要: {deal_data['business_summary']}")
    if deal_data["revealed_info"].get("funding_ask_range"): print(f"  要求投資額(本ラウンド): ¥{deal_data['investment_amount_required']:,.0f}")
    if deal_data["revealed_info"].get("equity_offered_range"): print(f"  提供株式割合(目安): {deal_data['offered_share_percent']:.1f}%")
    print(f"  実行済みDDレベル: {deal_data.get('dd_level_performed', 0)}")

def invest_in_venture(player: Player, selected_deal: Dict[str, Any], game_time: GameTime) -> bool:
    global available_venture_deals
    
    print("\n--- 投資資金源の選択 ---")
    print("  1: 会社資金で投資する")
    print("  2: 個人資産で投資する")
    print("  0: キャンセル")
    
    fund_choice = utils.get_integer_input("選択: ", 0, 2)
    if fund_choice is None or fund_choice == 0:
        print("投資をキャンセルしました。")
        return False

    owner_type = "company" if fund_choice == 1 else "personal"
    
    if player.invest_in_venture(owner_type, selected_deal, game_time.total_weeks_elapsed):
        available_venture_deals = [d for d in available_venture_deals if d["id"] != selected_deal["id"]]
        return True
    else:
        return False

def manage_single_venture_deal_menu(player: Player, deal_id: str, game_time: GameTime):
    global available_venture_deals
    
    deal_in_market = next((deal for deal in available_venture_deals if deal['id'] == deal_id), None)
    
    if deal_in_market is None:
        print("エラー: 選択された案件が見つかりませんでした。")
        return

    while True:
        print(f"\n--- ベンチャー投資案件詳細: {deal_in_market['company_name']} ---")
        display_venture_deal_summary(deal_in_market)
        
        current_dd_level = deal_in_market.get('dd_level_performed', 0)
        if current_dd_level > 0: 
            print("\n  --- デューデリジェンス開示情報 ---")
            for level in range(1, 4): 
                if current_dd_level >= level:
                    dd_level_info = constants.VENTURE_DD_LEVELS_INFO.get(level)
                    if dd_level_info:
                        print(f"    --- DDレベル{level}情報 ({dd_level_info['name']}) ---")
                        for key in dd_level_info["info_keys_revealed"]:
                            if key in deal_in_market and deal_in_market["revealed_info"].get(key):
                                print(f"      {constants.VENTURE_DD_DISPLAY_NAMES.get(key, key)}: {deal_in_market[key]}")
        
        print("\n  --- アクション ---")
        options: Dict[int, str] = {}
        action_data: Dict[int, Any] = {}
        next_option_num = 1

        if current_dd_level < 3:
            next_dd_level_to_perform = current_dd_level + 1
            if next_dd_level_to_perform in constants.VENTURE_DD_LEVELS_INFO:
                dd_info = constants.VENTURE_DD_LEVELS_INFO[next_dd_level_to_perform]
                print(f"  {next_option_num}: {dd_info['name']}を実行する (費用: ¥{dd_info['cost']:,})")
                options[next_option_num] = "perform_dd"
                action_data[next_option_num] = {"dd_level": next_dd_level_to_perform, "cost": dd_info['cost']}
                next_option_num += 1
        
        print(f"  {next_option_num}: この案件に投資する")
        options[next_option_num] = "invest"
        next_option_num += 1
        print(f"  0: 案件リストに戻る")
        options[0] = "back"

        choice = utils.get_integer_input("選択: ", 0, next_option_num - 1)
        if choice is None: continue
        
        action_key = options.get(choice)

        if action_key == "back": break
        elif action_key == "perform_dd":
            dd_params = action_data.get(choice)
            if dd_params:
                dd_level_to_perform = dd_params["dd_level"]
                dd_cost = dd_params["cost"]
                if player.finance.get_cash() >= dd_cost:
                    confirm_dd = input("よろしいですか? (y/n): ").lower()
                    if confirm_dd == 'y':
                        if perform_dd(player, deal_in_market, dd_level_to_perform):
                            print(f"{constants.VENTURE_DD_LEVELS_INFO[dd_level_to_perform]['name']}が完了し、追加情報が開示されました。")
                else:
                    print("デューデリジェンス費用が不足しています。")
        elif action_key == "invest":
            if invest_in_venture(player, deal_in_market, game_time):
                break

def handle_follow_on_investment(player: Player, deal_id: str, game_time: GameTime):
    """追加投資ラウンドのオファーを処理する"""
    target_deal = None
    owner_portfolio = None
    owner_type = ""
    
    if deal_id in player.company_portfolio.active_venture_investments:
        target_deal = player.company_portfolio.active_venture_investments[deal_id]
        owner_portfolio = player.company_portfolio
        owner_type = "company"
    elif deal_id in player.personal_portfolio.active_venture_investments:
        target_deal = player.personal_portfolio.active_venture_investments[deal_id]
        owner_portfolio = player.personal_portfolio
        owner_type = "personal"

    if not target_deal:
        print("エラー: 対象の案件が見つかりませんでした。")
        return

    print(f"\n--- 追加投資の要請: {target_deal['company_name']} ---")
    print(f"現在のラウンド: {target_deal['current_status']}")
    print(f"新たな企業評価額: ¥{target_deal['current_valuation_jpy']:,.0f}")
    print(f"要求される投資額: ¥{target_deal['investment_amount_required']:,.0f}")
    print(f"提供される株式割合: {target_deal['offered_share_percent']:.1f}%")

    confirm = input(f"この追加投資に応じますか? ({owner_type}資産から拠出) (y/n): ").lower()
    if confirm == 'y':
        if player.invest_in_venture(owner_type, target_deal, game_time.total_weeks_elapsed):
            target_deal["current_status"] = "進行中"
            next_round_info = owner_portfolio._get_next_round_info(target_deal["current_round_id"])
            if next_round_info:
                weeks_min, weeks_max = next_round_info["weeks_to_next_eval_range"]
                target_deal["weeks_to_next_event"] = random.randint(weeks_min, weeks_max) if weeks_max > 0 else 0
            else:
                target_deal["weeks_to_next_event"] = random.randint(52, 104)
    else:
        target_deal.setdefault('diluted_in_rounds', []).append(target_deal['current_round_id'])
        target_deal["current_status"] = f"進行中 ({target_deal['growth_stage']}を見送り)"
        
        next_round_info = owner_portfolio._get_next_round_info(target_deal["current_round_id"])
        if next_round_info:
            weeks_min, weeks_max = next_round_info["weeks_to_next_eval_range"]
            target_deal["weeks_to_next_event"] = random.randint(weeks_min, weeks_max) if weeks_max > 0 else 0
        else:
            target_deal["weeks_to_next_event"] = random.randint(52, 104)
        print("追加投資を見送りました。あなたの株式持分は希薄化される可能性があります。")

def view_active_investments(player: Player):
    """プレイヤーが現在所有しているベンチャー投資の一覧を表示する。"""
    print("\n--- 保有中のベンチャー投資一覧 ---")
    company_deals = player.company_portfolio.active_venture_investments
    personal_deals = player.personal_portfolio.active_venture_investments

    if not company_deals and not personal_deals:
        print("現在、進行中のベンチャー投資案件はありません。")
        return

    print("\n=== 会社ポートフォリオ ===")
    if not company_deals:
        print("  保有案件はありません。")
    else:
        for i, (deal_id, deal_data) in enumerate(company_deals.items()):
            print(f"  {i+1}. {deal_data.get('company_name', 'N/A')} (ID:...{deal_id[-6:]})")
            print(f"      ステータス: {deal_data.get('current_status', '不明')}, 次のイベントまで: {deal_data.get('weeks_to_next_event', 'N/A')}週")

    print("\n=== 個人ポートフォリオ ===")
    if not personal_deals:
        print("  保有案件はありません。")
    else:
        for i, (deal_id, deal_data) in enumerate(personal_deals.items()):
            print(f"  {i+1}. {deal_data.get('company_name', 'N/A')} (ID:...{deal_id[-6:]})")
            print(f"      ステータス: {deal_data.get('current_status', '不明')}, 次のイベントまで: {deal_data.get('weeks_to_next_event', 'N/A')}週")


def show_venture_investment_menu(player: Player, game_time: GameTime):
    """ベンチャー投資システムのメインメニュー"""
    global available_venture_deals 
    refresh_venture_deal_market(game_time)

    while True:
        print("\n--- ベンチャー投資市場 ---")
        
        action_options: Dict[int, Dict[str, Any]] = {}
        option_num = 1

        deals_seeking_funding = get_deals_seeking_follow_on(player)
        
        if deals_seeking_funding:
            print("【!】追加の資金調達を求めている投資先があります:")
            for deal in deals_seeking_funding:
                print(f"  {option_num}: {deal['company_name']} ({deal['current_status']})")
                action_options[option_num] = {"type": "follow_on", "deal_id": deal['id']}
                option_num += 1
            print("-" * 20)
        
        if available_venture_deals:
            print("投資可能な新規案件:")
            for deal in available_venture_deals:
                print(f"  {option_num}: {deal['company_name']} ({deal['sector']})")
                action_options[option_num] = {"type": "view_deal_details", "deal_id": deal['id']}
                option_num += 1
        else:
            print("現在、市場に新規投資可能な案件はありません。")
        
        print("-" * 20)
        
        total_active_deals = len(player.company_portfolio.active_venture_investments) + len(player.personal_portfolio.active_venture_investments)
        print(f"  {option_num}: 保有中のベンチャー投資一覧を見る ({total_active_deals}件)")
        action_options[option_num] = {"type": "view_active_investments"}
        
        print("  0: メインメニューに戻る")
        action_options[0] = {"type": "back"}
        
        max_choice = option_num
        choice = utils.get_integer_input(f"アクションを選択してください (0-{max_choice}): ", 0, max_choice)

        if choice is None: continue
        
        selected_action = action_options.get(choice)
        if not selected_action:
            print("無効な選択です。")
            continue

        action_type = selected_action.get("type")
        if action_type == "back":
            break
        elif action_type == "view_deal_details":
            manage_single_venture_deal_menu(player, selected_action["deal_id"], game_time)
        elif action_type == "follow_on":
            handle_follow_on_investment(player, selected_action["deal_id"], game_time)
        elif action_type == "view_active_investments":
            view_active_investments(player)
        else:
            print("無効な選択です。")
