# models/competitor_company.py
import random
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .game_time import GameTime
    from .business_unit import BusinessUnit
    from .player import Player
    from .listed_company import ListedCompany

from .portfolio import Portfolio
from .business_unit import BusinessUnit
import constants

class CompetitorCompany:
    """AIが操作する競合他社を表すクラス。"""
    def __init__(self, name: str, company_type: str, initial_cash: int, action_prob: float, game_time: 'GameTime'):
        self.name: str = name
        self.company_type: str = company_type
        self.cash: float = float(initial_cash)
        self.action_prob: float = action_prob # 行動確率を個別に設定
        self.businesses_owned: List['BusinessUnit'] = []
        self.portfolio: Portfolio = Portfolio()
        self.loans = [] # 将来的な拡張用
        
        # ゲーム開始時に最初の店舗を出店する
        initial_shops = random.randint(constants.COMPETITOR_INITIAL_SHOP_COUNT_RANGE[0], constants.COMPETITOR_INITIAL_SHOP_COUNT_RANGE[1])
        for _ in range(initial_shops):
            self._expand(game_time)

    def _expand(self, game_time: 'GameTime'):
        """新しい店舗を出店するAIロジック"""
        from constants.map_master_data import REGIONS_MASTER
        
        try:
            location_data = random.choice(REGIONS_MASTER)
        except IndexError:
            return 
        
        setup_cost = int(constants.BASE_SHOP_SETUP_COST * location_data['setup_multiplier'])
        
        if self.cash < setup_cost:
            return
        
        self.cash -= setup_cost
        
        shop_name = f"{self.name} {location_data['name']}店"
        
        new_shop = BusinessUnit(
            name=shop_name,
            business_type=constants.DEFAULT_RAMEN_SHOP_TYPE_NAME,
            location_name=location_data['name'],
            base_weekly_fixed_costs=float(location_data['rent_base']),
            location_sales_modifier=float(location_data['sales_modifier']),
            base_weekly_customer_pool=int(location_data['base_weekly_customer_pool'])
        )
        new_shop.equipment_level = random.randint(1, 2)
        self.businesses_owned.append(new_shop)
        print(f"  [AI] {self.name} が {location_data['name']} に新店舗を出店しました。")

    def _upgrade_shop(self):
        """最もレベルの低い店舗をアップグレードするAIロジック"""
        if not self.businesses_owned:
            return
        
        shop_to_upgrade = min(self.businesses_owned, key=lambda shop: shop.equipment_level)
        
        max_level = constants.MAX_EQUIPMENT_LEVEL.get(shop_to_upgrade.business_type, 5)
        if shop_to_upgrade.equipment_level >= max_level:
            return # 既に最大レベル

        upgrade_cost = shop_to_upgrade.get_next_upgrade_cost()
        
        if self.cash >= upgrade_cost:
            self.cash -= upgrade_cost
            shop_to_upgrade.upgrade_equipment()
            print(f"  [AI] {self.name} が {shop_to_upgrade.name} の設備をアップグレードしました。")

    def _invest_in_stocks(self, market_data: List['ListedCompany']):
        """株式市場に投資するAIロジック"""
        if not market_data:
            return
            
        investment_amount = self.cash * random.uniform(0.05, 0.15)
        if investment_amount < 100_000:
            return
        
        target_stock = random.choice(market_data)
        if target_stock.current_price > 0:
            num_shares = int(investment_amount / target_stock.current_price)
            if num_shares > 0:
                cost = num_shares * target_stock.current_price
                self.cash -= cost
                self.portfolio.buy_stock(target_stock.ticker_symbol, target_stock.company_name, num_shares, target_stock.current_price, is_margin=False)
                print(f"  [AI] {self.name} が {target_stock.company_name} の株を {num_shares} 株購入しました。")

    def take_weekly_action(self, game_time: 'GameTime', player: 'Player', market_data: List['ListedCompany'], competitors: List['CompetitorCompany']):
        """週ごとのAIの行動を決定・実行する"""
        if random.random() > self.action_prob:
            return None

        possible_actions = ['expand', 'upgrade', 'invest']
        action_weights = [constants.COMPETITOR_EXPANSION_PROBABILITY, constants.COMPETITOR_UPGRADE_PROBABILITY, constants.COMPETITOR_INVESTMENT_PROBABILITY]
        
        chosen_action = random.choices(possible_actions, weights=action_weights, k=1)[0]
        
        if chosen_action == 'expand':
            self._expand(game_time)
        elif chosen_action == 'upgrade':
            self._upgrade_shop()
        elif chosen_action == 'invest':
            self._invest_in_stocks(market_data)
            
        return None

    def process_interest_payments(self):
        """ローン金利の支払い(将来的な拡張用)"""
        pass

    def __str__(self) -> str:
        return f"{self.name} (キャッシュ: ¥{self.cash:,.0f}, 店舗数: {len(self.businesses_owned)})"
