# models/hr.py
from typing import Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .cxo import CXO

class HumanResources:
    """
    会社の人事(特にCXO)を管理するクラス。
    """
    def __init__(self):
        self.employed_cxos: Dict[str, 'CXO'] = {}

    def hire_cxo(self, candidate: 'CXO') -> bool:
        """
        CXO候補者を雇用し、管理リストに追加する。
        
        Args:
            candidate (CXO): 雇用するCXOオブジェクト。

        Returns:
            bool: 雇用に成功した場合はTrue、失敗した場合はFalse。
        """
        position = candidate.position
        if position in self.employed_cxos:
            print(f"エラー: {position} のポジションは既に埋まっています。")
            return False
        
        self.employed_cxos[position] = candidate
        print(f"  {candidate.name} さんを {candidate.display_position_name} として雇用しました。")
        return True

    def fire_cxo(self, position: str) -> Optional['CXO']:
        """
        指定されたポジションのCXOを解任する。
        
        Args:
            position (str): 解任するCXOの役職キー (例: "CFO")。

        Returns:
            Optional[CXO]: 解任されたCXOオブジェクト。見つからなかった場合はNone。
        """
        if position in self.employed_cxos:
            fired_cxo = self.employed_cxos.pop(position)
            print(f"  {fired_cxo.name} ({fired_cxo.display_position_name}) を解任しました。")
            return fired_cxo
        else:
            print(f"エラー: {position} のポジションにCXOはいません。")
            return None

    def get_total_weekly_salary(self) -> float:
        """
        現在雇用中の全CXOの週次給与の合計を計算する。

        Returns:
            float: 週次給与の合計額。
        """
        if not self.employed_cxos:
            return 0.0
        return sum(cxo.weekly_salary for cxo in self.employed_cxos.values())

    def get_cxo_by_position(self, position: str) -> Optional['CXO']:
        """
        指定されたポジションのCXOオブジェクトを取得する。

        Args:
            position (str): 取得したいCXOの役職キー。

        Returns:
            Optional[CXO]: 該当するCXOオブジェクト。いなければNone。
        """
        return self.employed_cxos.get(position)
