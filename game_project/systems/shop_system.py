# systems/shop_system.py (修正版)
import random
from typing import Optional
import console

from models.player import Player
from models.game_time import GameTime
from models.business_unit import BusinessUnit
from models.menu_item import MenuItem
from models.staff import Staff
from models.region import Region
from models.map_point import MapPoint
import constants
import utils
from constants import map_master_data


def select_shop_from_owned(player: Player, action_description: str) -> Optional[BusinessUnit]:
    if not player.ops.businesses_owned:
        print(f"{action_description}対象の店舗がありません。")
        return None
    
    print(f"\n{action_description}対象の店舗を選択してください:")
    for i, shop in enumerate(player.ops.businesses_owned):
        print(f"  {i+1}: {shop.name} (設備レベル: {shop.equipment_level})")
    print("  0: キャンセル")

    shop_choice = utils.get_integer_input("選択: ", 0, len(player.ops.businesses_owned))
    if shop_choice is None or shop_choice == 0:
        return None
    
    return player.ops.businesses_owned[shop_choice - 1]

def open_new_ramen_shop(player: Player, game_time: GameTime, region: Region, map_point: MapPoint):
    """指定されたマップ上の地点に新しいラーメン店を開店する。"""
    print(f"\n--- {region.name}・{map_point.name}への新規出店 ---")
    
    try:
        selected_location = next(loc for loc in map_master_data.REGIONS_MASTER if loc['name'] == region.name)
    except StopIteration:
        print(f"エラー: {region.name} の立地データ(REGIONS_MASTER)が見つかりません。")
        return

    shop_name = input("新しい店舗の名前を入力してください: ").strip()
    if not shop_name:
        shop_name = f"{player.company_name} {region.name}店"
        print(f"店舗名が入力されなかったので、「{shop_name}」とします。")

    base_setup_cost = constants.BASE_SHOP_SETUP_COST
    actual_setup_cost = int(base_setup_cost * selected_location['setup_multiplier'])
    
    print(f"\n店舗名: {shop_name}")
    print(f"立地: {selected_location['name']}")
    print(f"初期セットアップコスト: ¥{actual_setup_cost:,.0f}")
    
    # CUI版では個人資産から会社に資本注入する流れのため、この部分はそのままにします
    initial_capital_prompt = "会社の初期運転資金として、個人資産からいくら投入しますか? (0でキャンセル): "
    initial_company_capital_input = utils.get_integer_input(initial_capital_prompt, 0)
    if initial_company_capital_input is None or initial_company_capital_input == 0:
        print("出店をキャンセルしました。")
        return
        
    initial_company_capital = initial_company_capital_input

    total_cost = actual_setup_cost + initial_company_capital
    print(f"必要な個人資産: ¥{total_cost:,.0f} (セットアップ費用 + 初期運転資金)")
    if player.money_personal < total_cost:
        print(f"個人資産が不足しています。(現在: ¥{player.money_personal:,.0f})")
        return

    confirm = input("この内容で出店しますか? (y/n): ").lower()
    if confirm == 'y':
        new_shop = BusinessUnit(
            name=shop_name,
            business_type=constants.DEFAULT_RAMEN_SHOP_TYPE_NAME,
            location_name=selected_location['name'],
            base_weekly_fixed_costs=float(selected_location['rent_base']),
            location_sales_modifier=float(selected_location['sales_modifier']),
            base_weekly_customer_pool=int(selected_location['base_weekly_customer_pool'])
        )
        if player.acquire_business(new_shop, actual_setup_cost, initial_company_capital):
            print(f"\n「{shop_name}」が無事オープンしました!")
            map_point.name = shop_name
            map_point.point_type = "OWNED_SHOP"
            map_point.linked_object = new_shop
    else:
        print("出店をキャンセルしました。")

def upgrade_shop_equipment(player: Player):
    selected_shop = select_shop_from_owned(player, "設備アップグレード")
    if not selected_shop:
        return
    if selected_shop.equipment_level >= constants.MAX_EQUIPMENT_LEVEL.get(selected_shop.business_type, 5):
        print("この店舗の設備は既に最大レベルです。")
        return
    upgrade_cost = selected_shop.get_next_upgrade_cost()
    print(f"現在の設備レベル: {selected_shop.equipment_level}")
    print(f"次のレベルへのアップグレード費用: ¥{upgrade_cost:,.0f}")
    confirm = input("アップグレードしますか? (y/n): ").lower()
    if confirm == 'y':
        if player.ops.upgrade_shop_equipment(selected_shop, player.finance):
            print(f"「{selected_shop.name}」の設備をレベル {selected_shop.equipment_level} にアップグレードしました!")
        else:
            print("アップグレード費用が不足しています。")

def manage_staff(player: Player):
    selected_shop = select_shop_from_owned(player, "スタッフ管理")
    if not selected_shop:
        return
    while True:
        print(f"\n--- 「{selected_shop.name}」のスタッフ管理 ---")
        selected_shop.display_staff()
        print("\n  1: スタッフを雇用する")
        print("  2: スタッフを解雇する")
        print("  0: 戻る")
        choice = utils.get_integer_input("選択: ", 0, 2)
        if choice is None or choice == 0: break
        if choice == 1:
            print("\n雇用可能なスタッフ候補:")
            for i, candidate in enumerate(constants.STAFF_CANDIDATES):
                print(f"  {i+1}: {candidate.name} ({candidate.role}) - 週給: ¥{candidate.weekly_salary:,}")
            hire_choice = utils.get_integer_input("雇用するスタッフを選択 (0でキャンセル): ", 0, len(constants.STAFF_CANDIDATES))
            if hire_choice is None or hire_choice == 0: continue
            hired_staff_data = constants.STAFF_CANDIDATES[hire_choice - 1]
            new_staff = Staff(
                name=hired_staff_data.name, role=hired_staff_data.role,
                weekly_salary=hired_staff_data.weekly_salary, efficiency_modifier=hired_staff_data.efficiency_modifier
            )
            selected_shop.hire_staff(new_staff)
            print(f"「{hired_staff_data.name}」を雇用しました。")
        elif choice == 2:
            if not selected_shop.staff_list:
                print("解雇できるスタッフがいません。")
                continue
            print("解雇するスタッフを選択してください:")
            for i, staff in enumerate(selected_shop.staff_list):
                print(f"  {i+1}: {staff.name} ({staff.role})")
            fire_choice = utils.get_integer_input("選択 (0でキャンセル): ", 0, len(selected_shop.staff_list))
            if fire_choice is None or fire_choice == 0: continue
            fired_staff = selected_shop.fire_staff(fire_choice - 1)
            if fired_staff:
                print(f"「{fired_staff.name}」を解雇しました。")

def manage_menu(player: Player):
    selected_shop = select_shop_from_owned(player, "メニュー管理")
    if not selected_shop:
        return
    while True:
        print(f"\n--- 「{selected_shop.name}」のメニュー管理 ---")
        print("現在のメニュー:")
        selected_shop.display_menu()
        print("\n  1: メニュー項目を追加する")
        print("  2: メニュー項目を削除する")
        print("  0: 戻る")
        choice = utils.get_integer_input("選択: ", 0, 2)
        if choice is None or choice == 0: break
        if choice == 1:
            print("\n追加可能なメニュー項目:")
            available_items = [item for item in constants.AVAILABLE_MENU_ITEMS_MASTER_DATA if item['name'] not in [m.name for m in selected_shop.menu]]
            if not available_items:
                print("追加できるメニュー項目がありません。")
                continue
            for i, item_data in enumerate(available_items):
                print(f"  {i+1}: {item_data['name']} (価格:¥{item_data['price']:,}, 原価:¥{item_data['cost']:,})")
            add_choice = utils.get_integer_input("追加する項目を選択 (0でキャンセル): ", 0, len(available_items))
            if add_choice is None or add_choice == 0: continue
            item_to_add_data = available_items[add_choice - 1]
            new_item = MenuItem(name=item_to_add_data['name'], price=item_to_add_data['price'], cost=item_to_add_data['cost'])
            selected_shop.add_menu_item(new_item)
            print(f"「{new_item.name}」をメニューに追加しました。")
        elif choice == 2:
            if not selected_shop.menu:
                print("削除できるメニュー項目がありません。")
                continue
            print("削除するメニュー項目を選択してください:")
            for i, item in enumerate(selected_shop.menu):
                print(f"  {i+1}: {item.name}")
            remove_choice = utils.get_integer_input("選択 (0でキャンセル): ", 0, len(selected_shop.menu))
            if remove_choice is None or remove_choice == 0: continue
            removed_item = selected_shop.remove_menu_item(remove_choice - 1)
            if removed_item:
                print(f"「{removed_item.name}」をメニューから削除しました。")
                
def open_new_shop_from_ui(player: Player, region: Region, point: MapPoint, shop_name: str, initial_capital: int) -> Optional['BusinessUnit']:
    """UIからの情報に基づいて新規店舗を開店する"""
    
    try:
        selected_location = next(loc for loc in constants.map_master_data.REGIONS_MASTER if loc['name'] == region.name)
        base_setup_cost = constants.BASE_SHOP_SETUP_COST
        actual_setup_cost = int(base_setup_cost * selected_location['setup_multiplier'])
    except StopIteration:
        print(f"エラー: {region.name} の立地データが見つかりません。")
        return None
    
    total_cost = actual_setup_cost + initial_capital

    if player.finance.get_cash() < total_cost:
        console.hud_alert('出店費用と初期資本金を支払うための会社の資金が不足しています。', 'error', 2)
        return None

    new_shop = BusinessUnit(
        name=shop_name,
        business_type=constants.DEFAULT_RAMEN_SHOP_TYPE_NAME,
        location_name=selected_location['name'],
        base_weekly_fixed_costs=float(selected_location['rent_base']),
        location_sales_modifier=float(selected_location['sales_modifier']),
        base_weekly_customer_pool=int(selected_location['base_weekly_customer_pool'])
    )
    
    if player.acquire_business(new_shop, actual_setup_cost, initial_capital):
        console.hud_alert(f'「{shop_name}」が無事オープンしました!', 'success', 2)
        return new_shop
    else:
        console.hud_alert('出店処理中に不明なエラーが発生しました。', 'error', 2)
        return None
