# handlers/map_handler.py (完全版)
import ui
import console
import constants
from systems import shop_system
from views.action_modal_view import ActionModalView
from views.open_shop_view import OpenShopView

class MapActionHandler:
    def __init__(self, game_controller):
        self.gc = game_controller

    def show_map_point_details(self, region_name, point_name):
        """マップ上の地点をタップした際の処理"""
        region = next((r for r in self.gc.game_regions if r.name == region_name), None)
        if not region: return
        point = next((p for p in region.map_points if p.name == point_name), None)
        if not point: return
        
        if point.point_type == 'OWNED_HQ':
            self.gc.show_hq_view()
            return
        
        if point.point_type == 'VACANT_SHOP':
            self.show_open_shop_view(point)
            return
        if point.point_type == 'OWNED_SHOP':
            self.gc.show_shop_management_view(point.linked_object)
            return
        if point.point_type == 'SECURITIES':
            self.gc.show_stock_market_view()
            return
        if point.point_type == 'BANK':
            self.gc.show_banking_view()
            return
            
        title = point.name
        details = []
        actions = []
        
        if point.point_type == 'RENTAL_OFFICE' and point.linked_object:
            prop = point.linked_object
            title = f"貸しオフィス: {prop.name}"
            details.append(f"契約金: ¥{prop.purchase_price:,.0f}")
            details.append(f"週次賃料: ¥{prop.weekly_maintenance_cost:,.0f}")
            details.append("\nここを本社として契約しますか?")
            actions.append({'title': '契約する', 'action': lambda s: self.rent_office_action(prop, point)})

        elif point.point_type == 'REAL_ESTATE' and point.linked_object:
            prop = point.linked_object
            net_yield = (prop.weekly_rent_income - prop.weekly_maintenance_cost) * 52 / prop.purchase_price if prop.purchase_price > 0 else 0
            details.append(f"種別: {prop.property_type}")
            details.append(f"価格: ¥{prop.purchase_price:,.0f}")
            details.append(f"想定利回り: {net_yield:.2%}")
            actions.append({'title': '会社資金で購入', 'action': lambda s: self.buy_property_action(prop, 'company')})
            actions.append({'title': '個人資産で購入', 'bg_color': '#555', 'action': lambda s: self.buy_property_action(prop, 'personal')})
        else:
            details.append('この地点では現在アクションできません。')

        modal = ActionModalView(title, details, actions, frame=self.gc.root_view.bounds, flex='WH')
        modal.present('fade')
    
    def rent_office_action(self, prop, point):
        """オフィスを借りるアクション"""
        self.gc.root_view.subviews[-1].close()
        
        cost = prop.purchase_price
        rent = prop.weekly_maintenance_cost
        
        if self.gc.player.establish_hq_rented(cost, rent):
            console.hud_alert(f'「{prop.name}」を本社として契約しました!', 'success', 2)
            point.point_type = 'OWNED_HQ'
            point.name = 'マイカンパニー本社'
            
            # メインのUI全体(特にヘッダー)を更新する
            self.gc.root_view.subviews[0].update_view()
            
            self.gc.show_hq_view()
        else:
            console.hud_alert('契約金が不足しています。', 'error', 2)
    
    def show_open_shop_view(self, point):
        """新規出店用のモーダルを表示"""
        setup_cost = 10000000 
        def confirm_action(shop_name, initial_capital):
            self.open_shop_action(point, shop_name, initial_capital)
        open_shop_v = OpenShopView(self, point, setup_cost, confirm_action=confirm_action, cancel_action=None, frame=self.gc.root_view.bounds)
        open_shop_v.present('fade')

    def open_shop_action(self, point, shop_name, initial_capital):
        """新規出店ロジックを呼び出す"""
        region = next((r for r in self.gc.game_regions if point in r.map_points), None)
        if not region:
            console.hud_alert('エラー: 地点の所属地域が見つかりません', 'error', 2)
            return
        new_shop = shop_system.open_new_shop_from_ui(player=self.gc.player, region=region, point=point, shop_name=shop_name, initial_capital=initial_capital)
        if new_shop:
            point.point_type = 'OWNED_SHOP'
            point.name = new_shop.name
            point.linked_object = new_shop
            game_view = self.gc.root_view.subviews[0]
            if game_view and hasattr(game_view, 'update_view'):
                game_view.update_view()

    def buy_property_action(self, prop_object, owner_type):
        """不動産購入ロジックを呼び出す"""
        self.gc.root_view.subviews[-1].close()
        if self.gc.player.buy_property(owner_type, prop_object):
            console.hud_alert(f'「{prop_object.name}」を購入しました。', 'success', 2)
            self.gc.root_view.subviews[0].update_view()

