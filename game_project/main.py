# main.py
import sys
import os
import traceback
from typing import Optional, List, Dict, Any

# プロジェクトのルートパスをPythonの検索パスに追加
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)

from models.player import Player
from models.game_time import GameTime
import constants
import utils
from systems import (
    shop_system, banking_system, real_estate_system, company_system, 
    venture_system, stock_market_system, general_stock_market_system, 
    acquisition_system, ipo_system, rnd_system, personal_finance_system, 
    competitor_ai_system, hr_system, reporting_system, save_load_system,
    map_system
)

# --- グローバル変数 ---
player: Optional[Player] = None
game_time: Optional[GameTime] = None

# --- ヘルパー関数 ---
def display_quick_status():
    """現在の簡易ステータスを表示する"""
    if player and game_time:
        print("\n" + "="*50)
        print(f"現在時刻: {game_time.get_date_string()}")
        print(reporting_system.get_status_summary(player, general_stock_market_system.listed_companies_on_market))
        print("="*50)

def show_financial_report():
    """会社の財務レポートを表示する"""
    if player:
        print(reporting_system.generate_company_financial_report(player, general_stock_market_system.listed_companies_on_market))

def show_shop_submenu(p: Player, gt: GameTime):
    """店舗運営のサブメニュー"""
    while True:
        print("\n--- 店舗運営 ---")
        print("1: 店舗設備をアップグレードする")
        print("2: スタッフ管理")
        print("3: メニュー管理")
        print("0: 戻る")
        choice = utils.get_integer_input("選択: ", 0, 3)
        if choice is None or choice == 0: break
        if choice == 1: shop_system.upgrade_shop_equipment(p) 
        elif choice == 2: shop_system.manage_staff(p)       
        elif choice == 3: shop_system.manage_menu(p)

# --- ゲームロジック ---
def process_weekly_events() -> Optional[str]:
    """週を進める処理。ゲームオーバー時に'GAME_OVER'を返す"""
    global player, game_time
    if not player or not game_time: return None
    
    print("\n--- 週を進行中... ---")
    game_time.advance_week()
    market_data = general_stock_market_system.listed_companies_on_market
    
    player.process_weekly_updates(game_time, market_data)
    
    if player.finance.get_cash() < 0:
        print("\n" + "!"*50)
        print("!!! ゲームオーバー !!!")
        print(f"会社の現金が ¥{player.finance.get_cash():,.0f} となり、資金が尽きたため倒産しました。")
        print("!"*50)
        return 'GAME_OVER'
        
    print("--- 週の処理完了 ---")
    return None

def save_game_state_wrapper(p, gt):
    """main_game_loopから呼び出すためのラッパー"""
    save_load_system.save_game({'player': p, 'game_time': gt})

def main_game_loop():
    """テキストベースのメインゲームループ"""
    global player, game_time
    if not player or not game_time: return

    while True:
        display_quick_status()
        
        actions = []
        actions.append({'title': "マップを見る", 'func': lambda p, gt: map_system.show_map_menu(p, gt)})
        if player.ops.businesses_owned:
            actions.append({'title': "店舗運営", 'func': show_shop_submenu})
        actions.append({'title': "会社運営・本部管理", 'func': lambda p, gt: company_system.show_company_management_menu(p, gt)})
        actions.append({'title': "人事・採用 (CXO)", 'func': lambda p, gt: hr_system.show_hr_menu(p, gt)})
        if player.departments.get("rnd"):
            actions.append({'title': "研究開発 (R&D)", 'func': lambda p, gt: rnd_system.show_rnd_menu(p, gt)})
        actions.append({'title': "自社IPO (株式公開)", 'func': lambda p, gt: ipo_system.show_ipo_menu(p, gt)})
        actions.append({'title': "個人資産管理", 'func': lambda p, gt: personal_finance_system.show_personal_finance_menu(p, gt, general_stock_market_system.listed_companies_on_market)})
        actions.append({'title': "経営レポートを見る", 'func': lambda p, gt: show_financial_report()})
        if player.departments.get("investment"):
             actions.append({'title': "ベンチャー投資", 'func': lambda p, gt: venture_system.show_venture_investment_menu(p, gt)})
        actions.append({'title': "企業買収 (M&A/TOB)", 'func': lambda p, gt: acquisition_system.show_acquisition_menu(p, gt)})
        actions.append({'title': "週を進める", 'func': lambda p, gt: process_weekly_events()})
        actions.append({'title': "ゲームを保存する", 'func': save_game_state_wrapper})

        print("\nメインメニュー:")
        for i, action in enumerate(actions):
            print(f"  {i+1}: {action['title']}")
        
        print("\n  0: ゲームを終了する")

        choice = utils.get_integer_input(f"選択 (0-{len(actions)}): ", 0, len(actions))
        if choice is None: continue
        
        if choice == 0:
            print("ゲームを終了します。お疲れ様でした。")
            break
            
        if 0 < choice <= len(actions):
            result = actions[choice-1]['func'](player, game_time)
            if result == 'GAME_OVER':
                break
        else:
            print("無効な選択です。")

def initialize_game():
    """新しいゲームを初期化する"""
    global player, game_time
    print("\n--- ニューゲーム ---")
    company_name = input("あなたの会社名を入力してください: ").strip() or "マイカンパニー"
    
    print("\n--- 競合AIの設定 ---")
    num_competitors = utils.get_integer_input("競合CPUの数を入力してください (3~7): ", 3, 7)
    if num_competitors is None: num_competitors = 3

    difficulty_prompt = """難易度を選択してください:
  1: 最弱 (資金・行動頻度: 低)
  2: 簡単
  3: 普通
  4: 困難
  5: 最恐 (資金・行動頻度: 高)
選択: """
    difficulty_choice = utils.get_integer_input(difficulty_prompt, 1, 5)
    if difficulty_choice is None: difficulty_choice = 3
    
    player = Player(company_name, constants.INITIAL_PERSONAL_MONEY, constants.INITIAL_COMPANY_MONEY)
    game_time = GameTime(2025, 6, 2)
    
    general_stock_market_system.initialize_general_stock_market(constants.NUMBER_OF_LISTED_COMPANIES, game_time.current_year)
    competitor_ai_system.initialize_competitors(num_competitors, difficulty_choice, game_time)
    hr_system.refresh_cxo_candidate_market(game_time)
    map_system.initialize_map()
    
    print(f"\n{company_name}の経営を開始します。")
    main_game_loop()

def load_game_state():
    """ゲーム状態をロードする"""
    global player, game_time
    game_state = save_load_system.load_game()
    if game_state:
        player = game_state.get('player')
        game_time = game_state.get('game_time')
        general_stock_market_system.listed_companies_on_market = game_state.get('listed_companies', [])
        competitor_ai_system.competitor_companies = game_state.get('competitors', [])
        real_estate_system.properties_on_market = game_state.get('real_estate_market', [])
        venture_system.available_venture_deals = game_state.get('venture_deals', [])
        map_system.game_regions = game_state.get('game_regions', [])
        
        print("\nロードが完了しました。ゲームを再開します。")
        main_game_loop()
    else:
        print("ロードに失敗しました。タイトル画面に戻ります。")

def title_screen():
    """ゲーム起動時のタイトル画面"""
    while True:
        print("\n" + "="*30)
        print("  ラーメン経営コングロマリット")
        print("="*30)
        print("\n  1: ニューゲーム")
        if save_load_system.has_save_data(): print("  2: ロードする")
        print("  9: 終了する")
        
        choice = input("選択: ")
        if choice == '1':
            initialize_game()
        elif choice == '2' and save_load_system.has_save_data():
            load_game_state()
        elif choice == '9':
            print("またのプレイをお待ちしております。")
            break
        else:
            print("無効な選択です。")

if __name__ == "__main__":
    try:
        title_screen()
    except Exception as e:
        print(f"\n予期せぬエラーが発生しました: {e}")
        traceback.print_exc()
        print("ゲームを強制終了します。")
        
        
