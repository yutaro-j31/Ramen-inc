# models/corporate_development.py
# 省略なしの完全なコードです。

import random
from typing import List, Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .player import Player
    from .game_time import GameTime
    from .listed_company import ListedCompany
    from .target_company import TargetCompany
    from .business_unit import BusinessUnit
    from .menu_item import MenuItem
    from .staff import Staff

import constants

class CorporateDevelopment:
    """
    M&Aによる企業買収、子会社管理、PMI(買収後統合)などを担当するクラス。
    """
    def __init__(self):
        self.subsidiaries: List['ListedCompany'] = []
        self.acquired_companies_log: List[Dict[str, Any]] = []

    def add_subsidiary(self, company: 'ListedCompany', acquisition_cost: float, game_time: 'GameTime', acquisition_type: str):
        """
        買収した企業を子会社としてリストに追加する。
        """
        company.is_subsidiary = True
        company.market_cap_at_acquisition = company.market_cap
        self.subsidiaries.append(company)
        
        self.acquired_companies_log.append({
            "name": company.company_name, 
            "ticker": company.ticker_symbol,
            "sector": company.sector,
            "acquisition_cost": acquisition_cost,
            "acquired_week": game_time.total_weeks_elapsed,
            "type": acquisition_type
        })
        print(f"  {company.company_name} は {game_time.get_date_string()} 付で子会社となりました。")

    def integrate_acquired_private_company(self, acquired_company: 'TargetCompany', game_time: 'GameTime') -> Dict[str, Any]:
        """
        買収した非上場企業を統合し、その結果(新規事業、シナジーなど)を返す。
        """
        from .business_unit import BusinessUnit
        from .menu_item import MenuItem
        from .staff import Staff

        print(f"\n--- {acquired_company.name} の統合処理を開始 ---")
        integration_results = {
            "new_businesses": [],
            "new_synergy": None,
            "one_time_gain": 0.0
        }

        if acquired_company.industry == "地域密着型ラーメンチェーン":
            num_new_shops = 0
            avg_staff_per_shop_divisor = (1.0/constants.ACQUIRED_RAMEN_CHAIN_SHOPS_PER_EMPLOYEE_RANGE[0] + 1.0/constants.ACQUIRED_RAMEN_CHAIN_SHOPS_PER_EMPLOYEE_RANGE[1]) / 2.0
            if acquired_company.employee_count > 0 and avg_staff_per_shop_divisor > 0:
                shops_by_emp = acquired_company.employee_count / avg_staff_per_shop_divisor
                num_new_shops = max(num_new_shops, int(round(shops_by_emp)))
            avg_rev_per_shop = (constants.ACQUIRED_RAMEN_CHAIN_SHOPS_PER_REVENUE_RANGE[0] + constants.ACQUIRED_RAMEN_CHAIN_SHOPS_PER_REVENUE_RANGE[1])/2.0
            if acquired_company.estimated_annual_revenue > 0 and avg_rev_per_shop > 0 :
                shops_by_rev = acquired_company.estimated_annual_revenue / avg_rev_per_shop
                num_new_shops = max(num_new_shops, int(round(shops_by_rev)))
            
            num_new_shops = max(1, min(constants.ACQUIRED_RAMEN_CHAIN_MAX_NEW_SHOPS, num_new_shops))
            print(f"  {acquired_company.name} を買収し、新たに {num_new_shops} 店舗のラーメン店を系列に加えます。")
            
            for i in range(num_new_shops):
                new_loc_data = random.choice(constants.LOCATIONS_DATA)
                shop_name = f"{acquired_company.name[:5]} {new_loc_data['name']}店"
                initial_equip_level = constants.DEFAULT_EQUIPMENT_LEVEL + random.randint(0,1)
                new_bu = BusinessUnit(name=shop_name, business_type=constants.DEFAULT_RAMEN_SHOP_TYPE_NAME, base_weekly_fixed_costs=float(new_loc_data['rent_base']) * random.uniform(0.9, 1.1), location_name=new_loc_data['name'], location_sales_modifier=float(new_loc_data['sales_modifier']), initial_equipment_level=initial_equip_level)
                
                # ここではメニューやスタッフの追加は行わず、BusinessUnitオブジェクトのリストを返す
                integration_results["new_businesses"].append(new_bu)
                print(f"    新店舗「{shop_name}」の準備が整いました。")

        elif acquired_company.industry in constants.ACQUISITION_SYNERGY_EFFECTS:
            synergy_id = acquired_company.company_id 
            effect_data = constants.ACQUISITION_SYNERGY_EFFECTS[acquired_company.industry]
            integration_results["new_synergy"] = {
                "id": synergy_id,
                "data": {
                    "name": f"{acquired_company.name}買収によるシナジー",
                    "type": effect_data["effect_type"],
                    "value": effect_data["value"],
                    "remaining_weeks": effect_data["duration_weeks"],
                    "description": effect_data.get("description", "") 
                }
            }
            print(f"  {acquired_company.name} を買収し、「{effect_data.get('description', effect_data['type'])}」のシナジー効果が発生します。")
        else: 
            one_time_asset_gain = acquired_company.get_estimated_net_profit() * random.uniform(0.5, 1.5) 
            integration_results["one_time_gain"] = one_time_asset_gain
            print(f"  {acquired_company.name} を買収し、一時的な経営資源として ¥{one_time_asset_gain:,.0f} を獲得しました。")

        print(f"--- {acquired_company.name} の統合処理完了 ---")
        return integration_results

    def get_total_weekly_subsidiary_profit(self) -> float:
        """全ての子会社の週次利益の合計を計算して返す。"""
        if not self.subsidiaries:
            return 0.0
        return sum(sub.get_weekly_profit_as_subsidiary() for sub in self.subsidiaries)
