# systems/company_system.py
from typing import Dict, Callable, Any
import console

from models.player import Player
from models.game_time import GameTime
import constants
import utils

def show_hq_and_department_status(player: Player):
    """本部と部門の現在の状況を表示する。(テキストベースメニュー用)"""
    print("\n--- 本部・部門状況 ---")
    print(f"  本部形態: {player.headquarters_type}")
    if player.headquarters_type == "賃貸オフィス":
        print(f"  週次家賃: ¥{player.hq_weekly_rent:,.0f}")
    
    depts = player.departments
    print(f"  部門: 投資({_d(depts, 'investment')}), 人事({_d(depts, 'hr')}), R&D({_d(depts, 'rnd')}), マーケティング({_d(depts, 'marketing')})")

def establish_hq(player: Player, choice: int):
    """本部設立のロジックのみを行う"""
    if player.headquarters_type != "なし":
        print("既に本部が設立されています。")
        return

    if choice == 1: # 賃貸
        cost = constants.HQ_RENTED_INITIAL_COST
        if player.finance.get_cash() >= cost:
            player.establish_hq_rented(cost, constants.HQ_RENTED_WEEKLY_RENT)
            print(f"賃貸オフィスを契約し、本部を設立しました。初期費用: ¥{cost:,.0f}")
        else:
            print("エラー: 資金が不足しています。")
    elif choice == 2: # 所有
        cost = constants.HQ_OWNED_CONSTRUCTION_COST
        if player.finance.get_cash() >= cost:
            player.establish_hq_owned(cost)
            print(f"自社ビルを建設し、本部を設立しました。建設費用: ¥{cost:,.0f}")
        else:
            print("エラー: 資金が不足しています。")

def establish_department(player: Player, dept_key: str):
    """部門設置のロジックのみを行う"""
    if player.headquarters_type == "なし":
        print("部門を設置するには、まず本部を設立してください。")
        return

    cost_map = {
        "investment": constants.INVESTMENT_DEPT_SETUP_COST,
        "hr": constants.HR_DEPT_SETUP_COST,
        "rnd": constants.RND_DEPT_SETUP_COST,
        "marketing": constants.MARKETING_DEPT_SETUP_COST
    }
    cost = cost_map.get(dept_key)
    if cost is None: 
        print("エラー: 無効な部門です。")
        return

    if player.departments.get(dept_key, False):
        print(f"エラー: {dept_key.upper()}部門は既に存在します。")
        return
        
    if player.finance.get_cash() >= cost:
        player.establish_department(dept_key, cost)
        print(f"{dept_key.upper()}部門を新設しました。設置費用: ¥{cost:,.0f}")
    else:
        print("エラー: 資金が不足しています。")

def set_player_salary_action(player: Player, game_time: GameTime):
    """役員報酬を設定するアクション"""
    current_salary = player.player_weekly_salary
    print(f"\n現在の週次役員報酬: ¥{current_salary:,.0f}")
    
    max_salary = 0
    if player.is_company_public:
        _r, profit = player.finance.get_estimated_annuals(game_time)
        max_salary = (profit * constants.MAX_PLAYER_WEEKLY_SALARY_PUBLIC_COMPANY_RATIO_TO_PROFIT) / game_time.WEEKS_PER_YEAR
    else:
        max_salary = player.finance.get_cash() * constants.MAX_PLAYER_WEEKLY_SALARY_PRIVATE_COMPANY_RATIO_TO_CASH
    max_salary = max(0, int(max_salary))

    print(f"設定可能な最大週次報酬額の目安: ¥{max_salary:,.0f}")
    
    new_salary = utils.get_integer_input("新しい週次報酬額を入力してください (0でキャンセル): ", 0)

    if new_salary is not None:
        if new_salary > max_salary:
            print("警告: 設定額が推奨最大額を超えています。会社のキャッシュフローに注意してください。")
        player.player_weekly_salary = float(new_salary)
        print(f"新しい週次役員報酬を ¥{player.player_weekly_salary:,.0f} に設定しました。")

def show_company_management_menu(player: Player, game_time: GameTime):
    """会社運営・本部管理のテキストベースメニューを表示する"""
    while True:
        show_hq_and_department_status(player)

        print("\n--- 会社運営・本部管理メニュー ---")
        print("  1: 本部を設立する")
        print("  2: 部門を設置する")
        print("  3: 役員報酬を設定する")
        print("  0: メインメニューに戻る")

        choice = utils.get_integer_input("選択: ", 0, 3)
        if choice is None or choice == 0:
            break
        
        if choice == 1:
            hq_choice = utils.get_integer_input("1: 賃貸オフィス, 2: 自社ビル, 0: キャンセル: ", 0, 2)
            if hq_choice is not None and hq_choice > 0:
                establish_hq(player, hq_choice)
        elif choice == 2:
            dept_key = input("設置する部門名を入力 (investment, hr, rnd, marketing): ").lower()
            if dept_key in ["investment", "hr", "rnd", "marketing"]:
                establish_department(player, dept_key)
            else:
                print("無効な部門名です。")
        elif choice == 3:
            set_player_salary_action(player, game_time)

def _d(depts: Dict[str, bool], key: str) -> str:
    """部門の設置状況を「済」か「未」で返すヘルパー関数"""
    return "済" if depts.get(key) else "未"
