# models/player.py
from typing import List, Dict, Any, TYPE_CHECKING, Optional, Tuple

if TYPE_CHECKING:
    from .business_unit import BusinessUnit
    from .game_time import GameTime
    from .listed_company import ListedCompany
    from .target_company import TargetCompany
    from .cxo import CXO
    from .property import Property

from .portfolio import Portfolio
from .corporate_finance import CorporateFinance
from .hr import HumanResources
from .personal_assets import PersonalAssets
from .operations import Operations
from .ipo_manager import IPOManager
from .corporate_development import CorporateDevelopment
from .effects_manager import EffectsManager
from .game_time import GameTime 
import constants 

class Player:
    def __init__(self, company_name: str, initial_personal_money: int, initial_company_money: int):
        self.company_name: str = company_name
        self.finance = CorporateFinance(initial_cash=float(initial_company_money))
        self.hr = HumanResources()
        self.ops = Operations()
        self.corp_dev = CorporateDevelopment()
        self.effects = EffectsManager()
        self.ipo = IPOManager()
        self.personal_assets = PersonalAssets(initial_money=initial_personal_money)
        self.company_portfolio = Portfolio()
        self.credit_rating_score: int = 600
        self.credit_rating: str = "BBB"
    
    @property
    def player_weekly_salary(self) -> float: return self.personal_assets.weekly_salary
    @player_weekly_salary.setter
    def player_weekly_salary(self, value: float): self.personal_assets.set_salary(value)
    @property
    def company_finances(self): return self.finance.finances
    @property
    def employed_cxos(self): return self.hr.employed_cxos
    @property
    def departments(self): return self.ops.departments
    @property
    def businesses_owned(self): return self.ops.businesses_owned
    @property
    def headquarters_type(self): return self.ops.headquarters_type
    @property
    def hq_weekly_rent(self): return self.ops.hq_weekly_rent
    @property
    def is_company_public(self): return self.ipo.is_company_public
    @property
    def ipo_preparation_weeks_remaining(self): return self.ipo.preparation_weeks_remaining
    @property
    def personal_portfolio(self): return self.personal_assets.portfolio
    @property
    def money_personal(self): return self.personal_assets.money
    @money_personal.setter
    def money_personal(self, value): self.personal_assets.money = value
    @property
    def completed_rnd_projects(self): return self.effects.completed_rnd_projects
    @property
    def estimated_recent_annual_revenue(self): return self.finance.estimated_recent_annual_revenue
    @property
    def estimated_recent_annual_net_profit(self): return self.finance.estimated_recent_annual_net_profit
    @property
    def owned_luxury_goods(self): return self.personal_assets.owned_luxury_goods
    @property
    def stock_options_personal(self): return self.personal_assets.stock_options

    def get_total_debt(self) -> float:
        bank_loan = self.finance.get_total_bank_loan()
        company_margin_loan = self.company_portfolio.margin_loan
        personal_margin_loan = self.personal_assets.portfolio.margin_loan
        bonds_payable = self.finance.get_total_bonds_payable()
        return bank_loan + company_margin_loan + personal_margin_loan + bonds_payable
        
    def receive_dividend(self, ticker: str, dividend_per_share: float):
        company_dividend = self.company_portfolio.receive_dividend(ticker, dividend_per_share)
        self.finance.add_revenue(company_dividend, 'dividend_income')
        self.personal_assets.receive_dividend(ticker, dividend_per_share)
    
    def process_weekly_updates(self, game_time: 'GameTime', market_data: List['ListedCompany']):
        self.ops.finalize_all_finances(self)
        self.finance.process_company_cashflow(operations=self.ops, hr=self.hr, player_salary=self.player_weekly_salary)
        self.personal_assets.receive_salary()
        self.personal_assets.process_weekly_updates(game_time, market_data)
        company_vc_events = self.company_portfolio.update_active_venture_investments(game_time)
        for event in company_vc_events:
            if event["type"] == "cash":
                amount = event["amount"]
                self.finance.add_revenue(amount, 'vc_exit')
                print(f"  [会社VC] 「{event['name']}」への投資が{event['outcome']}となり、¥{amount:,.0f} を受け取りました。")
            elif event["type"] == "stock":
                print(f"  [会社VC] 「{event['name']}」がIPOし、新たに株式を取得しました!")
            elif event["type"] == "funding_round":
                print(f"  [会社VC] 「{event['name']}」が次の資金調達ラウンドに進みました。対応が必要です。")
        company_portfolio_costs = self.company_portfolio.calculate_interest_and_fees()
        if company_portfolio_costs > 0: self.finance.record_expense(company_portfolio_costs, 'portfolio_costs')
        subsidiary_profit = self.corp_dev.get_total_weekly_subsidiary_profit()
        if subsidiary_profit != 0: self.finance.add_subsidiary_profit(subsidiary_profit)
        self.effects.process_weekly_updates(self.finance.finances, self.ops.get_total_weekly_variable_costs())
        if self.ipo.is_in_preparation: self.ipo.process_ipo_events(self, game_time, market_data)

    def process_quarterly_updates(self, game_time: 'GameTime', market_data: List['ListedCompany']):
        print("\n--- 四半期末処理: 財務・格付け更新 ---")
        self.finance.record_financial_snapshot(game_time, self)
        self.update_credit_rating(game_time, market_data)

    def update_credit_rating(self, game_time: 'GameTime', market_data: Optional[List[Any]] = None): pass
    
    def check_margin_call(self, owner_type: str, market_data: List[Any]) -> Tuple[bool, float]:
        if owner_type == "company": return self.company_portfolio.check_margin_call(market_data, self.finance.get_cash())
        elif owner_type == "personal": return self.personal_assets.portfolio.check_margin_call(market_data, self.personal_assets.money)
        return False, 0.0
    
    def hire_cxo(self, candidate: 'CXO') -> bool: return self.hr.hire_cxo(candidate)
    def fire_cxo(self, position: str) -> Optional['CXO']: return self.hr.fire_cxo(position)
    def take_loan(self, *args, **kwargs): return self.finance.take_loan(*args, **kwargs)
    def repay_loan(self, *args, **kwargs): return self.finance.repay_loan(*args, **kwargs)
    def issue_bond(self, *args, **kwargs): return self.finance.issue_bond(*args, **kwargs)
    
    def buy_property(self, owner_type: str, property_to_buy: 'Property') -> bool:
        if owner_type == "company": return self.ops.buy_company_property(property_to_buy, self.finance)
        elif owner_type == "personal": return self.personal_assets.buy_property(property_to_buy)
        return False

    def sell_property(self, owner_type: str, property_to_sell: 'Property') -> bool:
        if owner_type == "company": return self.ops.sell_company_property(property_to_sell, self.finance)
        elif owner_type == "personal": return self.personal_assets.sell_property(property_to_sell)
        return False

    def open_margin_account(self, owner_type: str) -> bool:
        cost = constants.MARGIN_ACCOUNT_OPENING_COST
        if owner_type == "company":
            if self.finance.get_cash() >= cost:
                self.finance.record_expense(cost, 'account_fee')
                self.company_portfolio.has_margin_account = True
                return True
        elif owner_type == "personal":
            if self.personal_assets.money >= cost:
                self.personal_assets.money -= cost
                self.personal_assets.portfolio.has_margin_account = True
                return True
        return False
    
    def buy_stock_on_cash(self, owner_type: str, ticker: str, company_name: str, num_shares: int, price: float) -> bool:
        if owner_type == "company": return self.finance.buy_stock_on_cash(self.company_portfolio, ticker, company_name, num_shares, price)
        elif owner_type == "personal": return self.personal_assets.buy_stock_on_cash(ticker, company_name, num_shares, price)
        return False

    def buy_stock_on_margin(self, owner_type: str, ticker: str, company_name: str, num_shares: int, price: float) -> bool:
        if owner_type == "company":
            if not self.company_portfolio.has_margin_account: print("  エラー: 会社の信用取引口座が開設されていません。"); return False
            return self.finance.buy_stock_on_margin(self.company_portfolio, ticker, company_name, num_shares, price)
        elif owner_type == "personal":
            if not self.personal_assets.portfolio.has_margin_account: print("  エラー: 個人の信用取引口座が開設されていません。"); return False
            return self.personal_assets.buy_stock_on_margin(ticker, company_name, num_shares, price)
        return False

    def sell_stock(self, owner_type: str, ticker: str, num_shares_to_sell: int, price: float) -> bool:
        if owner_type == "company": return self.finance.sell_stock(self.company_portfolio, ticker, num_shares_to_sell, price)
        elif owner_type == "personal": return self.personal_assets.sell_stock(ticker, num_shares_to_sell, price)
        return False

    def short_sell_stock(self, owner_type: str, ticker: str, company_name: str, num_shares: int, price: float, game_time: 'GameTime') -> bool:
        if owner_type == "company":
            if not self.company_portfolio.has_margin_account: print("  エラー: 会社の信用取引口座が開設されていません。"); return False
            return self.finance.short_sell_stock(self.company_portfolio, ticker, company_name, num_shares, price, game_time)
        elif owner_type == "personal":
            if not self.personal_assets.portfolio.has_margin_account: print("  エラー: 個人の信用取引口座が開設されていません。"); return False
            return self.personal_assets.short_sell_stock(ticker, company_name, num_shares, price, game_time)
        return False

    def buy_to_cover_short(self, owner_type: str, ticker: str, num_shares_to_cover: int, price: float) -> bool:
        if owner_type == "company": return self.finance.buy_to_cover_short(self.company_portfolio, ticker, num_shares_to_cover, price)
        elif owner_type == "personal": return self.personal_assets.buy_to_cover_short(ticker, num_shares_to_cover, price)
        return False

    def deposit_from_personal_to_company(self, amount: int) -> bool:
        success, withdrawn_amount = self.personal_assets.withdraw(amount)
        if success:
            self.finance.deposit(withdrawn_amount)
            print(f"個人資産から会社へ ¥{withdrawn_amount:,.0f} を入金しました。")
            return True
        return False
        
    def acquire_business(self, business: 'BusinessUnit', setup_cost: int, initial_company_capital: int) -> bool:
        # --- ここが修正箇所 ---
        # 個人資産からではなく、会社の財務から費用を処理する
        total_cost = setup_cost + initial_company_capital
        
        if self.finance.get_cash() < total_cost:
            print("エラー: acquire_businessで資金不足を検知")
            return False
            
        # 会社の経費として総コストを記録する
        self.finance.record_expense(total_cost, 'business_setup')
        self.ops.add_business(business)
        return True
        # --- ここまで修正 ---
        
    def establish_hq_rented(self, *args, **kwargs): return self.ops.establish_hq_rented(self.finance, *args, **kwargs)
    def establish_hq_owned(self, *args, **kwargs): return self.ops.establish_hq_owned(self.finance, *args, **kwargs)
    def establish_department(self, *args, **kwargs): return self.ops.establish_department(self.finance, *args, **kwargs)
    
    def invest_in_venture(self, owner_type: str, deal_data: Dict[str, Any], current_total_weeks: int) -> bool:
        if owner_type == "company":
            return self.finance.invest_in_venture(self.company_portfolio, deal_data, current_total_weeks)
        elif owner_type == "personal":
            return self.personal_assets.invest_in_venture(deal_data, current_total_weeks)
        return False
        
    def sell_owned_stock(self, owner_type: str, stock_deal_id_to_sell: str) -> bool:
        if owner_type == "company":
            print("会社の保有VC株売却機能は現在調整中です")
            return False
        elif owner_type == "personal":
            return self.personal_assets.sell_owned_stock(stock_deal_id_to_sell)
        return False
