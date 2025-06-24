# models/personal_assets.py
from typing import List, Dict, Any, TYPE_CHECKING, Tuple
import collections

if TYPE_CHECKING:
    from .game_time import GameTime
    from .property import Property
    from .corporate_finance import CorporateFinance

from .portfolio import Portfolio
import constants

class PersonalAssets:
    """
    プレイヤーの個人資産(現金、不動産、ポートフォリオ、贅沢品など)を管理するクラス。
    """
    def __init__(self, initial_money: int):
        self.money: int = initial_money
        self.weekly_salary: float = 0.0
        self.properties: List['Property'] = []
        self.portfolio = Portfolio()
        self.owned_luxury_goods: List[Dict[str, Any]] = []
        self.stock_options: List[Dict[str, Any]] = []
        self.cumulative_upkeep_paid: float = 0.0

    def set_salary(self, new_salary: float):
        self.weekly_salary = new_salary

    def receive_salary(self):
        if self.weekly_salary > 0:
            self.money += int(self.weekly_salary)

    def withdraw(self, amount: float) -> Tuple[bool, float]:
        if amount <= 0: return False, 0
        if self.money >= amount:
            self.money -= int(amount)
            return True, amount
        else:
            print("個人資産が不足しています。")
            return False, 0

    def deposit(self, amount: float):
        if amount > 0:
            self.money += int(amount)

    # ★★★ このメソッドを追記しました ★★★
    def receive_dividend(self, ticker: str, dividend_per_share: float):
        """個人ポートフォリオの配当金を受け取り、資産に加える。"""
        # 1. ポートフォリオに配当額を計算させる
        dividend_amount = self.portfolio.receive_dividend(ticker, dividend_per_share)
        
        # 2. 計算された額を自分の現金に加算する
        if dividend_amount > 0:
            self.money += int(dividend_amount)
            print(f"  [個人] {ticker}から配当金 ¥{dividend_amount:,.0f} を受け取りました。")
    # ★★★ 追記ここまで ★★★

    def process_weekly_updates(self, game_time: 'GameTime', market_data: List[Any]):
        """個人資産に関わる週次の更新処理。"""
        # (このメソッドは変更ありません)
        # 1. 個人所有不動産の収支
        if self.properties:
            for prop in self.properties:
                if prop.weekly_rent_income > 0:
                    self.money += prop.weekly_rent_income
                if prop.weekly_maintenance_cost > 0:
                    if self.money >= prop.weekly_maintenance_cost:
                        self.money -= prop.weekly_maintenance_cost
                    else:
                        print(f"警告: 個人資産不足のため、不動産「{prop.name}」の維持費が支払えませんでした。")
        
        # 2. 贅沢品維持費
        upkeep_cost_total = sum(good.get("weekly_upkeep_cost", 0) for good in self.owned_luxury_goods)
        if upkeep_cost_total > 0:
            if self.money >= upkeep_cost_total:
                self.money -= upkeep_cost_total
                self.cumulative_upkeep_paid += upkeep_cost_total
            else:
                print(f"  警告: 個人資金不足のため、贅沢品の維持費 ¥{upkeep_cost_total:,.0f}が支払えませんでした。")
        
        # 3. ポートフォリオの金利・手数料支払い
        portfolio_costs = self.portfolio.calculate_interest_and_fees()
        if portfolio_costs > 0:
            if self.money >= portfolio_costs:
                self.money -= int(portfolio_costs)
            else:
                print(f"警告: 個人資金不足のため、ポートフォリオの金利・手数料 ¥{portfolio_costs:,.0f}が支払えませんでした。")

        # 4. ストックオプションの権利確定・期限切れチェック
        if self.stock_options:
            for option in self.stock_options:
                if option['is_exercised'] or option['is_expired']: continue
                if not option['is_vested'] and game_time.total_weeks_elapsed >= option['vesting_end_week']:
                    option['is_vested'] = True
                    print(f"  [個人通知] ストックオプション (ID: ...{option['grant_id'][-6:]}) の権利が確定しました。")
                if game_time.total_weeks_elapsed >= option['expiration_week'] and not option['is_exercised']:
                    option['is_expired'] = True
                    print(f"  [個人通知] ストックオプション (ID: ...{option['grant_id'][-6:]}) が行使期限切れとなりました。")

    def buy_property(self, property_to_buy: 'Property') -> bool:
        price = property_to_buy.purchase_price
        if self.money >= price:
            self.money -= price
            self.properties.append(property_to_buy)
            print(f"  [個人資産] 不動産 「{property_to_buy.name}」を購入しました。")
            return True
        else:
            print(f"  不動産購入失敗: 個人の資産が不足しています。")
            return False

    def sell_property(self, property_to_sell: 'Property') -> bool:
        if property_to_sell in self.properties:
            self.money += int(property_to_sell.current_value)
            self.properties.remove(property_to_sell)
            print(f"  個人所有の不動産 「{property_to_sell.name}」を売却しました。")
            return True
        else:
            print(f"  不動産売却失敗: あなた個人はその不動産を所有していません。")
            return False
            
    def buy_stock_on_cash(self, ticker: str, company_name: str, num_shares: int, price: float) -> bool:
        total_cost = num_shares * price
        if self.money < total_cost:
            print("  [個人資産] 現物買い失敗: 資金が不足しています。")
            return False
        
        self.money -= total_cost
        self.portfolio.buy_stock(ticker, company_name, num_shares, price, is_margin=False)
        print(f"  [個人資産] 現物買い: 「{company_name}」を{num_shares:,}株購入しました。")
        return True

    def buy_stock_on_margin(self, ticker: str, company_name: str, num_shares: int, price: float) -> bool:
        total_cost = num_shares * price
        required_cash = total_cost * constants.INITIAL_MARGIN_REQUIREMENT_RATIO
        
        if self.money < required_cash:
            print("  [個人資産] 信用買い失敗: 委託保証金が不足しています。")
            return False
        
        self.money -= required_cash
        self.portfolio.buy_stock(ticker, company_name, num_shares, price, is_margin=True)
        print(f"  [個人資産] 信用買い: 「{company_name}」を{num_shares:,}株購入しました。")
        return True

    def sell_stock(self, ticker: str, num_shares_to_sell: int, price: float) -> bool:
        avg_buy_price = self.portfolio.sell_stock(ticker, num_shares_to_sell)
        if avg_buy_price is None: return False
        
        proceeds = num_shares_to_sell * price
        self.money += int(proceeds)
        return True

    def short_sell_stock(self, ticker: str, company_name: str, num_shares: int, price: float, game_time: 'GameTime') -> bool:
        proceeds = num_shares * price
        self.money += int(proceeds)
        self.portfolio.short_sell(ticker, company_name, num_shares, price, game_time)
        return True

    def buy_to_cover_short(self, ticker: str, num_shares_to_cover: int, price: float) -> bool:
        cost_to_cover = num_shares_to_cover * price
        if self.money < cost_to_cover:
            print("  [個人資産] 買い戻し失敗: 資金が不足しています。")
            return False

        original_sell_price = self.portfolio.buy_to_cover(ticker, num_shares_to_cover)
        if original_sell_price is None: return False
        
        self.money -= int(cost_to_cover)
        return True
        
    def invest_in_venture(self, deal_data: Dict[str, Any], current_total_weeks: int) -> bool:
        investment_amount = deal_data["investment_amount_required"]
        if self.money < investment_amount:
            print("  [個人資産] ベンチャー投資失敗: 資金が不足しています。")
            return False

        self.money -= investment_amount
        self.portfolio.invest_in_venture(deal_data, current_total_weeks)
        print(f"  [個人資産] ベンチャー投資を実行しました。")
        return True
    
    def sell_owned_stock(self, stock_deal_id_to_sell: str) -> bool:
        # このメソッドは現在、player.py側で直接呼び出されていないため、
        # 必要であれば実装します。
        print("個人資産からのVC株売却は未実装です。")
        return False
