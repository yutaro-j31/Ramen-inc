# models/portfolio.py
import collections
import uuid
import random
from typing import List, Dict, Any, TYPE_CHECKING, Optional, Tuple

if TYPE_CHECKING:
    from .game_time import GameTime
    from .corporate_finance import CorporateFinance

from .game_time import GameTime
import constants

class Portfolio:
    """
    株式、ベンチャー投資など、全ての投資ポートフォリオを管理するクラス。
    このクラスは資産の数量と平均取得価額のみを管理し、現金操作は行わない。
    """
    def __init__(self):
        self.active_venture_investments: Dict[str, Dict[str, Any]] = {}
        self.owned_stocks: List[Dict[str, Any]] = [] 
        self.general_stock_portfolio: Dict[str, Dict[str, Any]] = {}
        self.margin_loan: float = 0.0
        self.short_positions: Dict[str, Dict[str, Any]] = {}
        self.has_margin_account: bool = False

    def get_total_general_stock_value(self, market_data: Optional[List[Any]]) -> float:
        total_value = 0.0
        if market_data and self.general_stock_portfolio:
            for ticker, holding_info in self.general_stock_portfolio.items():
                market_company_data = next((c for c in market_data if hasattr(c, 'ticker_symbol') and c.ticker_symbol == ticker), None)
                total_shares_for_ticker = holding_info.get("cash_shares",0) + holding_info.get("margin_shares",0)
                
                if market_company_data and hasattr(market_company_data, 'current_price'):
                    total_value += total_shares_for_ticker * market_company_data.current_price
                else: 
                    total_value += total_shares_for_ticker * holding_info.get("average_buy_price", 0.0)
        return total_value
        
    def get_total_stock_value(self, market_data: Optional[List[Any]]) -> float:
        total_value = 0.0
        total_value += sum(s.get('current_market_value', 0) for s in self.owned_stocks)
        total_value += self.get_total_general_stock_value(market_data)
        return total_value
    
    def check_margin_call(self, market_data: List[Any], cash_balance: float) -> Tuple[bool, float]:
        if not (self.margin_loan > 0 or self.short_positions):
            return False, 0.0

        margin_long_value = 0.0
        for ticker, data in self.general_stock_portfolio.items():
            if data.get('margin_shares', 0) > 0:
                market_company = next((c for c in market_data if hasattr(c, 'ticker_symbol') and c.ticker_symbol == ticker), None)
                if market_company and hasattr(market_company, 'current_price'):
                    margin_long_value += data['margin_shares'] * market_company.current_price
        
        margin_loan_amount = self.margin_loan

        short_position_current_value = 0.0
        short_position_initial_proceeds = 0.0
        for ticker, data in self.short_positions.items():
            market_company = next((c for c in market_data if hasattr(c, 'ticker_symbol') and c.ticker_symbol == ticker), None)
            if market_company and hasattr(market_company, 'current_price'):
                short_position_current_value += data['shares'] * market_company.current_price
            
            short_position_initial_proceeds += data['shares'] * data['sell_price']

        total_equity = (cash_balance + margin_long_value + short_position_initial_proceeds) - \
                         (margin_loan_amount + short_position_current_value)

        total_position_value = margin_long_value + short_position_current_value
        maintenance_margin_required = total_position_value * constants.MAINTENANCE_MARGIN_REQUIREMENT_RATIO

        if total_equity < maintenance_margin_required:
            shortfall = maintenance_margin_required - total_equity
            return True, shortfall
            
        return False, 0.0

    def _update_portfolio_buy(self, ticker: str, company_name: str, num_shares: int, price: float, is_margin: bool):
        """株式購入時のポートフォリオ更新(内部処理)"""
        if ticker not in self.general_stock_portfolio:
            self.general_stock_portfolio[ticker] = {
                "company_name": company_name, "cash_shares": 0, "margin_shares": 0, "average_buy_price": 0.0
            }
        
        portfolio_item = self.general_stock_portfolio[ticker]
        current_total_shares = portfolio_item["cash_shares"] + portfolio_item["margin_shares"]
        current_avg_price = portfolio_item["average_buy_price"]
        
        new_total_shares = current_total_shares + num_shares
        if new_total_shares > 0:
            new_avg_price = ((current_total_shares * current_avg_price) + (num_shares * price)) / new_total_shares
            portfolio_item['average_buy_price'] = round(new_avg_price, 2)

        if is_margin:
            portfolio_item['margin_shares'] += num_shares
        else:
            portfolio_item['cash_shares'] += num_shares

    def buy_stock(self, ticker: str, company_name: str, num_shares: int, price: float, is_margin: bool):
        """株式を購入し、ポートフォリオに追加する。現金操作は行わない。"""
        self._update_portfolio_buy(ticker, company_name, num_shares, price, is_margin)
        if is_margin:
            loan_amount = (num_shares * price) * (1 - constants.INITIAL_MARGIN_REQUIREMENT_RATIO)
            self.margin_loan += loan_amount

    def sell_stock(self, ticker: str, num_shares_to_sell: int) -> Optional[float]:
        """株式を売却し、ポートフォリオから削除する。損益計算のために平均取得単価を返す。"""
        if ticker not in self.general_stock_portfolio: return None
            
        portfolio_item = self.general_stock_portfolio[ticker]
        cash_shares = portfolio_item.get('cash_shares', 0)
        margin_shares = portfolio_item.get('margin_shares', 0)
        total_shares = cash_shares + margin_shares
        
        if num_shares_to_sell > total_shares: return None

        avg_price = portfolio_item['average_buy_price']
        
        margin_shares_sold = min(num_shares_to_sell, margin_shares)
        if margin_shares_sold > 0:
            loan_ratio = (1 - constants.INITIAL_MARGIN_REQUIREMENT_RATIO)
            avg_loan_per_margin_share = avg_price * loan_ratio if margin_shares > 0 else 0
            loan_repayment_amount = min(self.margin_loan, avg_loan_per_margin_share * margin_shares_sold)
            self.margin_loan -= loan_repayment_amount
            portfolio_item['margin_shares'] -= margin_shares_sold

        cash_shares_sold = num_shares_to_sell - margin_shares_sold
        if cash_shares_sold > 0:
            portfolio_item['cash_shares'] -= cash_shares_sold
            
        if portfolio_item['cash_shares'] + portfolio_item['margin_shares'] == 0:
            del self.general_stock_portfolio[ticker]
        
        return avg_price 

    def short_sell(self, ticker: str, company_name: str, num_shares: int, price: float, game_time: 'GameTime'):
        """空売りを行い、ポジションを持つ。現金操作は行わない。"""
        if ticker in self.short_positions: return
        self.short_positions[ticker] = {
            "company_name": company_name, "shares": num_shares,
            "sell_price": price, "borrowed_week": game_time.total_weeks_elapsed
        }

    def buy_to_cover(self, ticker: str, num_shares_to_cover: int) -> Optional[float]:
        """空売りポジションを買い戻す。損益計算のために売建単価を返す。"""
        if ticker not in self.short_positions: return None
        
        position = self.short_positions[ticker]
        if num_shares_to_cover > position['shares']: return None

        original_sell_price = position['sell_price']
        
        position['shares'] -= num_shares_to_cover
        if position['shares'] <= 0:
            del self.short_positions[ticker]
        
        return original_sell_price

    def calculate_interest_and_fees(self) -> float:
        """信用取引の金利と貸株料を計算して、合計費用を返す。"""
        total_cost = 0.0
        if self.margin_loan > 0:
            total_cost += self.margin_loan * constants.MARGIN_INTEREST_RATE_WEEKLY
        
        if self.short_positions:
            for ticker, position in self.short_positions.items():
                position_value = position['shares'] * position['sell_price']
                total_cost += position_value * constants.SHORT_SELLING_INTEREST_RATE_WEEKLY
        return total_cost

    def invest_in_venture(self, deal_data: Dict[str, Any], current_total_weeks: int):
        """ベンチャー案件に投資し、ポートフォリオに追加する。"""
        invested_deal = deal_data.copy() 
        invested_deal["invested_week"] = current_total_weeks
        invested_deal["current_status"] = "進行中"
        if "player_investments" not in invested_deal: invested_deal["player_investments"] = []
        invested_deal["player_investments"].append({
            "round_id": deal_data["current_round_id"],
            "amount": deal_data["investment_amount_required"],
            "equity_percent": deal_data["offered_share_percent"]
        })
        
        round_data = next((r for r in constants.VENTURE_ROUND_DEFINITIONS if r["id"] == deal_data["current_round_id"]), None)
        if round_data:
             weeks_min, weeks_max = round_data["weeks_to_next_eval_range"]
             invested_deal["weeks_to_next_event"] = random.randint(weeks_min, weeks_max) if weeks_max > 0 else 0
        else:
             invested_deal["weeks_to_next_event"] = random.randint(52, 104)

        self.active_venture_investments[deal_data["id"]] = invested_deal
        
    def _get_next_round_info(self, current_round_id: str) -> Optional[Dict[str, Any]]:
        """現在のラウンドIDから次のラウンドの定義を取得する"""
        try:
            current_index = next(i for i, r in enumerate(constants.VENTURE_ROUND_DEFINITIONS) if r["id"] == current_round_id)
            if current_index + 1 < len(constants.VENTURE_ROUND_DEFINITIONS):
                return constants.VENTURE_ROUND_DEFINITIONS[current_index + 1]
        except StopIteration:
            pass
        return None

    def _resolve_venture_exit(self, deal_data: Dict[str, Any]) -> Dict[str, Any]:
        """VC投資の最終的な出口(IPO, M&A等)を決定し、結果を返す"""
        outcomes = list(constants.VENTURE_EXIT_PROBABILITIES.keys())
        weights = list(constants.VENTURE_EXIT_PROBABILITIES.values())
        chosen_outcome = random.choices(outcomes, weights=weights, k=1)[0]
        
        total_investment = sum(inv["amount"] for inv in deal_data.get("player_investments", []))
        event = {"name": deal_data['company_name'], "outcome": chosen_outcome}
        
        if chosen_outcome == "IPO":
            multiplier = random.uniform(*constants.VENTURE_IPO_RETURN_MULTIPLIER_RANGE)
            exit_value = total_investment * multiplier
            new_stock = {
                "deal_id": deal_data['id'], "company_name": deal_data["company_name"],
                "sector": deal_data["sector"], "acquired_value_at_ipo": total_investment,
                "current_market_value": exit_value,
                "shares_equivalent": sum(inv["equity_percent"] for inv in deal_data.get("player_investments", [])),
                "annual_dividend_rate": random.uniform(*constants.TARGET_ANNUAL_DIVIDEND_YIELD_RANGE)
            }
            self.owned_stocks.append(new_stock)
            event.update({"type": "stock", "data": new_stock})
            deal_data["current_status"] = "成功: IPO"

        elif chosen_outcome in ["M_AND_A_HIGH", "M_AND_A_LOW", "STAGNATION"]:
            ranges = {"M_AND_A_HIGH": constants.VENTURE_M_AND_A_HIGH_RETURN_MULTIPLIER_RANGE,
                      "M_AND_A_LOW": constants.VENTURE_M_AND_A_LOW_RETURN_MULTIPLIER_RANGE,
                      "STAGNATION": constants.VENTURE_STAGNATION_RETURN_MULTIPLIER_RANGE}
            multiplier = random.uniform(*ranges[chosen_outcome])
            cash_return = total_investment * multiplier
            event.update({"type": "cash", "amount": cash_return})
            deal_data["current_status"] = f"結果: {chosen_outcome}"

        elif chosen_outcome == "BANKRUPTCY":
            event.update({"type": "cash", "amount": 0})
            deal_data["current_status"] = "失敗: 倒産"
            
        return event

    def update_active_venture_investments(self, game_time: 'GameTime') -> List[Dict[str, Any]]:
        """進行中のVC投資を更新し、イベント(次のラウンド or 出口)を発生させる"""
        events = []
        deals_to_process = list(self.active_venture_investments.keys())

        for deal_id in deals_to_process:
            if deal_id not in self.active_venture_investments: continue
            
            deal_data = self.active_venture_investments[deal_id]
            
            if deal_data.get("weeks_to_next_event", 0) > 0:
                deal_data["weeks_to_next_event"] -= 1
                continue
            
            if deal_data.get("current_status") != "進行中":
                continue

            event_type = random.choices(
                list(constants.VENTURE_EVENT_PROBABILITIES.keys()),
                weights=list(constants.VENTURE_EVENT_PROBABILITIES.values()),
                k=1
            )[0]
            
            next_round_info = self._get_next_round_info(deal_data["current_round_id"])
            
            if not next_round_info or event_type != "NEXT_ROUND":
                exit_event = self._resolve_venture_exit(deal_data)
                events.append(exit_event)
                if deal_id in self.active_venture_investments:
                     del self.active_venture_investments[deal_id]
            else:
                deal_data["current_status"] = f"追加資金調達ラウンド ({next_round_info['display_name']})"
                deal_data["current_round_id"] = next_round_info['id']
                
                val_multiplier = random.uniform(*next_round_info["valuation_multiplier_from_previous_range"])
                new_valuation = deal_data["current_valuation_jpy"] * val_multiplier
                deal_data["current_valuation_jpy"] = round(new_valuation / 1_000_000) * 1_000_000
                
                funding_ask_percent = random.uniform(*next_round_info["typical_funding_ask_percent_of_valuation"])
                deal_data["investment_amount_required"] = round(deal_data["current_valuation_jpy"] * funding_ask_percent / 100_000) * 100_000
                
                equity_offer_percent = random.uniform(*next_round_info["player_equity_offer_percent_range"])
                deal_data["offered_share_percent"] = round(equity_offer_percent * 100, 1)

                events.append({"type": "funding_round", "data": deal_data, "name": deal_data['company_name']})
            
        return events
        
    def add_stock_from_option(self, option_data: Dict[str, Any], game_time: 'GameTime'):
        self._update_portfolio_buy(
            ticker=option_data['ticker_symbol'],
            company_name=option_data['company_name'],
            num_shares=option_data['num_shares'],
            price=option_data['strike_price'],
            is_margin=False
        )
        
    def receive_dividend(self, ticker: str, dividend_per_share: float) -> float:
        """一般市場株の配当金合計額を計算して返す"""
        dividend_income = 0.0
        if ticker in self.general_stock_portfolio:
            holding_info = self.general_stock_portfolio[ticker]
            owned_shares = holding_info.get("cash_shares", 0) + holding_info.get("margin_shares", 0)
            dividend_income = owned_shares * dividend_per_share
        return dividend_income
