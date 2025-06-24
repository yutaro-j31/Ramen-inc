# models/ipo_manager.py
# 省略なしの完全なコードです。

from typing import Optional, TYPE_CHECKING, List

if TYPE_CHECKING:
    from .player import Player
    from .game_time import GameTime
    from .listed_company import ListedCompany

import constants

class IPOManager:
    """
    会社の株式公開(IPO)プロセスを管理するクラス。
    """
    def __init__(self):
        self.is_company_public: bool = False # ★★★ この属性を追加 ★★★
        self.company_ticker_symbol: Optional[str] = None # ★★★ この属性を追加 ★★★
        
        self.is_in_preparation: bool = False
        self.preparation_weeks_remaining: int = 0
        self.roadshow_weeks_remaining: int = 0
        self.underwriter_fee_paid: bool = False
        self.target_ipo_price: Optional[float] = None
        self.target_ipo_offer_percentage: Optional[float] = None
        self.current_investor_demand_score: Optional[float] = None
        self.final_offering_price: Optional[float] = None
        self.final_shares_offered_percentage: Optional[float] = None

    def start_preparation(self, player: 'Player', target_price: float, offer_percentage: float, game_time: 'GameTime') -> bool:
        """IPO準備を開始する。"""
        eligibility = constants.IPO_ELIGIBILITY_CRITERIA
        
        # is_company_public のチェックをここに追加
        if self.is_company_public:
            print("エラー: 会社は既に上場しています。")
            return False

        if player.finance.get_estimated_annuals(game_time)[0] < eligibility['min_annual_revenue_estimate']:
            print("IPO準備失敗: 推定年間売上が基準に達していません。")
            return False
        if player.finance.get_net_profit() < eligibility['min_cumulative_profit']:
            print("IPO準備失敗: 累積純利益が基準に達していません。")
            return False
        for dept in eligibility['required_departments']:
            if not player.departments.get(dept):
                print(f"IPO準備失敗: {dept.upper()}部門が設置されていません。")
                return False
        
        fee = constants.IPO_UNDERWRITER_FEE_FIXED
        if player.finance.get_cash() < fee:
            print(f"IPO準備失敗: 引受手数料(¥{fee:,.0f})を支払う資金がありません。")
            return False

        player.finance.finances['cash'] -= fee
        player.finance.finances['total_costs'] += fee
        
        self.is_in_preparation = True
        self.preparation_weeks_remaining = constants.IPO_PROCESS_WEEKS
        self.roadshow_weeks_remaining = constants.IPO_ROADSHOW_WEEKS
        self.underwriter_fee_paid = True
        self.target_ipo_price = target_price
        self.target_ipo_offer_percentage = offer_percentage
        self.current_investor_demand_score = float(constants.IPO_INVESTOR_DEMAND_BASE_LEVEL)
        
        print(f"IPOの準備を開始しました。引受手数料 ¥{fee:,.0f} を支払いました。")
        print(f"上場までの準備期間は {self.preparation_weeks_remaining}週です。")
        return True

    def process_ipo_events(self, player: 'Player', game_time: 'GameTime', market_list: List['ListedCompany']):
        """IPOプロセスの週次更新を行う。"""
        if not self.is_in_preparation:
            return

        self.preparation_weeks_remaining -= 1
        
        # (投資家需要の変動ロジックはここに記述)

        if self.preparation_weeks_remaining <= 0:
            self.finalize_ipo(player, market_list, game_time)

    def finalize_ipo(self, player: 'Player', market_list: List['ListedCompany'], game_time: 'GameTime'):
        """IPOプロセスの最終処理を行う。"""
        print("\n--- IPO公開日 ---")
        
        # (需要に応じた価格・株数調整ロジック)
        
        if self.current_investor_demand_score < constants.IPO_FAILURE_DEMAND_THRESHOLD:
            print("投資家の需要が想定を大幅に下回り、IPOは失敗しました...")
        else:
            print("IPO成功!あなたの会社は株式市場に上場しました。")
            self.is_company_public = True
            # ティッカーシンボルを決定
            # ... (ティッカーシンボル生成ロジック)
            # self.company_ticker_symbol = new_ticker
            
            # (資金調達などの処理)
            pass

        # IPOプロセスをリセット
        self.is_in_preparation = False
        self.preparation_weeks_remaining = 0
        self.underwriter_fee_paid = False
