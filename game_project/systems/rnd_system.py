# systems/rnd_system.py
import console
from typing import List, Dict, Optional, Any

from models.player import Player
from models.game_time import GameTime
import constants
import utils

def list_available_projects(player: Player) -> List[Dict[str, Any]]:
    """プレイヤーが開始可能なR&Dプロジェクトのリストを返す。"""
    available_projects = []
    
    active_project_ids = {k for k, v in player.effects.active_rnd_bonuses.items() if not v.get('is_permanent')}
    completed_project_ids = player.effects.completed_rnd_projects

    for project_data in constants.RND_PROJECTS_DATA:
        if project_data["id"] in active_project_ids or project_data["id"] in completed_project_ids:
            continue
        
        prereqs_met = True
        for prereq_id in project_data.get("prerequisites", []):
            if prereq_id not in completed_project_ids:
                prereqs_met = False
                break
        if not prereqs_met:
            continue
        
        if "required_department" in project_data:
            if not player.departments.get(project_data["required_department"], False):
                continue
                
        available_projects.append(project_data)
        
    return available_projects


def start_new_project(player: Player, project_data: Dict[str, Any]):
    """新しいR&Dプロジェクトを開始する。"""
    cost_to_start = project_data.get('cost_to_start', 0)
    
    if player.finance.get_cash() < cost_to_start:
        console.hud_alert(f"プロジェクト開始費用が不足しています。(必要額: ¥{cost_to_start:,.0f})", 'error', 2)
        return

    player.finance.record_expense(cost_to_start, 'rnd_start')
    
    project_id = project_data['id']
    in_progress_data = {
        "id": project_id, # ★ プロジェクトIDを追加
        "name": project_data['name'],
        "description": project_data['description'],
        "bonus_effects": project_data.get("bonus_effects", []),
        "research_points_needed": project_data.get("research_points_needed", 1),
        "max_weekly_funding": project_data.get("max_weekly_funding", 0),
        "points_accrued": 0,
        "is_permanent": False,
    }
    player.effects.active_rnd_bonuses[project_id] = in_progress_data

    console.hud_alert(f"R&Dプロジェクト「{project_data['name']}」を開始しました。", 'success', 2)


def show_rnd_menu(player: Player, game_time: GameTime):
    """R&Dシステムのメインメニュー(テキストベース)"""
    while True:
        print("\n--- 研究開発 (R&D) ---")
        
        active_projects = {k: v for k, v in player.effects.active_rnd_bonuses.items() if not v.get("is_permanent")}
        if active_projects:
            print("進行中のプロジェクト:")
            for proj_id, proj_data in active_projects.items():
                progress = (proj_data.get('points_accrued', 0) / proj_data.get('research_points_needed', 1)) * 100
                print(f"  - {proj_data['name']} (進捗: {progress:.1f}%)")
        else:
            print("進行中のプロジェクトはありません。")
        
        print("\n  1: 新しいプロジェクトを開始する")
        print("  2: 進行中のプロジェクトに資金を配分する")
        print("  0: 会社運営メニューに戻る")
        
        choice = utils.get_integer_input("選択: ", 0, 2)
        if choice is None or choice == 0: break

        if choice == 1:
            available = list_available_projects(player)
            if not available:
                print("現在開始できる新しいプロジェクトはありません。")
                continue
            
            print("\n開始可能なプロジェクト:")
            for i, proj in enumerate(available):
                print(f"  {i+1}: {proj['name']} (開始費用: ¥{proj.get('cost_to_start',0):,.0f})")
            
            proj_choice = utils.get_integer_input("選択 (0でキャンセル): ", 0, len(available))
            if proj_choice is None or proj_choice == 0: continue
            
            start_new_project(player, available[proj_choice - 1])

        elif choice == 2:
            if not active_projects:
                print("資金を配分できるプロジェクトがありません。")
                continue
            
            active_list = list(active_projects.items())
            print("\n資金を配分するプロジェクトを選択:")
            for i, (proj_id, proj_data) in enumerate(active_list):
                print(f"  {i+1}: {proj_data['name']}")
            
            proj_choice = utils.get_integer_input("選択 (0でキャンセル): ", 0, len(active_list))
            if proj_choice is None or proj_choice == 0: continue
            
            project_id_to_fund, project_to_fund_data = active_list[proj_choice - 1]
            max_fund = project_to_fund_data.get('max_weekly_funding', 0)
            funding_amount = utils.get_integer_input(f"投入額を入力 (最大: ¥{max_fund:,.0f}): ", 0, max_fund)
            
            if funding_amount:
                allocate_funding_to_project_from_ui(player, project_id_to_fund, funding_amount)

# この関数がインデントなしでファイルレベルに定義されていることを確認
def allocate_funding_to_project_from_ui(player: Player, project_id: str, funding_amount: int) -> bool:
    """UIから指定された額の資金をプロジェクトに投入する"""
    project = player.effects.active_rnd_bonuses.get(project_id)
    if not project or project.get('is_permanent'):
        return False

    max_funding = project.get('max_weekly_funding', 0)
    if not (0 < funding_amount <= max_funding):
        console.hud_alert(f'投入額は¥1~¥{max_funding:,.0f}の範囲で入力してください。', 'error', 2)
        return False
        
    if player.finance.get_cash() < funding_amount:
        console.hud_alert('資金が不足しています。', 'error', 1.5)
        return False

    player.finance.record_expense(funding_amount, 'rnd_funding')
    project['points_accrued'] += funding_amount
    
    if project['points_accrued'] >= project.get('research_points_needed', float('inf')):
        console.hud_alert(f"🎉 プロジェクト「{project['name']}」の研究が完了しました!", 'success', 2.5)
        player.effects.add_completed_rnd_project(project_id, project.get("bonus_effects", []))
        if project_id in player.effects.active_rnd_bonuses:
            del player.effects.active_rnd_bonuses[project_id]
            
    return True
