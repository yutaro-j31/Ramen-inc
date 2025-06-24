# handlers/shop_handler.py
import ui
import console
import constants
from models.menu_item import MenuItem

class ShopActionHandler:
    def __init__(self, game_controller):
        self.gc = game_controller

    def upgrade_equipment(self, shop_object):
        """選択された店舗の設備をアップグレードする"""
        upgrade_cost = shop_object.get_next_upgrade_cost()
        if self.gc.player.finance.get_cash() < upgrade_cost:
            console.hud_alert('アップグレード費用が不足しています。', 'error', 1.5)
            return
        if self.gc.player.ops.upgrade_shop_equipment(shop_object, self.gc.player.finance):
            console.hud_alert(f'「{shop_object.name}」の設備をアップグレードしました!', 'success', 1.5)
            shop_management_view = self.gc.root_view.subviews[0].current_content_view
            if shop_management_view and hasattr(shop_management_view, 'show_equipment_view'):
                shop_management_view.show_equipment_view()
            
    def hire_staff(self, shop_object, staff_candidate):
        """スタッフを雇用する"""
        shop_object.hire_staff(staff_candidate)
        console.hud_alert(f'{staff_candidate.name}を雇用しました。', 'success', 1)
        shop_management_view = self.gc.root_view.subviews[0].current_content_view
        if shop_management_view and hasattr(shop_management_view, 'show_staff_view'):
            shop_management_view.show_staff_view()
            
    def fire_staff(self, shop_object, staff_index):
        """スタッフを解任する"""
        fired_staff = shop_object.fire_staff(staff_index)
        if fired_staff:
            console.hud_alert(f'「{fired_staff.name}」を解任しました。', 'success', 1)
            shop_management_view = self.gc.root_view.subviews[0].current_content_view
            if shop_management_view and hasattr(shop_management_view, 'show_staff_view'):
                shop_management_view.show_staff_view()
                
    def add_menu_item(self, shop_object, menu_data):
        """メニュー項目を追加する"""
        new_item = MenuItem(name=menu_data['name'], price=menu_data['price'], cost=menu_data['cost'])
        shop_object.add_menu_item(new_item)
        console.hud_alert(f'「{new_item.name}」をメニューに追加しました。', 'success', 1)
        shop_management_view = self.gc.root_view.subviews[0].current_content_view
        if shop_management_view and hasattr(shop_management_view, 'show_menu_view'):
            shop_management_view.show_menu_view()
            
    def remove_menu_item(self, shop_object, item_index):
        """メニュー項目を削除する"""
        removed_item = shop_object.remove_menu_item(item_index)
        if removed_item:
            console.hud_alert(f'「{removed_item.name}」をメニューから削除しました。', 'success', 1)
            shop_management_view = self.gc.root_view.subviews[0].current_content_view
            if shop_management_view and hasattr(shop_management_view, 'show_menu_view'):
                shop_management_view.show_menu_view()
    
    def show_shop_management(self, shop_object):
        """店舗一覧から選択された店舗の管理画面を表示する"""
        self.gc.show_shop_management_view(shop_object)
