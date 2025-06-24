# models/staff.py

class Staff:
    """
    従業員を表すクラス。
    名前、役割、週給、効率補正値を持つ。
    """
    def __init__(self, name: str, role: str, weekly_salary: float, efficiency_modifier: float = 1.0):
        self.name: str = name
        self.role: str = role # 例: "キッチン", "ホール", "店長候補"
        self.weekly_salary: float = weekly_salary
        self.efficiency_modifier: float = efficiency_modifier # 1.0が標準。1.1なら10%効率が良いなど。

    def __str__(self) -> str:
        return (f"{self.name} ({self.role}) - 週給: ¥{self.weekly_salary:,.0f}, "
                f"効率: {self.efficiency_modifier*100:.0f}%")

    def __repr__(self) -> str:
        return (f"Staff(name='{self.name}', role='{self.role}', "
                f"weekly_salary={self.weekly_salary}, efficiency_modifier={self.efficiency_modifier})")

