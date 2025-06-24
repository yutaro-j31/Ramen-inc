# models/cxo.py
import uuid
from typing import List, Dict, Any

class CXO:
    """経営幹部(CFO, CMO, CTO, COOなど)を表すクラス"""
    def __init__(self, name: str, position: str, # 例: "CFO", "CMO"
                 skill_level: str, # 例: "S", "A", "B", "C"
                 weekly_salary: float,
                 effects: List[Dict[str, Any]]): # constants.CXO_TYPES の "effects" リスト
        
        self.cxo_id: str = str(uuid.uuid4())[:8] # 短いユニークID
        self.name: str = name
        self.position: str = position # 役職名 (CFO, CMOなど)
        self.display_position_name: str = "" # 表示用の役職名(例:最高財務責任者)
        self.skill_level: str = skill_level # S, A, B, C
        self.weekly_salary: float = weekly_salary
        
        # CXOがもたらす具体的な効果 (constantsからコピー)
        # 例: [{"type": "loan_interest_reduction", "value_percent_reduction": 0.1, "skill_level_needed": "A"}, ...]
        self.effects: List[Dict[str, Any]] = effects
        
        # プレイヤーの会社に雇用されているか
        self.is_hired: bool = False
        self.hired_by_company_name: Optional[str] = None # どの会社に雇われているか(将来の競合引き抜き用)

    def get_effect_value(self, effect_type: str) -> Any:
        """指定されたタイプの効果の値を取得する。該当効果がなければNoneを返す。"""
        for effect in self.effects:
            if effect.get("type") == effect_type:
                # このCXOのスキルレベルが効果発動に必要なスキルレベルを満たしているか確認
                required_skill = effect.get("skill_level_needed")
                if required_skill:
                    # スキルレベルは S > A > B > C の順と仮定
                    skill_order = {"C": 0, "B": 1, "A": 2, "S": 3}
                    if skill_order.get(self.skill_level, -1) >= skill_order.get(required_skill, -1):
                        return effect.get("value")
                else: # スキルレベル不要な効果ならそのまま返す
                    return effect.get("value")
        return None # 効果なし、またはスキルレベル不足

    def __str__(self) -> str:
        title = self.display_position_name if self.display_position_name else self.position
        return (f"{self.name} ({title} - {self.skill_level}ランク)\n"
                f"  週給: ¥{self.weekly_salary:,.0f}")

    def get_detailed_description(self) -> str:
        """CXOの詳細な説明(効果含む)を返す"""
        title = self.display_position_name if self.display_position_name else self.position
        desc_lines = [
            f"{self.name} ({title} - {self.skill_level}ランク)",
            f"  週給: ¥{self.weekly_salary:,.0f}",
            f"  主な役割・効果:"
        ]
        if self.effects:
            for effect in self.effects:
                # スキルレベルが足りている効果のみ表示するなども検討可能
                # effect_value = self.get_effect_value(effect.get("type","")) # これだと循環呼び出しの可能性
                # ここでは単純に定義されている効果をリストアップ
                desc_lines.append(f"    - {effect.get('description', effect.get('type'))}: {effect.get('value')}")
        else:
            desc_lines.append("    - (具体的な効果は未設定)")
        return "\n".join(desc_lines)
