# systems/map_system.py
from typing import List, Optional
import random

from models.player import Player
from models.game_time import GameTime
from models.region import Region
from models.map_point import MapPoint
from models.property import Property
from constants import map_master_data, property_master_data
from systems import shop_system, real_estate_system, banking_system, general_stock_market_system, stock_market_system
import utils

game_regions: List[Region] = []

def initialize_map() -> List[Region]:
    """マスターデータに基づいてゲーム内のマップと不動産市場を初期化する"""
    global game_regions
    game_regions = []
    
    real_estate_system.initialize_real_estate_market(property_master_data.PROPERTIES_MASTER)

    for region_data in map_master_data.REGIONS_MASTER:
        region = Region(name=region_data["name"], description=region_data["description"])
        
        points_data = map_master_data.MAP_POINTS_MASTER.get(region.name, [])
        for point_data in points_data:
            linked_obj = None
            
            if point_data["point_type"] in ["REAL_ESTATE", "RENTAL_OFFICE"]:
                try:
                    linked_obj = next(p for p in real_estate_system.properties_on_market if p.name == point_data["name"])
                except StopIteration:
                    linked_obj = None

            map_point = MapPoint(
                name=point_data["name"],
                point_type=point_data["point_type"],
                coordinates=point_data["coordinates"],
                linked_object=linked_obj
            )
            region.add_map_point(map_point)
            
        game_regions.append(region)
    
    print(f"{len(game_regions)}地域のマップデータを初期化しました。")
    return game_regions

# --- (以降のCUI用コードは変更なし) ---
def show_securities_firm_menu(player: Player, game_time: GameTime):
    while True:
        print("\n--- 証券会社 ---")
        print("1: 一般株式市場を見る・取引する")
        print("2: 保有株式を管理する (VC投資など)")
        print("0: 地点から離れる")
        choice = utils.get_integer_input("選択: ", 0, 2)
        if choice is None or choice == 0: break
        if choice == 1: general_stock_market_system.show_general_stock_market_menu(player, game_time)
        elif choice == 2: stock_market_system.show_stock_market_menu(player, game_time)

def show_map_point_actions(player: Player, game_time: GameTime, point: MapPoint, region: Region):
    while True:
        print(f"\n--- {point.name} ---")
        action_available = False
        action_prompt = "選択: "
        if point.point_type == "VACANT_SHOP":
            print("ここは新しいお店を建てられる空き区画です。")
            print("1: この区画に出店する")
            action_available = True
        elif point.point_type == "OWNED_SHOP":
            print("ここはあなたの所有する店舗です。")
        elif point.point_type == "REAL_ESTATE":
            if point.linked_object:
                prop = point.linked_object
                net_yield = (prop.weekly_rent_income - prop.weekly_maintenance_cost) * 52 / prop.purchase_price if prop.purchase_price > 0 else 0
                print("ここは投資用の不動産物件です。")
                print(f"  種別: {prop.property_type}, 価格: ¥{prop.purchase_price:,}")
                print(f"  週次収支: ¥{prop.weekly_rent_income - prop.weekly_maintenance_cost:,} / 想定利回り: {net_yield:.2%}")
                print("1: この不動産を購入する")
                action_available = True
            else:
                print("(売却済みまたは情報エラー)")
        elif point.point_type == "OWNED_PROPERTY":
            print("この物件はあなたが所有しています。")
        elif point.point_type == "BANK":
            print("銀行です。融資の相談などができます。")
            print("1: 銀行の機能を利用する")
            action_available = True
        elif point.point_type == "SECURITIES":
            print("証券会社です。株式の売買ができます。")
            print("1: 証券会社の機能を利用する")
            action_available = True
        
        print("0: エリアマップに戻る")
        
        choice = utils.get_integer_input(action_prompt, 0, 1 if action_available else 0)
        if choice is None or choice == 0: break
        if choice == 1:
            if point.point_type == "VACANT_SHOP":
                shop_system.open_new_ramen_shop(player, game_time, region, point)
                break 
            elif point.point_type == "REAL_ESTATE" and point.linked_object:
                real_estate_system.purchase_property_from_map(player, game_time, point.linked_object, point)
                break
            elif point.point_type == "BANK":
                banking_system.show_banking_menu(player, game_time)
            elif point.point_type == "SECURITIES":
                show_securities_firm_menu(player, game_time)
            else:
                print("この機能は現在実装中です。")

def show_region_menu(player: Player, game_time: GameTime, region: Region):
    while True:
        print(f"\n--- {region.name} エリア ---")
        if not region.map_points:
            print("このエリアにはまだ注目すべき地点がありません。")
        else:
            for i, point in enumerate(region.map_points):
                print(f"{i + 1}: {point}")
        
        print("\n0: 地域選択に戻る")
        
        choice = utils.get_integer_input("見る地点を選択してください: ", 0, len(region.map_points))
        
        if choice is None or choice == 0: break
        
        selected_point = region.map_points[choice - 1]
        show_map_point_actions(player, game_time, selected_point, region)

def show_map_menu(player: Player, game_time: GameTime):
    while True:
        print("\n--- 日本地図 ---")
        print("どの地域を見ますか?")
        
        for i, region in enumerate(game_regions):
            print(f"{i + 1}: {region.name}")
        
        print("\n0: メインメニューに戻る")
        
        choice = utils.get_integer_input("地域を選択してください: ", 0, len(game_regions))

        if choice is None or choice == 0: break
        
        selected_region = game_regions[choice - 1]
        show_region_menu(player, game_time, selected_region)

