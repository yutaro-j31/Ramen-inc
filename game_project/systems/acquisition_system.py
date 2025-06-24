# systems/acquisition_system.py
import random
import uuid
from typing import List, Dict, Any, Optional

from models.player import Player
from models.game_time import GameTime
from models.listed_company import ListedCompany
from models.target_company import TargetCompany
from models.business_unit import BusinessUnit
from systems import general_stock_market_system
from constants import (
    PRIVATE_COMPANY_INDUSTRIES, PRIVATE_COMPANY_SIZE_TEMPLATES, 
    PRIVATE_COMPANY_NAME_EXAMPLES, PRIVATE_MA_STRENGTH_SNIPPETS,
    PRIVATE_MA_WEAKNESS_SNIPPETS, PRIVATE_MA_SYNERGY_SNIPPETS,
    ACQUISITION_SYNERGY_EFFECTS,
    MA_PRIVATE_COMPANY_DD_COST,
    WEEKS_TO_REFRESH_PRIVATE_MA_MARKET
)
import utils

# --- モジュールレベル変数 ---
private_companies_for_sale: List[TargetCompany] = []
MAX_PRIVATE_COMPANIES_ON_MARKET = 5
last_private_ma_market_refresh_week = -WEEKS_TO_REFRESH_PRIVATE_MA_MARKET

# --- 案件生成・市場更新 ---
def _generate_random_private_target_company(game_time: GameTime) -> Optional[TargetCompany]:
    if not PRIVATE_COMPANY_INDUSTRIES or not PRIVATE_COMPANY_SIZE_TEMPLATES:
        return None
    industry = random.choice(PRIVATE_COMPANY_INDUSTRIES)
    size_tier_name = random.choices(
        list(PRIVATE_COMPANY_SIZE_TEMPLATES.keys()),
        weights=[0.6, 0.3, 0.1], k=1
    )[0]
    size_template = PRIVATE_COMPANY_SIZE_TEMPLATES[size_tier_name]
    est_revenue = random.uniform(size_template["annual_revenue_range"][0], size_template["annual_revenue_range"][1])
    est_profit_margin = random.uniform(size_template["net_profit_margin_range"][0], size_template["net_profit_margin_range"][1])
    employees = random.randint(size_template["employee_count_range"][0], size_template["employee_count_range"][1])
    ask_price_mult_min, ask_price_mult_max = size_template["asking_price_revenue_multiplier_range"]
    asking_price_min = round(est_revenue * ask_price_mult_min / 1_000_000) * 1_000_000
    asking_price_max = round(est_revenue * ask_price_mult_max / 1_000_000) * 1_000_000
    asking_price_min = max(1_000_000, asking_price_min)
    asking_price_max = max(asking_price_min, asking_price_max)
    name_examples = PRIVATE_COMPANY_NAME_EXAMPLES.get(industry, ["(不明な業種の会社)"])
    company_name = random.choice(name_examples) + f" ({size_tier_name})"
    description = f"{industry}を営む{size_tier_name}の非公開企業。市場での独自のポジションを持つ。"
    synergy_notes = random.sample(PRIVATE_MA_SYNERGY_SNIPPETS, k=random.randint(1,2)) if PRIVATE_MA_SYNERGY_SNIPPETS else []
    target = TargetCompany(name=company_name, industry=industry, estimated_annual_revenue=est_revenue, estimated_net_profit_margin=est_profit_margin, employee_count=employees, asking_price_min=asking_price_min, asking_price_max=asking_price_max, description=description, synergy_notes=synergy_notes, weeks_on_market=0)
    return target

def refresh_private_ma_market(game_time: GameTime):
    global private_companies_for_sale, last_private_ma_market_refresh_week
    if game_time.total_weeks_elapsed < last_private_ma_market_refresh_week + WEEKS_TO_REFRESH_PRIVATE_MA_MARKET and private_companies_for_sale:
        return
    private_companies_for_sale = []
    for _ in range(MAX_PRIVATE_COMPANIES_ON_MARKET):
        company = _generate_random_private_target_company(game_time)
        if company:
            private_companies_for_sale.append(company)
    last_private_ma_market_refresh_week = game_time.total_weeks_elapsed
    if private_companies_for_sale:
        print(f"非上場M&A市場に新たに{len(private_companies_for_sale)}件の案件が登場しました。")

def get_private_acquisition_targets(player: Player, game_time: GameTime) -> List[TargetCompany]:
    global private_companies_for_sale
    refresh_private_ma_market(game_time)
    return private_companies_for_sale

def perform_due_diligence(player: Player, target_company: TargetCompany) -> bool:
    cost = MA_PRIVATE_COMPANY_DD_COST
    if player.finance.get_cash() >= cost:
        player.finance.record_expense(cost, "due_diligence")
        target_company.dd_performed = True
        target_company.dd_revealed_strength = random.choice(PRIVATE_MA_STRENGTH_SNIPPETS)
        target_company.dd_revealed_weakness = random.choice(PRIVATE_MA_WEAKNESS_SNIPPETS)
        return True
    return False

def make_acquisition_offer(player: Player, target_company: TargetCompany, offer_amount: float, game_time: GameTime) -> bool:
    if player.finance.get_cash() < offer_amount:
        return False
    min_ask = target_company.asking_price_min
    max_ask = target_company.asking_price_max
    success_range = max_ask - min_ask
    offer_premium_ratio = (offer_amount - min_ask) / success_range if success_range > 0 else 1.0
    success_chance = 0.2 + (0.7 * offer_premium_ratio)
    
    if random.random() < success_chance:
        player.finance.record_expense(offer_amount, "acquisition")
        integration_results = player.corp_dev.integrate_acquired_private_company(target_company, game_time)
        
        # --- ここから追加 ---
        player.corp_dev.acquired_companies_log.append({
            'name': target_company.name,
            'type': '非上場企業買収',
            'cost': offer_amount,
            'week': game_time.get_date_string()
        })
        # --- ここまで追加 ---

        if 'new_businesses' in integration_results and integration_results['new_businesses']:
            for new_shop in integration_results['new_businesses']:
                player.ops.add_business(new_shop)
        if 'new_synergy' in integration_results and integration_results['new_synergy']:
            player.effects.add_synergy(integration_results['new_synergy']['id'], integration_results['new_synergy']['data'])
        if 'one_time_gain' in integration_results and integration_results['one_time_gain'] > 0:
            player.finance.add_revenue(integration_results['one_time_gain'], 'acquisition_gain')
            
        global private_companies_for_sale
        private_companies_for_sale = [c for c in private_companies_for_sale if c.company_id != target_company.company_id]
        return True
    else:
        return False
