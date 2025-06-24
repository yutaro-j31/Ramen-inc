# systems/competitor_ai_system.py
import random
from typing import List

from models.player import Player
from models.game_time import GameTime
from models.competitor_company import CompetitorCompany
from models.listed_company import ListedCompany
from models.portfolio import Portfolio
import constants

# --- モジュールレベル変数 ---
competitor_companies: List[CompetitorCompany] = []

# --- 初期化 ---
def initialize_competitors(num_competitors: int, difficulty_level: int, game_time: GameTime):
    """指定された数の競合他社を、指定された難易度で生成し、初期化する。"""
    global competitor_companies
    competitor_companies = []
    
    def _generate_random_competitor_name() -> str:
        """ランダムな競合名を作成する内部関数"""
        template = random.choice(constants.COMPETITOR_NAME_TEMPLATES)
        placeholders = {
            "kanji_name": random.choice(constants.COMPETITOR_NAME_KANJI),
            "latin_name": random.choice(constants.COMPETITOR_NAME_LATIN),
            "place_name": random.choice(constants.COMPETITOR_NAME_PLACE),
            "unique_word": random.choice(constants.COMPETITOR_NAME_UNIQUE_WORD)
        }
        return template.format(**placeholders)
        
    # 難易度設定を取得
    difficulty_setting = constants.COMPETITOR_DIFFICULTY_SETTINGS.get(difficulty_level, constants.COMPETITOR_DIFFICULTY_SETTINGS[3]) # デフォルトは「普通」
    cash_min, cash_max = difficulty_setting['cash_range']
    action_prob = difficulty_setting['action_prob']
        
    for _ in range(num_competitors):
        comp_name = _generate_random_competitor_name()
        comp_type = random.choice(["個人経営", "中小企業"])
        initial_cash = random.randint(cash_min, cash_max)
        
        competitor = CompetitorCompany(
            name=comp_name,
            company_type=comp_type,
            initial_cash=initial_cash,
            action_prob=action_prob, # 難易度に応じた行動確率を渡す
            game_time=game_time
        )
        competitor_companies.append(competitor)

    print(f"{len(competitor_companies)}社の競合他社(難易度: {difficulty_setting['name']})が設立されました。")

# --- 週次処理 ---
def prepare_all_for_competition():
    """全競合企業の競争準備を行う。"""
    if not competitor_companies: return
    for comp in competitor_companies:
        for biz_unit in comp.businesses_owned:
            biz_unit.prepare_for_weekly_competition(player=None)

def run_market_simulation_and_allocate_sales(player: Player):
    """市場シミュレーションを実行し、顧客を各店舗に割り振る。"""
    from models.business_unit import BusinessUnit
    
    all_shops: List[BusinessUnit] = []
    all_shops.extend(player.ops.businesses_owned)
    for comp in competitor_companies:
        all_shops.extend(comp.businesses_owned)

    if not all_shops: return

    total_attractiveness = sum(shop.attractiveness for shop in all_shops)
    if total_attractiveness == 0: return

    # 地域ごとの顧客プールを考慮した方がよりリアルだが、まずは全体で計算
    total_customer_pool = sum(getattr(shop, 'base_weekly_customer_pool', 500) for shop in all_shops)

    for shop in all_shops:
        market_share = shop.attractiveness / total_attractiveness if total_attractiveness > 0 else 0
        customers = int(total_customer_pool * market_share)
        shop.weekly_customers = customers

def finalize_all_competitor_finances():
    """全競合企業の週次決算を処理する。"""
    if not competitor_companies: return
    for comp in competitor_companies:
        comp_profit = 0
        for biz_unit in comp.businesses_owned:
            biz_unit.finalize_weekly_finances(player=None)
            comp_profit += biz_unit.finances.get('weekly_profit', 0)
        comp.cash += comp_profit

def process_weekly_competitor_actions(player: Player, game_time: GameTime, market_data: List[ListedCompany]):
    """競合他社の週次アクションを処理する。"""
    global competitor_companies
    if not competitor_companies: return
    
    acquired_this_week = []
    for comp in list(competitor_companies):
        if comp in acquired_this_week:
            continue

        if not hasattr(comp, 'portfolio'):
            comp.portfolio = Portfolio()

        portfolio_costs = comp.portfolio.calculate_interest_and_fees()
        if portfolio_costs > 0:
            comp.cash -= portfolio_costs
        
        comp.process_interest_payments()
        
        acquired_company = comp.take_weekly_action(game_time, player, market_data, competitor_companies)
        if acquired_company:
            acquired_this_week.append(acquired_company)

    if acquired_this_week:
        competitor_companies = [c for c in competitor_companies if c not in acquired_this_week]
