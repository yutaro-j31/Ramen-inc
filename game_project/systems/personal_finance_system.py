# systems/personal_finance_system.py
# 省略なしの完全なコードです。

import random
from typing import List, Optional, Any, Dict

from models.player import Player
from models.game_time import GameTime
import constants
import utils


# ★★★ このファイル固有の入力受付関数は削除しました ★★★

# --- 機能 ---

def view_and_exercise_stock_options(player: Player, game_time: GameTime, market_data: List[Any]):
    """ストックオプションの確認と権利行使"""
    print("\n--- ストックオプション管理 ---")
    
    options = player.personal_assets.stock_options
    if not options:
        print("行使可能なストックオプションはありません。")
        return

    print("保有ストックオプション一覧:")
    exercisable_options: List[Dict[str, Any]] = []
    for i, option in enumerate(options):
        status = "未確定"
        if option['is_expired']:
            status = "期限切れ"
        elif option['is_exercised']:
            status = "行使済み"
        elif option['is_vested']:
            status = "権利確定済み"
            exercisable_options.append(option)
        
        print(f"  {i+1}. ID: ...{option['grant_id'][-6:]} ({option['company_name']})")
        print(f"      株数: {option['num_shares']:,}株, 行使価格: ¥{option['strike_price']:,.0f}, ステータス: {status}")

    if not exercisable_options:
        print("\n現在、権利を行使できるストックオプションはありません。")
        return

    print("\n権利を行使するストックオプションを選択してください。")
    for i, option in enumerate(exercisable_options):
         print(f"  {i+1}: ID: ...{option['grant_id'][-6:]} ({option['num_shares']:,}株)")
    print("  0: キャンセル")

    choice = utils.get_integer_input("選択: ", 0, len(exercisable_options))
    if choice is None or choice == 0:
        return

    selected_option = exercisable_options[choice - 1]
    
    # 行使コストの計算
    exercise_cost = selected_option['num_shares'] * selected_option['strike_price']
    
    # 現在の市場価格を取得(簡易的に会社名で検索)
    # 本来はティッカーシンボルで行うべき
    market_price = 0
    company_on_market = next((c for c in market_data if c.company_name == selected_option['company_name']), None)
    if company_on_market:
        market_price = company_on_market.current_price
    
    print("\n--- ストックオプション権利行使の確認 ---")
    print(f"  対象: {selected_option['company_name']} {selected_option['num_shares']:,}株")
    print(f"  行使価格: ¥{selected_option['strike_price']:,.0f} / 株")
    print(f"  市場価格: ¥{market_price:,.0f} / 株")
    print(f"  必要な個人資産: ¥{exercise_cost:,.0f}")
    
    if market_price > selected_option['strike_price']:
        gain = (market_price - selected_option['strike_price']) * selected_option['num_shares']
        print(f"  推定含み益: ¥{gain:,.0f}")
    else:
        print("  警告: 現在の市場価格が行使価格を下回っています。")

    if player.personal_assets.money < exercise_cost:
        print("個人資産が不足しているため、権利を行使できません。")
        return

    confirm = input("このストックオプションの権利を行使しますか? (y/n): ").lower()
    if confirm == 'y':
        player.personal_assets.money -= exercise_cost
        # 行使した株式を個人ポートフォリオに追加
        player.personal_portfolio.add_stock_from_option(selected_option, game_time)
        selected_option['is_exercised'] = True
        print("ストックオプションの権利を行使し、株式を取得しました。")

def purchase_luxury_good(player: Player, game_time: GameTime):
    """贅沢品を購入する"""
    print("\n--- 贅沢品の購入 ---")
    
    owned_good_ids = {good.get("id") for good in player.personal_assets.owned_luxury_goods}
    available_goods = [good for good in constants.LUXURY_GOODS_DATA if good['id'] not in owned_good_ids]

    if not available_goods:
        print("現在購入可能な贅沢品はありません。")
        return
        
    print("購入する贅沢品を選択してください:")
    for i, good in enumerate(available_goods):
        print(f"  {i+1}: {good['name']} (価格: ¥{good['price']:,.0f})")
        print(f"      カテゴリ: {good['category']}, 週次維持費: ¥{good['weekly_upkeep_cost']:,.0f}")
        print(f"      「{good['description']}」")
    print("  0: キャンセル")
    
    choice = utils.get_integer_input("選択: ", 0, len(available_goods))
    if choice is None or choice == 0:
        print("購入をキャンセルしました。")
        return
        
    selected_good = available_goods[choice-1]
    price = selected_good['price']

    if player.personal_assets.money < price:
        print("個人資産が不足しており、この贅沢品は購入できません。")
        return

    confirm = input(f"「{selected_good['name']}」を ¥{price:,.0f}で購入しますか? (y/n): ").lower()
    if confirm == 'y':
        player.personal_assets.money -= price
        player.personal_assets.owned_luxury_goods.append(selected_good)
        print(f"「{selected_good['name']}」を購入しました!")
    else:
        print("購入をキャンセルしました。")

def set_player_salary_action(player: Player, game_time: GameTime):
    """役員報酬を設定するアクション"""
    print("\n--- 役員報酬設定 ---")
    print(f"現在の週次役員報酬: ¥{player.player_weekly_salary:,.0f}")
    
    max_salary = 0
    if player.ipo.is_company_public:
        revenue, profit = player.finance.get_estimated_annuals(game_time)
        max_salary = (profit * constants.MAX_PLAYER_WEEKLY_SALARY_PUBLIC_COMPANY_RATIO_TO_PROFIT) / game_time.WEEKS_PER_YEAR
    else:
        max_salary = player.finance.get_cash() * constants.MAX_PLAYER_WEEKLY_SALARY_PRIVATE_COMPANY_RATIO_TO_CASH
    
    max_salary = max(0, int(max_salary))
    
    print(f"設定可能な最大週次報酬額の目安: ¥{max_salary:,.0f}")
    
    new_salary_input = utils.get_integer_input(
        "新しい週次報酬額を入力してください (0でキャンセル): ", 0, int(max_salary) if max_salary > 0 else 1_000_000_000
    )

    if new_salary_input is None:
        print("役員報酬の変更をキャンセルしました。")
        return
        
    if new_salary_input > max_salary:
        print("警告: 設定額が推奨最大額を超えています。会社のキャッシュフローに注意してください。")

    player.player_weekly_salary = float(new_salary_input)
    print(f"新しい週次役員報酬を ¥{player.player_weekly_salary:,.0f} に設定しました。")


def show_personal_finance_menu(player: Player, game_time: GameTime, market_data: List[Any]):
    """個人資産管理のメインメニュー"""
    while True:
        print("\n--- 個人資産管理 ---")
        print(f"  現在の個人資産(現金): ¥{player.personal_assets.money:,.0f}")
        # (ここに他の個人資産サマリーを追加可能)
        
        print("\n  1: ストックオプションを確認・行使する")
        print("  2: 贅沢品を購入する")
        print("  3: 役員報酬を設定する")
        print("  0: メインメニューに戻る")

        choice = utils.get_integer_input("選択: ", 0, 3)
        if choice is None: continue

        if choice == 1:
            view_and_exercise_stock_options(player, game_time, market_data)
        elif choice == 2:
            purchase_luxury_good(player, game_time)
        elif choice == 3:
            set_player_salary_action(player, game_time)
        elif choice == 0:
            break
