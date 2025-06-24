# models/listed_company.py
# 省略なしの完全なコードです。

import random
import string
from typing import List, Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .player import Player
    from .game_time import GameTime

import constants

class ListedCompany:
    """
    一般市場に上場している企業を表すクラス。
    """
    def __init__(self, ticker_symbol: str, company_name: str, sector: str,
                 initial_market_cap: float, initial_price: float,
                 shares_outstanding: int, founded_year: int,
                 initial_pbr_multiplier: float,
                 description: str, major_shareholders: List[Dict[str, Any]],
                 earnings_forecast: Dict[str, float]):
        
        self.company_name: str = company_name
        self.ticker_symbol: str = ticker_symbol
        self.sector: str = sector
        self.founded_year: int = founded_year
        
        # ▼▼▼ 新しい属性を追加 ▼▼▼
        self.description: str = description
        self.major_shareholders: List[Dict[str, Any]] = major_shareholders
        self.quarterly_results_history: List[Dict[str, Any]] = []
        self.earnings_forecast: Dict[str, float] = earnings_forecast
        # ▲▲▲ 追加ここまで ▲▲▲
        
        self.current_price: float = initial_price
        self.market_cap: float = initial_market_cap
        self.shares_outstanding: int = shares_outstanding
        
        if initial_pbr_multiplier > 0:
            self.net_assets: float = self.market_cap / initial_pbr_multiplier
        else:
            self.net_assets: float = self.market_cap
            
        self.earnings_per_share_ttm: float = 0.0
        self.p_e_ratio: float = float('inf')
        self.update_financial_ratios()
        
        self.next_earnings_announcement_week: int = random.randint(1, 13)
        self.last_quarterly_dividend_per_share: float = 0.0
        
        self.historical_prices: List[float] = [self.current_price]
        
        self.is_subsidiary: bool = False

    def update_stock_price(self, economic_phase: str):
        """週次の株価変動を計算し、株価と関連指標を更新する。"""
        base_volatility_min, base_volatility_max = constants.BASE_WEEKLY_STOCK_PRICE_VOLATILITY
        price_change_rate = random.uniform(base_volatility_min, base_volatility_max)
        
        econ_impact_min, econ_impact_max = constants.STOCK_MARKET_ECONOMIC_IMPACT_WEEKLY.get(economic_phase, (0.0,0.0))
        price_change_rate += random.uniform(econ_impact_min, econ_impact_max)
        
        if random.random() < constants.STOCK_NEWS_EVENT_PROBABILITY_WEEKLY:
            news_impact = random.uniform(constants.STOCK_NEWS_IMPACT_RANGE[0], constants.STOCK_NEWS_IMPACT_RANGE[1])
            price_change_rate += news_impact
        
        new_price = self.current_price * (1 + price_change_rate)
        self.current_price = max(1.0, round(new_price, 2))
        
        self.historical_prices.append(self.current_price)
        if len(self.historical_prices) > 52:
            self.historical_prices.pop(0)
        
        self.update_financial_ratios()

    def update_financial_ratios(self):
        """現在の株価に基づいて財務指標を更新する。"""
        if self.shares_outstanding > 0:
            self.market_cap = self.current_price * self.shares_outstanding
            if self.earnings_per_share_ttm > 0:
                self.p_e_ratio = self.current_price / self.earnings_per_share_ttm
            else:
                self.p_e_ratio = float('inf')
        else:
            self.market_cap = 0
            self.p_e_ratio = float('inf')
            
    def get_book_value_per_share(self) -> float:
        """1株あたり純資産 (BPS) を計算する。"""
        if self.shares_outstanding > 0:
            return self.net_assets / self.shares_outstanding
        return 0.0

    def get_pbr_ratio(self) -> float:
        """株価純資産倍率 (PBR) を計算する。"""
        bps = self.get_book_value_per_share()
        if bps > 0:
            return self.current_price / bps
        return float('inf')

    def get_current_annual_dividend_yield_estimate(self) -> float:
        """現在の株価に基づいた、年間の配当利回り(推定)を計算する。"""
        if self.current_price > 0:
            from models.game_time import GameTime
            annual_dividend = self.last_quarterly_dividend_per_share * 4
            return annual_dividend / self.current_price
        return 0.0

    def process_earnings_announcement(self, game_time: 'GameTime'):
        """四半期決算発表を処理する。"""
        if self.next_earnings_announcement_week <= game_time.total_weeks_elapsed:
            base_eps = self.get_book_value_per_share() * 0.05 
            new_eps_quarterly = base_eps * random.uniform(0.5, 1.5)
            
            # 業績履歴を更新
            new_sales = (new_eps_quarterly * self.shares_outstanding) * (self.p_e_ratio if self.p_e_ratio != float('inf') and self.p_e_ratio > 0 else 20)
            new_profit = new_eps_quarterly * self.shares_outstanding
            self.quarterly_results_history.append({
                "year": game_time.current_year,
                "quarter": (game_time.current_month - 1) // 3 + 1,
                "sales": new_sales,
                "profit": new_profit
            })
            if len(self.quarterly_results_history) > 4: # 直近4四半期(1年分)のみ保持
                self.quarterly_results_history.pop(0)

            # TTM (Trailing Twelve Months) のEPSを更新
            self.earnings_per_share_ttm = sum(res['profit'] for res in self.quarterly_results_history) / self.shares_outstanding if self.shares_outstanding > 0 else 0
            
            self.next_earnings_announcement_week += 13 # 13週後
            self.update_financial_ratios()
            print(f"  [決算発表] {self.company_name} ({self.ticker_symbol}) が決算を発表しました。")

    def process_dividend_payment(self, player: 'Player', game_time: 'GameTime'):
        """四半期ごとの配当支払いを処理する。"""
        if (self.next_earnings_announcement_week - 1) == game_time.total_weeks_elapsed: 
            if self.earnings_per_share_ttm > 0:
                payout_ratio = random.uniform(0.2, 0.5)
                annual_dividend = self.earnings_per_share_ttm * payout_ratio
                self.last_quarterly_dividend_per_share = round(annual_dividend / 4, 2)
            else:
                self.last_quarterly_dividend_per_share = 0.0

            player.receive_dividend(self.ticker_symbol, self.last_quarterly_dividend_per_share)

    def get_weekly_profit_as_subsidiary(self) -> float:
        """子会社としての週次利益(推定)を返す。"""
        if self.p_e_ratio > 0 and self.p_e_ratio != float('inf'):
            annual_profit = self.market_cap / self.p_e_ratio
            from models.game_time import GameTime
            return annual_profit / GameTime.WEEKS_PER_YEAR
        return self.market_cap * 0.0005
