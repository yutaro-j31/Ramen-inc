# systems/real_estate_system.py
from typing import List
import random

from models.player import Player
from models.game_time import GameTime
from models.property import Property
from models.map_point import MapPoint
properties_on_market: List[Property] = []
import utils


def initialize_real_estate_market(property_master_data: List[dict]):
    """ゲーム開始時に売り出し中の不動産を初期化する"""
    global properties_on_market
    properties_on_market = []
    for prop_data in property_master_data:
        prop = Property(
            name=prop_data["name"],
            property_type=prop_data["property_type"],
            location=prop_data["location"],
            purchase_price=prop_data["purchase_price"], # "price" -> "purchase_price" に修正
            weekly_rent_income=prop_data["weekly_rent_income"],
            weekly_maintenance_cost=prop_data["weekly_maintenance_cost"]
        )
        properties_on_market.append(prop)
    print(f"{len(properties_on_market)}件の不動産を市場に出しました。")


def purchase_property_from_map(player: Player, game_time: GameTime, property_obj: Property, map_point: MapPoint):
    """マップ上の特定の一件を購入する処理"""
    net_yield = (property_obj.weekly_rent_income - property_obj.weekly_maintenance_cost) * 52 / property_obj.purchase_price
    
    print(f"\n--- 不動産購入: {property_obj.name} ---")
    print(f"種別: {property_obj.property_type} ({property_obj.location})")
    print(f"価格: ¥{property_obj.purchase_price:,}")
    print(f"週次家賃収入: ¥{property_obj.weekly_rent_income:,}")
    print(f"週次維持費: ¥{property_obj.weekly_maintenance_cost:,}")
    print(f"想定利回り(実質・年率): {net_yield:.2%}")

    print("\n購入者を選択してください:")
    print("1: 会社として購入")
    print("2: 個人として購入")
    print("0: やめる")

    owner_type_choice = input("選択: ")
    if owner_type_choice not in ["1", "2"]:
        print("購入を中止しました。")
        return

    owner_type = "company" if owner_type_choice == "1" else "personal"
    
    success = player.buy_property(owner_type, property_obj)
    
    if success:
        owner_name = '会社' if owner_type == 'company' else '個人'
        print(f"「{property_obj.name}」を{owner_name}資産として購入しました。")
        
        property_obj.owner_type = owner_type
        
        if property_obj in properties_on_market:
            properties_on_market.remove(property_obj)
            
        map_point.point_type = "OWNED_PROPERTY"
        map_point.name = f"{property_obj.name} (所有: {owner_name})"
    else:
        print("購入に失敗しました。")
        

def update_all_property_values(player: Player):
    """ゲーム内の全ての不動産オブジェクトの価値を更新する。"""
    # 簡易的な経済変動モデル
    economic_impact = random.uniform(-0.002, 0.003) # 週ごとに-0.2%から+0.3%の変動

    # 市場に出ている物件の価値を更新
    for prop in properties_on_market:
        prop.update_weekly_value(economic_impact)

    # プレイヤーが所有する物件の価値を更新
    if hasattr(player.ops, 'owned_properties'):
        for prop in player.ops.owned_properties:
            prop.update_weekly_value(economic_impact)
            
    if hasattr(player.personal_assets, 'owned_properties'):
        for prop in player.personal_assets.owned_properties:
            prop.update_weekly_value(economic_impact)

    # 将来的に、競合AIの所有物件もここで更新する
