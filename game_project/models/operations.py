# models/operations.py (完全版)
from typing import List, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .business_unit import BusinessUnit
    from .player import Player
    from .corporate_finance import CorporateFinance
    from .property import Property

import constants

class Operations:
    """
    会社の事業運営(店舗、本部、部門、会社所有不動産)を管理するクラス。
    """
    def __init__(self):
        self.businesses_owned: List['BusinessUnit'] = []
        self.company_properties: List['Property'] = []
        self.headquarters_type: str = "なし"
        self.hq_weekly_rent: float = 0.0
        self.departments: Dict[str, bool] = {
            "investment": False, 
            "hr": False, 
            "rnd": False, 
            "marketing": False
        }

    def add_business(self, business: 'BusinessUnit'):
        self.businesses_owned.append(business)

    def get_weekly_financials(self) -> tuple[float, float]:
        if not self.businesses_owned:
            return 0.0, 0.0
        
        total_sales = sum(b.finances.get('weekly_sales', 0.0) for b in self.businesses_owned)
        total_costs = sum(b.finances.get('weekly_total_costs', 0.0) for b in self.businesses_owned)
        return total_sales, total_costs

    def get_total_weekly_variable_costs(self) -> float:
        if not self.businesses_owned:
            return 0.0
        return sum(b.finances.get('weekly_variable_costs', 0.0) for b in self.businesses_owned)

    def prepare_all_for_competition(self, player: 'Player'):
        for business in self.businesses_owned:
            business.prepare_for_weekly_competition(player)
            
    def finalize_all_finances(self, player: 'Player'):
        for business in self.businesses_owned:
            business.finalize_weekly_finances(player)

    def upgrade_shop_equipment(self, shop: 'BusinessUnit', finance: 'CorporateFinance') -> bool:
        """指定された店舗の設備をアップグレードする。"""
        if shop.equipment_level >= constants.MAX_EQUIPMENT_LEVEL.get(shop.business_type, 5):
            return False

        upgrade_cost = shop.get_next_upgrade_cost()
        if finance.get_cash() >= upgrade_cost:
            # finance.finances['cash'] -= upgrade_cost # record_expenseで処理するため不要
            finance.record_expense(upgrade_cost, 'equipment_upgrade')
            shop.upgrade_equipment()
            return True
        else:
            return False

    def buy_company_property(self, property_to_buy: 'Property', finance: 'CorporateFinance') -> bool:
        if finance.get_cash() >= property_to_buy.purchase_price:
            finance.record_expense(property_to_buy.purchase_price, 'property_purchase')
            self.company_properties.append(property_to_buy)
            print(f"  [会社資金] 不動産 「{property_to_buy.name}」を購入しました。")
            return True
        else:
            print(f"  不動産購入失敗: 会社の現金が不足しています。")
            return False

    def sell_company_property(self, property_to_sell: 'Property', finance: 'CorporateFinance') -> bool:
        if property_to_sell in self.company_properties:
            proceeds = property_to_sell.current_value
            self.company_properties.remove(property_to_sell)
            
            # 売却益は収益、売却損は費用として計上
            profit_loss = proceeds - property_to_sell.purchase_price
            if profit_loss >= 0: 
                finance.add_revenue(proceeds, 'property_sale') # 売却額をそのまま収入として計上
                finance.record_expense(property_to_sell.purchase_price, 'property_cost_of_goods_sold') # 簿価を費用として計上
            else: 
                finance.add_revenue(proceeds, 'property_sale')
                finance.record_expense(abs(profit_loss), 'property_sale_loss')
            
            print(f"  会社所有の不動産 「{property_to_sell.name}」を売却しました。")
            return True
        else:
            print(f"  不動産売却失敗: 会社はその不動産を所有していません。")
            return False
            
    def establish_hq_rented(self, finance: 'CorporateFinance', initial_cost: float, weekly_rent: float) -> bool:
        if self.headquarters_type != "なし":
            print(f"  既に本部({self.headquarters_type})があります。")
            return False
        if finance.get_cash() >= initial_cost:
            finance.record_expense(initial_cost, 'hq_setup')
            self.headquarters_type = "賃貸オフィス"
            self.hq_weekly_rent = weekly_rent
            print(f"  賃貸オフィスで本部を設立しました! (初期費用: ¥{initial_cost:,.0f}, 週次賃料: ¥{weekly_rent:,.0f})")
            return True
        else:
            print(f"  本部設立失敗: 会社の資金が不足しています。")
            return False

    def establish_hq_owned(self, finance: 'CorporateFinance', construction_cost: float) -> bool:
        if self.headquarters_type != "なし":
            print(f"  既に本部({self.headquarters_type})があります。")
            return False
        if finance.get_cash() >= construction_cost:
            finance.record_expense(construction_cost, 'hq_setup')
            self.headquarters_type = "自社ビル"
            self.hq_weekly_rent = 0 
            print(f"  自社ビルを建設し、本部を設立しました! (建設費用: ¥{construction_cost:,.0f})")
            return True
        else:
            print(f"  自社ビル建設失敗: 会社の資金が不足しています。")
            return False

    def establish_department(self, finance: 'CorporateFinance', department_name: str, setup_cost: float) -> bool:
        if self.headquarters_type == "なし":
            print("  部門を設置するには、まず本部を設立してください。")
            return False
        if department_name not in self.departments:
            print(f"  無効な部門名です: {department_name}")
            return False
        if self.departments.get(department_name, False):
            print(f"  {department_name.upper()}部門は既に存在します。")
            return False
        if finance.get_cash() >= setup_cost:
            finance.record_expense(setup_cost, 'department_setup')
            self.departments[department_name] = True
            print(f"  {department_name.upper()}部門を新設しました。(設置費用: ¥{setup_cost:,.0f})")
            return True
        else:
            print(f"  {department_name.upper()}部門の新設失敗。会社の資金が不足しています。(必要費用: ¥{setup_cost:,.0f})")
            return False
