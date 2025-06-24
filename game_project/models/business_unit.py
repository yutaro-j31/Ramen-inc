# models/business_unit.py
import random
from typing import List, Dict, Optional
import collections
import math # 追記

from .menu_item import MenuItem
from .staff import Staff
from .player import Player
from constants import map_master_data, ATTRACTIVENESS_WEIGHTS, ATTRACTIVENESS_BASE_EQUIPMENT_SCORE, ATTRACTIVENESS_BASE_MENU_ITEM_SCORE, ATTRACTIVENESS_STAFF_EFFICIENCY_FACTOR, ATTRACTIVENESS_RND_QUALITY_FACTOR, EQUIPMENT_UPGRADE_COST_BASE, EQUIPMENT_UPGRADE_COST_FACTOR, AVG_SPEND_PER_CUSTOMER_RAMEN_SHOP

class BusinessUnit:
    """
    ラーメン店などの個別の事業ユニットを表すクラス。
    """
    # !!! 変更点: コンストラクタの引数を修正 !!!
    def __init__(self, name: str, business_type: str, location_name: str, 
                 base_weekly_fixed_costs: float, location_sales_modifier: float, 
                 base_weekly_customer_pool: int, initial_equipment_level: int = 1):
        self.name: str = name
        self.business_type: str = business_type
        self.location_name: str = location_name
        self.location_sales_modifier: float = location_sales_modifier
        self.base_weekly_customer_pool = base_weekly_customer_pool # 引数から直接受け取るように変更

        self.finances: collections.defaultdict[str, float] = collections.defaultdict(float)
        self.finances['weekly_fixed_costs'] = base_weekly_fixed_costs

        self.equipment_level: int = initial_equipment_level
        self.menu: List[MenuItem] = []
        self.staff_list: List[Staff] = []
        
        self.attractiveness: float = 0.0
        self.weekly_customers: int = 0
        self.update_attractiveness()

    def get_next_upgrade_cost(self) -> int:
        base = EQUIPMENT_UPGRADE_COST_BASE.get(self.business_type, 500000)
        factor = EQUIPMENT_UPGRADE_COST_FACTOR.get(self.business_type, 1000000)
        # 変更点: コストの増加をより急にする(例)
        cost = base + (factor * (self.equipment_level ** 1.5))
        return int(cost)

    def upgrade_equipment(self):
        self.equipment_level += 1
        self.update_attractiveness()

    def add_menu_item(self, item: MenuItem):
        self.menu.append(item)
        self.update_attractiveness()

    def remove_menu_item(self, index: int) -> Optional[MenuItem]:
        if 0 <= index < len(self.menu):
            removed_item = self.menu.pop(index)
            self.update_attractiveness()
            return removed_item
        return None

    def hire_staff(self, staff: Staff):
        self.staff_list.append(staff)
        self.update_attractiveness()

    def fire_staff(self, index: int) -> Optional[Staff]:
        if 0 <= index < len(self.staff_list):
            fired_staff = self.staff_list.pop(index)
            self.update_attractiveness()
            return fired_staff
        return None

    def calculate_staff_efficiency(self) -> float:
        if not self.staff_list:
            return 0.8
        
        total_efficiency = sum(s.efficiency_modifier for s in self.staff_list)
        return total_efficiency / len(self.staff_list)

    def update_attractiveness(self, rnd_quality_bonus: float = 0.0):
        weights = ATTRACTIVENESS_WEIGHTS
        
        # 収穫逓減を考慮したスコア計算
        equipment_score = math.sqrt(self.equipment_level) * ATTRACTIVENESS_BASE_EQUIPMENT_SCORE
        menu_score = math.sqrt(len(self.menu)) * ATTRACTIVENESS_BASE_MENU_ITEM_SCORE
        staff_score = self.calculate_staff_efficiency() * ATTRACTIVENESS_STAFF_EFFICIENCY_FACTOR
        rnd_score = rnd_quality_bonus * ATTRACTIVENESS_RND_QUALITY_FACTOR
        
        self.attractiveness = (equipment_score * weights['equipment'] +
                               menu_score * weights['menu_variety'] +
                               staff_score * weights['staff_efficiency'] +
                               rnd_score * weights['rnd_quality'])
        
    def prepare_for_weekly_competition(self, player: Optional[Player]):
        quality_bonus = 0.0
        if player and player.effects:
            quality_bonus = player.effects.get_total_rnd_bonus("ramen_shop_quality_boost")
        self.update_attractiveness(rnd_quality_bonus=quality_bonus)

    def finalize_weekly_finances(self, player: Optional[Player]):
        avg_spend = AVG_SPEND_PER_CUSTOMER_RAMEN_SHOP
        sales = self.weekly_customers * avg_spend
        self.finances['weekly_sales'] = sales
        self.finances['cumulative_sales'] += sales
        
        total_cost_ratio = sum(item.cost / item.price for item in self.menu) / len(self.menu) if self.menu else 0.3
        
        cost_reduction_bonus = 0.0
        if player and player.effects:
            cost_reduction_bonus = player.effects.get_total_rnd_bonus("ramen_shop_cost_reduction")
        actual_cost_ratio = total_cost_ratio * (1 - cost_reduction_bonus)
        
        variable_costs = sales * actual_cost_ratio
        self.finances['weekly_variable_costs'] = variable_costs
        self.finances['cumulative_variable_costs'] += variable_costs

        staff_salaries = sum(s.weekly_salary for s in self.staff_list)
        self.finances['weekly_staff_salaries'] = staff_salaries
        self.finances['cumulative_staff_salaries'] += staff_salaries

        fixed_costs = self.finances['weekly_fixed_costs']
        fixed_cost_reduction_bonus = 0.0
        if player and player.effects:
            fixed_cost_reduction_bonus = player.effects.get_total_rnd_bonus("ramen_shop_fixed_cost_reduction_percent")
        actual_fixed_costs = fixed_costs * (1 - fixed_cost_reduction_bonus)
        
        self.finances['weekly_total_costs'] = actual_fixed_costs + staff_salaries + variable_costs
        self.finances['cumulative_fixed_costs'] += actual_fixed_costs
        
        profit = sales - self.finances['weekly_total_costs']
        self.finances['weekly_profit'] = profit
        self.finances['cumulative_profit'] += profit

    def display_menu(self):
        if not self.menu:
            print("  メニューにはまだ何もありません。")
            return
        for i, item in enumerate(self.menu):
            print(f"  {i+1}. {item.name} (価格: ¥{item.price:,}, 原価: ¥{item.cost:,})")

    def display_staff(self):
        if not self.staff_list:
            print("  この店舗にはスタッフがいません。")
            return
        for i, staff in enumerate(self.staff_list):
            print(f"  {i+1}. {staff.name} ({staff.role}) - 週給: ¥{staff.weekly_salary:,}")
