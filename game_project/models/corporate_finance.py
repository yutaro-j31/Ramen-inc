# models/corporate_finance.py
import collections
import uuid
from typing import List, Dict, Any, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from .player import Player
    from .game_time import GameTime
    from .operations import Operations
    from .hr import HumanResources
    from .portfolio import Portfolio

from .loan import Loan
from .bond import Bond
from .game_time import GameTime
import constants

class CorporateFinance:
    """会社の財務、ローン、社債を管理するクラス。"""
    def __init__(self, initial_cash: float):
        self.finances: collections.defaultdict[str, float] = collections.defaultdict(float)
        self.finances['cash'] = initial_cash
        self.active_loans: List[Loan] = []
        self.outstanding_bonds: List[Bond] = []
        self.financial_history: List[Dict[str, Any]] = []
        self.estimated_recent_annual_revenue: float = 0.0
        self.estimated_recent_annual_net_profit: float = 0.0

    def get_cash(self) -> float:
        return self.finances.get('cash', 0.0)

    def deposit(self, amount: float):
        if amount > 0:
            self.finances['cash'] += amount

    def record_expense(self, amount: float, category: str = 'misc'):
        if amount > 0:
            self.finances['cash'] -= amount
            self.finances['total_costs'] += amount
            key = f'cumulative_{category}_cost'
            self.finances[key] = self.finances.get(key, 0.0) + amount
    
    def add_revenue(self, amount: float, category: str = 'misc'):
        if amount > 0:
            self.finances['cash'] += amount
            self.finances['total_sales'] += amount
            key = f'cumulative_{category}_revenue'
            self.finances[key] = self.finances.get(key, 0.0) + amount

    def add_subsidiary_profit(self, profit: float):
        self.finances['cash'] += profit
        if profit > 0:
            self.finances['total_sales'] += profit
        else:
            self.finances['total_costs'] += abs(profit)
        self.finances['cumulative_subsidiary_income'] = self.finances.get('cumulative_subsidiary_income', 0.0) + profit

    def get_net_profit(self) -> float:
        return self.finances.get('total_sales', 0.0) - self.finances.get('total_costs', 0.0)

    def get_total_bank_loan(self) -> float:
        return sum(loan.remaining_principal for loan in self.active_loans)

    def get_total_bonds_payable(self) -> float:
        return sum(bond.principal for bond in self.outstanding_bonds if not bond.is_redeemed)

    def process_company_cashflow(self, operations: 'Operations', hr: 'HumanResources', player_salary: float):
        """会社の週次キャッシュフローを計算・処理する統合メソッド"""
        business_sales, business_costs = operations.get_weekly_financials()
        self.add_revenue(business_sales, 'operations')
        self.record_expense(business_costs, 'operations')

        if player_salary > 0:
            if self.get_cash() >= player_salary:
                self.record_expense(player_salary, 'player_salary')
            else:
                print(f"  警告: 会社資金不足のため、役員報酬 ¥{player_salary:,.0f}が支払えませんでした。")

        cxo_salaries = hr.get_total_weekly_salary()
        if cxo_salaries > 0:
            if self.get_cash() >= cxo_salaries:
                self.record_expense(cxo_salaries, 'cxo_salaries')
            else:
                print(f"  警告: 会社資金不足のため、CXO給与合計 ¥{cxo_salaries:,.0f}が支払えませんでした。")

        if operations.headquarters_type == "賃貸オフィス" and operations.hq_weekly_rent > 0:
            if self.get_cash() >= operations.hq_weekly_rent:
                self.record_expense(operations.hq_weekly_rent, 'hq_rent')
            else:
                print(f"  警告: 会社資金不足のため、本部家賃 ¥{operations.hq_weekly_rent:,.0f}が支払えませんでした。")
        
        self.process_weekly_loan_interest()
        self.process_weekly_bond_interest()

    def take_loan(self, amount: float, weekly_rate: float, lender_name: str, product_name: str, repayment_weeks: int, game_time: 'GameTime') -> bool:
        new_loan = Loan(principal=amount, weekly_rate=weekly_rate, total_weeks=repayment_weeks, issued_week=game_time.total_weeks_elapsed, lender_name=lender_name, product_name=product_name)
        self.active_loans.append(new_loan)
        self.deposit(amount)
        print(f"  {lender_name}の「{product_name}」から ¥{amount:,.0f} を借入しました。")
        return True

    def repay_loan(self, loan_id_to_repay: str, amount_to_repay: float) -> bool:
        loan_to_repay = next((loan for loan in self.active_loans if loan.loan_id == loan_id_to_repay), None)
        if not loan_to_repay:
            print("エラー: 指定されたIDのローンが見つかりません。")
            return False
        
        repaid_amount = min(amount_to_repay, loan_to_repay.remaining_principal)
        if self.get_cash() < repaid_amount:
            print("返済資金が不足しています。")
            return False
        
        self.record_expense(repaid_amount, 'loan_repayment')
        loan_to_repay.remaining_principal -= repaid_amount
        print(f"  ローン(ID: ...{loan_to_repay.loan_id[-6:]})の一部として ¥{repaid_amount:,.0f} を返済しました。")
        
        if loan_to_repay.remaining_principal <= 0:
            print(f"  ローン(ID: ...{loan_to_repay.loan_id[-6:]})は完済されました。")
            self.active_loans.remove(loan_to_repay)
        
        return True

    def process_weekly_loan_interest(self):
        total_interest = sum(loan.calculate_interest() for loan in self.active_loans)
        if total_interest > 0:
             if self.get_cash() >= total_interest:
                self.record_expense(total_interest, 'loan_interest')
             else:
                print(f"  警告: 会社資金不足のため、ローン利息 ¥{total_interest:,.2f}の支払いができませんでした。")

    def issue_bond(self, principal: float, annual_coupon_rate: float, maturity_years: int, game_time: 'GameTime') -> bool:
        maturity_weeks = maturity_years * GameTime.WEEKS_PER_YEAR
        new_bond = Bond(principal=principal, annual_coupon_rate=annual_coupon_rate, maturity_weeks=maturity_weeks, issued_week=game_time.total_weeks_elapsed)
        self.outstanding_bonds.append(new_bond)
        self.deposit(principal)
        print(f"\n[資金調達] 新規社債を発行し、¥{principal:,.0f} を調達しました。")
        print(f"  (年利: {annual_coupon_rate:.2%}, {maturity_years}年債)")
        return True

    def process_weekly_bond_interest(self):
        if not self.outstanding_bonds: return
        total_interest = sum(bond.weekly_interest_payment for bond in self.outstanding_bonds if not bond.is_redeemed)
        if total_interest > 0:
            if self.get_cash() >= total_interest:
                self.record_expense(total_interest, 'bond_interest')
            else:
                print(f"!!! 警告: 会社資金不足のため、社債の利息 ¥{total_interest:,.0f}の支払いできませんでした。デフォルトのリスクがあります。 !!!")


    def process_bond_maturities(self, game_time: 'GameTime'):
        matured_bonds = [bond for bond in self.outstanding_bonds if bond.redemption_week <= game_time.total_weeks_elapsed and not bond.is_redeemed]
        for bond in matured_bonds:
            print(f"\n[財務イベント] 社債 (ID: ...{bond.bond_id[-6:]}) が満期を迎えました。元本 ¥{bond.principal:,.0f} の償還が必要です。")
            if self.get_cash() >= bond.principal:
                self.record_expense(bond.principal, 'bond_redemption')
                bond.is_redeemed = True
                print(f"  社債の元本 ¥{bond.principal:,.0f} を償還しました。")
            else:
                print(f"!!! 重大警告: 会社資金不足のため、満期を迎えた社債の元本 ¥{bond.principal:,.0f} を償還できません! デフォルトとなります。 !!!")
        self.outstanding_bonds = [bond for bond in self.outstanding_bonds if not bond.is_redeemed]

    def record_financial_snapshot(self, game_time: 'GameTime', player: 'Player'):
        snapshot = {"week": game_time.total_weeks_elapsed, "year": game_time.current_year, "month": game_time.current_month, "total_sales": self.finances['total_sales'], "total_costs": self.finances['total_costs'], "net_profit": self.get_net_profit(), "cash": self.get_cash(), "total_debt": player.get_total_debt()}
        self.financial_history.append(snapshot)
        if len(self.financial_history) > 52 * 5: self.financial_history.pop(0)

    def get_estimated_annuals(self, game_time: 'GameTime') -> Tuple[float, float]:
        if not self.financial_history:
            self.estimated_recent_annual_revenue = 0.0
            self.estimated_recent_annual_net_profit = 0.0
            return 0.0, 0.0
        one_year_ago_week = game_time.total_weeks_elapsed - GameTime.WEEKS_PER_YEAR
        one_year_ago_snapshot = None
        for snapshot in reversed(self.financial_history):
            if snapshot["week"] <= one_year_ago_week:
                one_year_ago_snapshot = snapshot
                break
        if one_year_ago_snapshot:
            current_snapshot = self.financial_history[-1]
            revenue = current_snapshot["total_sales"] - one_year_ago_snapshot["total_sales"]
            profit = current_snapshot["net_profit"] - one_year_ago_snapshot["net_profit"]
            self.estimated_recent_annual_revenue = max(0, revenue)
            self.estimated_recent_annual_net_profit = profit
            return self.estimated_recent_annual_revenue, self.estimated_recent_annual_net_profit
        elif game_time.total_weeks_elapsed > 0:
            first_snapshot = self.financial_history[0]
            current_snapshot = self.financial_history[-1]
            weeks_operated = current_snapshot["week"] - first_snapshot.get("week", 0)
            if weeks_operated > 0:
                period_sales = current_snapshot["total_sales"] - first_snapshot.get("total_sales", 0.0)
                period_profit = current_snapshot["net_profit"] - first_snapshot.get("net_profit", 0.0)
                est_annual_revenue = (period_sales / weeks_operated) * GameTime.WEEKS_PER_YEAR
                est_annual_profit = (period_profit / weeks_operated) * GameTime.WEEKS_PER_YEAR
                self.estimated_recent_annual_revenue = max(0, est_annual_revenue)
                self.estimated_recent_annual_net_profit = est_annual_profit
                return self.estimated_recent_annual_revenue, self.estimated_recent_annual_net_profit
        self.estimated_recent_annual_revenue = 0.0
        self.estimated_recent_annual_net_profit = 0.0
        return 0.0, 0.0
        
    def buy_stock_on_cash(self, portfolio: 'Portfolio', ticker: str, company_name: str, num_shares: int, price: float) -> bool:
        total_cost = num_shares * price
        if self.get_cash() < total_cost:
            print("  [会社資金] 現物買い失敗: 資金が不足しています。")
            return False
        self.record_expense(total_cost, 'stock_purchase')
        portfolio.buy_stock(ticker, company_name, num_shares, price, is_margin=False)
        print(f"  [会社資金] 現物買い: 「{company_name}」を{num_shares:,}株購入しました。")
        return True

    def buy_stock_on_margin(self, portfolio: 'Portfolio', ticker: str, company_name: str, num_shares: int, price: float) -> bool:
        total_cost = num_shares * price
        required_cash = total_cost * constants.INITIAL_MARGIN_REQUIREMENT_RATIO
        if self.get_cash() < required_cash:
            print("  [会社資金] 信用買い失敗: 委託保証金が不足しています。")
            return False
        self.record_expense(required_cash, 'stock_purchase_margin')
        portfolio.buy_stock(ticker, company_name, num_shares, price, is_margin=True)
        print(f"  [会社資金] 信用買い: 「{company_name}」を{num_shares:,}株購入しました。")
        return True

    def sell_stock(self, portfolio: 'Portfolio', ticker: str, num_shares_to_sell: int, price: float) -> bool:
        avg_buy_price = portfolio.sell_stock(ticker, num_shares_to_sell)
        if avg_buy_price is None: return False
        
        proceeds = num_shares_to_sell * price
        profit_loss = (price - avg_buy_price) * num_shares_to_sell
        
        self.deposit(proceeds) # 売却代金を現金に加算
        
        if profit_loss >= 0:
            # 利益分は売上、コスト分は費用から差し引くことで純利益を正しく計上
            cost_of_goods_sold = proceeds - profit_loss
            self.finances['total_sales'] += profit_loss
        else:
            # 損失は費用として計上
            self.finances['total_costs'] += abs(profit_loss)
        return True

    def short_sell_stock(self, portfolio: 'Portfolio', ticker: str, company_name: str, num_shares: int, price: float, game_time: 'GameTime') -> bool:
        proceeds = num_shares * price
        self.deposit(proceeds)
        portfolio.short_sell(ticker, company_name, num_shares, price, game_time)
        return True

    def buy_to_cover_short(self, portfolio: 'Portfolio', ticker: str, num_shares_to_cover: int, price: float) -> bool:
        cost_to_cover = num_shares_to_cover * price
        if self.get_cash() < cost_to_cover:
            print("  [会社資金] 買い戻し失敗: 資金が不足しています。")
            return False
        original_sell_price = portfolio.buy_to_cover(ticker, num_shares_to_cover)
        if original_sell_price is None: return False
        
        profit_loss = (original_sell_price - price) * num_shares_to_cover
        
        self.record_expense(cost_to_cover, 'short_cover')
        if profit_loss > 0:
            self.add_revenue(profit_loss, 'short_cover_gain')
        
        return True

    def invest_in_venture(self, portfolio: 'Portfolio', deal_data: Dict[str, Any], current_total_weeks: int) -> bool:
        """会社資金でベンチャー投資を行う"""
        investment_amount = deal_data["investment_amount_required"]
        if self.get_cash() < investment_amount:
            print("  [会社資金] ベンチャー投資失敗: 資金が不足しています。")
            return False

        self.record_expense(investment_amount, 'venture_investment')
        portfolio.invest_in_venture(deal_data, current_total_weeks)
        print(f"  [会社資金] 「{deal_data['company_name']}」への投資を実行しました。")
        return True
