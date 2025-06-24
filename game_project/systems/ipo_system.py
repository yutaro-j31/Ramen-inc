# systems/ipo_system.py
# 省略なしの完全なコードです。

from typing import List

from models.player import Player
from models.game_time import GameTime
from models.listed_company import ListedCompany
import constants
import utils

# ★★★ このファイル固有の入力受付関数は削除しました ★★★


# --- IPOシステム機能 ---
def check_ipo_eligibility(player: Player, game_time: GameTime) -> bool:
    """IPOの適格性をチェックする。"""
    criteria = constants.IPO_ELIGIBILITY_CRITERIA
    print("\n--- IPO適格性チェック ---")
    
    weeks_ok = game_time.total_weeks_elapsed >= criteria['min_weeks_in_operation']
    print(f"  運営期間: {game_time.total_weeks_elapsed}週 / {criteria['min_weeks_in_operation']}週 ... {'OK' if weeks_ok else 'NG'}")

    revenue, profit = player.finance.get_estimated_annuals(game_time)
    
    revenue_ok = revenue >= criteria['min_annual_revenue_estimate']
    print(f"  推定年間売上: ¥{revenue:,.0f} / ¥{criteria['min_annual_revenue_estimate']:,.0f} ... {'OK' if revenue_ok else 'NG'}")

    profit_ok = player.finance.get_net_profit() >= criteria['min_cumulative_profit']
    print(f"  累積純利益: ¥{player.finance.get_net_profit():,.0f} / ¥{criteria['min_cumulative_profit']:,.0f} ... {'OK' if profit_ok else 'NG'}")

    depts_ok = True
    for dept in criteria['required_departments']:
        if not player.departments.get(dept):
            depts_ok = False
            print(f"  必須部門 ({dept.upper()}): 未設置 ... NG")
    if depts_ok:
        print(f"  必須部門: 設置済み ... OK")

    return all([weeks_ok, revenue_ok, profit_ok, depts_ok])

def start_ipo_process(player: Player, game_time: GameTime):
    """IPO準備プロセスを開始する。"""
    if player.is_company_public:
        print("あなたの会社は既に上場しています。")
        return
    
    if player.ipo.is_in_preparation:
        print(f"現在、IPO準備中です。完了まで残り {player.ipo.preparation_weeks_remaining} 週です。")
        return

    if not check_ipo_eligibility(player, game_time):
        print("IPOの基準を満たしていません。")
        return
        
    print("\n--- IPO準備開始 ---")
    print("IPOにより、市場から大規模な資金調達が可能になりますが、多額の費用と時間がかかります。")
    
    psr_multiplier = random.uniform(constants.IPO_VALUATION_PSR_RANGE[0], constants.IPO_VALUATION_PSR_RANGE[1])
    per_multiplier = random.uniform(constants.IPO_VALUATION_PER_RANGE[0], constants.IPO_VALUATION_PER_RANGE[1])
    
    rev, prof = player.finance.get_estimated_annuals(game_time)
    valuation_by_sales = rev * psr_multiplier
    valuation_by_profit = prof * per_multiplier
    
    estimated_valuation = (valuation_by_sales + valuation_by_profit) / 2
    
    print(f"あなたの会社の推定企業価値: ¥{estimated_valuation:,.0f}")
    
    target_price = utils.get_integer_input("目標公募価格(1株あたり)を入力してください: ", 100, 10000)
    if target_price is None: return
    
    offer_percentage = utils.get_integer_input("売出株式の割合(%)を入力してください (15-30): ", 15, 30)
    if offer_percentage is None: return
    
    print("\n--- IPO準備内容の確認 ---")
    print(f"  目標公募価格: ¥{target_price:,.0f}")
    print(f"  売出株式割合: {offer_percentage}%")
    print(f"  引受手数料(前払い): ¥{constants.IPO_UNDERWRITER_FEE_FIXED:,.0f}")
    
    confirm = input("この内容でIPO準備を開始しますか? (y/n): ").lower()
    if confirm == 'y':
        player.ipo.start_preparation(player, target_price, float(offer_percentage) / 100.0, game_time)
    else:
        print("IPO準備をキャンセルしました。")


def show_ipo_status(player: Player, game_time: GameTime):
    """現在のIPOの状況を表示する。"""
    print("\n--- IPOステータス ---")
    if not player.ipo.is_in_preparation:
        print("  現在、IPO準備中ではありません。")
        return
        
    print("  IPO準備中です。")
    print(f"  上場までの残り期間: {player.ipo.preparation_weeks_remaining}週")
    print(f"  ロードショー(投資家説明会)開始まで: {max(0, player.ipo.preparation_weeks_remaining - player.ipo.roadshow_weeks_remaining)}週")
    if player.ipo.current_investor_demand_score is not None:
        print(f"  現在の投資家需要スコア: {player.ipo.current_investor_demand_score:.1f}")

def show_ipo_menu(player: Player, game_time: GameTime):
    """IPOシステムのメインメニュー"""
    while True:
        print("\n--- 自社IPO(株式公開)---")
        if player.is_company_public:
            print(f"あなたの会社「{player.company_name}」は上場企業です。")
            print(f"ティッカーシンボル: {player.ipo.company_ticker_symbol}")
            break

        show_ipo_status(player, game_time)
        
        print("\n  1: IPO準備を開始する")
        print("  0: メインメニューに戻る")

        choice = utils.get_integer_input("選択: ", 0, 1) # ★utilsの関数に変更
        if choice is None or choice == 0: break
        
        if choice == 1:
            start_ipo_process(player, game_time)
