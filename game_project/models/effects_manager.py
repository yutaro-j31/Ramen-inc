# models/effects_manager.py
# 省略なしの完全なコードです。

from typing import List, Dict, Any

class EffectsManager:
    """
    R&DボーナスやM&Aシナジーなど、会社に発生する様々な「効果」を管理するクラス。
    """
    def __init__(self):
        self.completed_rnd_projects: List[str] = []
        self.active_rnd_bonuses: Dict[str, Dict[str, Any]] = {}
        self.active_synergies: Dict[str, Dict[str, Any]] = {}

    def add_completed_rnd_project(self, project_id: str, bonus_effects_data: List[Dict[str, Any]]):
        """完了したR&Dプロジェクトを追加し、ボーナス効果を有効化する。"""
        if project_id not in self.completed_rnd_projects:
            self.completed_rnd_projects.append(project_id)
            for effect_data in bonus_effects_data:
                # 効果IDはプロジェクトIDと効果タイプで一意にする
                effect_id = f"{project_id}_{effect_data['type']}"
                self.active_rnd_bonuses[effect_id] = effect_data.copy()
                print(f"  [R&D] 新しい効果が有効になりました: {effect_data.get('description', effect_id)}")

    def add_synergy(self, synergy_id: str, effect_data: Dict[str, Any]):
        """新しいM&Aシナジー効果を追加する。"""
        if synergy_id not in self.active_synergies:
            self.active_synergies[synergy_id] = effect_data.copy()
            print(f"  [M&A] 新しいシナジーが発揮されます: {effect_data.get('description', synergy_id)}")

    def get_total_rnd_bonus(self, bonus_effect_type_key: str) -> float:
        """指定されたタイプの有効なR&Dボーナスの合計値を取得する。"""
        total_bonus_value = 0.0
        for _bonus_id, bonus_data in self.active_rnd_bonuses.items():
            if bonus_data.get("type") == bonus_effect_type_key:
                total_bonus_value += bonus_data.get("value", 0.0)
        return total_bonus_value
        
    def process_weekly_updates(self, company_finances: Dict[str, float], total_variable_costs: float):
        """週次で全ての効果を処理し、期限切れのものを削除する。"""
        
        # M&Aシナジー効果の適用と更新
        if self.active_synergies:
            synergies_to_remove = []
            total_material_cost_reduction = 0.0
            total_fixed_cost_reduction = 0.0

            for synergy_id, effect in list(self.active_synergies.items()):
                if effect["remaining_weeks"] <= 0:
                    synergies_to_remove.append(synergy_id)
                    print(f"  シナジー効果「{effect['name']}」が終了しました。")
                    continue
                
                if effect["type"] == "material_cost_reduction":
                    reduction = total_variable_costs * effect["value"]
                    total_material_cost_reduction += reduction
                elif effect["type"] == "fixed_cost_reduction_total":
                    reduction = effect.get("value_weekly_amount", 0.0)
                    total_fixed_cost_reduction += reduction
                
                effect["remaining_weeks"] -= 1

            if total_material_cost_reduction > 0:
                company_finances['cash'] += total_material_cost_reduction
                company_finances['total_costs'] -= total_material_cost_reduction
            if total_fixed_cost_reduction > 0:
                company_finances['cash'] += total_fixed_cost_reduction
                company_finances['total_costs'] -= total_fixed_cost_reduction

            for sid in synergies_to_remove:
                if sid in self.active_synergies:
                    del self.active_synergies[sid]

        # R&Dボーナス効果の期間更新
        if self.active_rnd_bonuses:
            rnd_bonuses_to_remove = []
            for bonus_id, effect_data in list(self.active_rnd_bonuses.items()):
                if not effect_data.get("is_permanent", False): 
                    if "remaining_weeks" in effect_data:
                        effect_data["remaining_weeks"] -= 1
                        if effect_data.get("remaining_weeks", 0) <= 0: 
                            rnd_bonuses_to_remove.append(bonus_id)
                            print(f"  R&Dボーナス「{effect_data['name']}」が終了しました。")
            
            for bid in rnd_bonuses_to_remove:
                if bid in self.active_rnd_bonuses:
                    del self.active_rnd_bonuses[bid]
