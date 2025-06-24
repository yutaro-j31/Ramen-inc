# systems/hr_system.py
import random
import uuid
from typing import List, Dict, Any, Optional

from models.player import Player
from models.game_time import GameTime
from models.cxo import CXO
import constants
import utils


# --- モジュールレベル変数 ---
available_cxo_candidates: List[CXO] = []
MAX_CXO_CANDIDATES_ON_MARKET = 5
WEEKS_TO_REFRESH_CXO_MARKET = 26
last_cxo_market_refresh_week = -WEEKS_TO_REFRESH_CXO_MARKET

# ★★★ このファイル固有の入力受付関数は削除しました ★★★

def _generate_random_cxo_candidate() -> Optional[CXO]:
    """ランダムなCXO候補者を1名生成する"""
    if not constants.CXO_TYPES or not constants.CXO_NAME_LIST:
        return None

    position_key = random.choice(list(constants.CXO_TYPES.keys()))
    position_data = constants.CXO_TYPES[position_key]
    
    name = random.choice(constants.CXO_NAME_LIST)
    # 簡単な重複チェック
    if any(cand.name == name and cand.position == position_key for cand in available_cxo_candidates):
        name += " Jr." # 仮の重複回避

    skill_levels = list(position_data["skill_levels"].keys()) # S, A, B, C
    # スキルレベルの出現確率 (例: Cが多く、Sは稀)
    skill_level = random.choices(skill_levels, weights=[0.4, 0.3, 0.2, 0.1], k=1)[0] # C, B, A, S の順の確率
    
    base_salary_min, base_salary_max = position_data["base_weekly_salary_range"]
    # スキルレベルに応じて給与を変動
    salary_multiplier = {"S": 1.5, "A": 1.2, "B": 1.0, "C": 0.8}.get(skill_level, 1.0)
    weekly_salary = random.uniform(base_salary_min, base_salary_max) * salary_multiplier
    weekly_salary = round(weekly_salary / 10000) * 10000 # 1万円単位に丸める

    effects = position_data["effects"] # CXOの効果リストをコピー

    candidate = CXO(
        name=name,
        position=position_key, # CFO, CMOなど
        skill_level=skill_level,
        weekly_salary=weekly_salary,
        effects=effects
    )
    candidate.display_position_name = position_data.get("display_name", position_key)
    return candidate

def refresh_cxo_candidate_market(game_time: GameTime):
    """CXO候補者市場のリストを更新する"""
    global available_cxo_candidates, last_cxo_market_refresh_week
    if game_time.total_weeks_elapsed < last_cxo_market_refresh_week + constants.WEEKS_TO_REFRESH_CXO_MARKET and available_cxo_candidates:
        return # まだリフレッシュ時期ではない

    available_cxo_candidates = []
    num_to_generate = MAX_CXO_CANDIDATES_ON_MARKET
    # 将来的には、会社の評判やHR部門のレベルで候補者の質や数が変わるようにしても良い
    for _ in range(num_to_generate):
        candidate = _generate_random_cxo_candidate()
        if candidate:
            available_cxo_candidates.append(candidate)
    last_cxo_market_refresh_week = game_time.total_weeks_elapsed
    if available_cxo_candidates:
        print(f"CXO人材市場に新たに{len(available_cxo_candidates)}名の候補者が現れました。")

# --- 人事システム機能 ---
def view_cxo_candidates(player: Player, game_time: GameTime) -> List[CXO]:
    """雇用可能なCXO候補者リストを表示する"""
    global available_cxo_candidates
    if not player.departments.get("hr"):
        print("人事部門が未設置のため、高度な人材サーチは限定的です。(CXO候補者を発見できません)")
        return []
    
    refresh_cxo_candidate_market(game_time)

    if not available_cxo_candidates:
        print("現在、CXO人材市場に候補者はいません。")
        return []

    print("\n--- CXO人材市場 候補者リスト ---")
    display_candidates = []
    for candidate in available_cxo_candidates:
        # 既にプレイヤーがその役職のCXOを雇用していないかチェック
        if candidate.position not in player.employed_cxos:
            display_candidates.append(candidate)
            
    if not display_candidates:
        print("現在、あなたが新たに雇用できる役職のCXO候補者はいません。(全ての役職が埋まっているか、市場に該当者がいません)")
        return []

    for i, candidate in enumerate(display_candidates):
        print(f"  {i+1}. {candidate.name} - {candidate.display_position_name} ({candidate.skill_level}ランク)")
        print(f"      要求週給: ¥{candidate.weekly_salary:,.0f}")
        # 簡単な効果サマリー表示
        effects_summary = [eff.get("description", eff.get("type")) for eff in candidate.effects[:2]] # 効果を2つまで表示
        if effects_summary:
            print(f"      主な期待効果: {', '.join(effects_summary)}{' など' if len(candidate.effects) > 2 else ''}")
            
    return display_candidates


def hire_cxo_action(player: Player, candidate: CXO, game_time: GameTime):
    """選択されたCXO候補者を雇用する"""
    print(f"\n--- {candidate.name} ({candidate.display_position_name}) の雇用交渉 ---")
    print(candidate.get_detailed_description()) # 詳細情報を表示
    
    recruitment_cost = constants.CXO_RECRUITMENT_COST_BASE * \
                       constants.CXO_RECRUITMENT_COST_SKILL_MULTIPLIER.get(candidate.skill_level, 1.0)
    
    print(f"\n契約一時金: ¥{recruitment_cost:,.0f}")
    print(f"週給: ¥{candidate.weekly_salary:,.0f}")
    
    if player.finance.get_cash() < recruitment_cost:
        print(f"契約一時金の支払いに必要な会社資金が不足しています。(必要額: ¥{recruitment_cost:,.0f})")
        return

    confirm = input("この条件で雇用契約を結びますか? (y/n): ").lower()
    if confirm != 'y':
        print("雇用契約を見送りました。")
        return

    player.finance.record_expense(recruitment_cost, 'recruitment') # 契約一時金も費用
    
    if player.hr.hire_cxo(candidate):
        candidate.is_hired = True
        candidate.hired_by_company_name = player.company_name
        
        print(f"\n{candidate.name}さん ({candidate.display_position_name}) との雇用契約が成立しました!")
        print(f"  契約一時金 ¥{recruitment_cost:,.0f} を支払いました。")
        
        # 市場リストから削除
        global available_cxo_candidates
        available_cxo_candidates = [c for c in available_cxo_candidates if c.cxo_id != candidate.cxo_id]


def view_employed_cxos(player: Player):
    """現在雇用しているCXOの一覧を表示する"""
    print("\n--- 現在の経営幹部 (CXO) ---")
    if not player.employed_cxos:
        print("現在、雇用しているCXOはいません。")
        return

    for position, cxo in player.employed_cxos.items():
        print(f"  {cxo.display_position_name}: {cxo.name} ({cxo.skill_level}ランク)")
        print(f"    週給: ¥{cxo.weekly_salary:,.0f}")
        effects_summary = [eff.get("description", eff.get("type")) for eff in cxo.effects]
        if effects_summary:
            print(f"    発揮中の効果: {', '.join(effects_summary)}")
        print("-"*10)


def show_hr_menu(player: Player, game_time: GameTime):
    """人事システムのメインメニュー"""
    if not player.departments.get("hr"):
        print("\n(注意: 人事部門が未設置のため、CXO人材のサーチ能力が限定的です。)")

    while True:
        print("\n--- 人事・採用 (CXO) ---")
        print("  1: CXO候補者リストを見る・雇用する")
        print("  2: 現在の経営幹部を見る")
        print("  0: メインメニューに戻る")

        choice = utils.get_integer_input("選択: ", 0, 2) # ★utilsの関数に変更
        if choice is None: continue

        if choice == 1:
            if len(player.employed_cxos) >= constants.MAX_CXOS_PER_COMPANY:
                print("既に最大数のCXOを雇用しています。新たなCXOを雇用するには、誰かを解任する必要があります。")
                continue
            candidates = view_cxo_candidates(player, game_time)
            if candidates:
                candidate_choice = utils.get_integer_input(f"採用交渉する候補者を選択してください (1-{len(candidates)}, 0で戻る): ", 0, len(candidates)) # ★utilsの関数に変更
                if candidate_choice is not None and candidate_choice > 0:
                    selected_candidate = candidates[candidate_choice - 1]
                    hire_cxo_action(player, selected_candidate, game_time)
        elif choice == 2:
            view_employed_cxos(player)
        elif choice == 0:
            break
