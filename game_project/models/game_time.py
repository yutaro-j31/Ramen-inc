# models/game_time.py
# 省略なしの完全なコードです。

import random

class GameTime:
    """
    ゲーム内の時間を管理するクラス。
    """
    WEEKS_PER_MONTH = 4
    MONTHS_PER_YEAR = 12
    WEEKS_PER_YEAR = WEEKS_PER_MONTH * MONTHS_PER_YEAR
    MONTHS_PER_QUARTER = 3
    
    def __init__(self, start_year: int, start_month: int, start_week: int):
        self.current_year: int = start_year
        self.current_month: int = start_month
        self.current_week: int = start_week # 月の中の週 (1-4)
        self.total_weeks_elapsed: int = 0
        self.current_economic_phase: str = "普通"
        self.weeks_in_current_phase: int = 0
        self._set_initial_phase()

    def _set_initial_phase(self):
        """経済フェーズを初期化する。"""
        self.current_economic_phase = "普通"
        self.weeks_in_current_phase = 0

    def advance_week(self):
        """時間を1週間進める。"""
        self.total_weeks_elapsed += 1
        self.current_week += 1
        if self.current_week > self.WEEKS_PER_MONTH:
            self.current_week = 1
            self.current_month += 1
            if self.current_month > self.MONTHS_PER_YEAR:
                self.current_month = 1
                self.current_year += 1
        
        self._update_economic_phase()

    def _update_economic_phase(self):
        """経済フェーズを確率的に更新する。"""
        self.weeks_in_current_phase += 1
        # 平均して半年から2年程度でフェーズが変わるように調整
        if self.weeks_in_current_phase > 24 and random.random() < 1/48.0:
            phases = ["好景気", "普通", "不景気"]
            weights = [0.3, 0.4, 0.3] 
            
            new_phase = random.choices(phases, weights=weights, k=1)[0]
            if new_phase != self.current_economic_phase:
                self.current_economic_phase = new_phase
                self.weeks_in_current_phase = 0
                print(f"\n[経済ニュース] 経済は「{self.current_economic_phase}」に移行しました。")

    def get_date_string(self) -> str:
        """現在の日付を文字列として返す。"""
        return f"{self.current_year}年{self.current_month}月{self.current_week}週"

    def get_current_economic_phase_impact_per_week(self) -> float:
        """現在の経済状況が週次の変動に与える影響係数を返す。"""
        if self.current_economic_phase == "好景気":
            return 0.002
        elif self.current_economic_phase == "不景気":
            return -0.002
        else: # 普通
            return 0.0

    def is_quarter_end(self) -> bool:
        """現在が四半期末(3,6,9,12月の最終週)かどうかを判定する。"""
        is_quarter_month = self.current_month % self.MONTHS_PER_QUARTER == 0
        is_last_week_of_month = self.current_week == self.WEEKS_PER_MONTH
        return is_quarter_month and is_last_week_of_month
