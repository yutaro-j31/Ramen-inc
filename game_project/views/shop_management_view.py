# views/shop_management_view.py (修正版)
import ui
import console
import constants
from models.menu_item import MenuItem

class StaffListDataSource:
    """スタッフリスト用のTableViewデータソース"""
    def __init__(self, items, action_title, action):
        self.items = items
        self.action_title = action_title
        self.action = action

    def tableview_number_of_rows(self, tableview, section):
        return len(self.items)

    def tableview_cell_for_row(self, tableview, section, row):
        cell = ui.TableViewCell('subtitle')
        staff = self.items[row]
        cell.text_label.text = f"{staff.name} ({staff.role})"
        cell.detail_text_label.text = f"週給: ¥{staff.weekly_salary:,.0f} | 効率: {staff.efficiency_modifier*100:.0f}%"
        
        action_button = ui.Button(title=self.action_title)
        action_button.frame = (tableview.width - 90, 7, 80, 30)
        action_button.background_color = '#C53426' if self.action_title == '解雇' else '#34C759'
        action_button.tint_color = 'white'
        action_button.corner_radius = 5
        action_button.font = ('<system-bold>', 12)
        action_button.row = row
        action_button.action = self.action
        cell.content_view.add_subview(action_button)
        
        return cell
        
class MenuListDataSource:
    """メニューリスト用のTableViewデータソース"""
    def __init__(self, items, action_title, action):
        self.items = items
        self.action_title = action_title
        self.action = action

    def tableview_number_of_rows(self, tableview, section):
        return len(self.items)

    def tableview_cell_for_row(self, tableview, section, row):
        cell = ui.TableViewCell('subtitle')
        menu = self.items[row]
        cell.text_label.text = menu.name
        cell.detail_text_label.text = f"価格: ¥{menu.price:,.0f} | 原価: ¥{menu.cost:,.0f}"
        
        action_button = ui.Button(title=self.action_title)
        action_button.frame = (tableview.width - 90, 7, 80, 30)
        action_button.background_color = '#C53426' if self.action_title == '削除' else '#34C759'
        action_button.tint_color = 'white'
        action_button.corner_radius = 5
        action_button.font = ('<system-bold>', 12)
        action_button.row = row
        action_button.action = self.action
        cell.content_view.add_subview(action_button)
        
        return cell

class ShopManagementView(ui.View):
    """店舗の詳細な運営画面"""
    def __init__(self, shop_handler, shop, **kwargs):
        super().__init__(**kwargs)
        self.shop_handler = shop_handler
        self.game_controller = shop_handler.gc
        self.shop = shop 
        self.background_color = '#0d0d0d'
        self.setup_ui()

    def setup_ui(self):
        back_button = ui.Button(title='< マップへ戻る')
        back_button.frame = (15, 15, 150, 30)
        back_button.tint_color = 'white'
        back_button.content_horizontal_alignment = 'left'
        back_button.action = self.back_action
        self.add_subview(back_button)

        title_label = ui.Label(text=f'【{self.shop.name}】運営画面', font=('<system-bold>', 20), text_color='white')
        title_label.size_to_fit()
        title_label.center = (self.width / 2, 40)
        self.add_subview(title_label)
        
        self.tab_control = ui.SegmentedControl(frame=(15, 80, self.width - 30, 32), flex='W')
        self.tab_control.segments = ['設備', 'スタッフ', 'メニュー']
        self.tab_control.action = self.tab_changed
        self.add_subview(self.tab_control)
        
        self.content_container = ui.View(frame=(0, 120, self.width, self.height - 120), flex='WH')
        self.add_subview(self.content_container)
        
        self.tab_changed(self.tab_control)

    def tab_changed(self, sender):
        selected_segment = sender.segments[sender.selected_index]
        for subview in list(self.content_container.subviews):
            self.content_container.remove_subview(subview)
        if selected_segment == '設備':
            self.show_equipment_view()
        elif selected_segment == 'スタッフ':
            self.show_staff_view()
        elif selected_segment == 'メニュー':
            self.show_menu_view()
            
    def show_equipment_view(self):
        for v in list(self.content_container.subviews): self.content_container.remove_subview(v)

        current_level_label = ui.Label(frame=(20, 20, 300, 20), text=f"現在の設備レベル: {self.shop.equipment_level}", text_color='white')
        self.content_container.add_subview(current_level_label)

        max_level = 5 
        if self.shop.equipment_level < max_level:
            upgrade_cost = self.shop.get_next_upgrade_cost()
            next_level_label = ui.Label(frame=(20, 50, 300, 20), text=f"次のレベルへのアップグレード費用: ¥{upgrade_cost:,.0f}", font=('<system>', 14), text_color='#AEAEB2')
            self.content_container.add_subview(next_level_label)
            upgrade_button = ui.Button(title='設備をアップグレードする', frame=(20, 90, 250, 44), background_color='#007AFF', tint_color='white', corner_radius=8, action=self.upgrade_equipment_action)
            self.content_container.add_subview(upgrade_button)
        else:
            max_level_label = ui.Label(frame=(20, 50, 300, 20), text="設備は既に最大レベルです。", font=('<system>', 14), text_color='#34C759')
            self.content_container.add_subview(max_level_label)

    def upgrade_equipment_action(self, sender):
        self.shop_handler.upgrade_equipment(self.shop)
        # 画面を更新するために再度呼び出す
        self.show_equipment_view()

    def show_staff_view(self):
        for v in list(self.content_container.subviews): self.content_container.remove_subview(v)

        current_staff_label = ui.Label(text='現在のスタッフ', font=('<system-bold>', 16), frame=(15, 10, 200, 20), text_color='white')
        self.content_container.add_subview(current_staff_label)
        
        current_staff_tv = ui.TableView(frame=(0, 40, self.content_container.width, 150), flex='W')
        current_staff_tv.data_source = StaffListDataSource(self.shop.staff_list, '解雇', self.handle_fire_staff_action)
        self.content_container.add_subview(current_staff_tv)
        
        candidates_label = ui.Label(text='雇用可能な候補者', font=('<system-bold>', 16), frame=(15, 200, 200, 20), text_color='white')
        self.content_container.add_subview(candidates_label)

        hired_names = {s.name for s in self.shop.staff_list}
        candidates = [c for c in constants.STAFF_CANDIDATES if c.name not in hired_names]
        
        candidates_tv = ui.TableView(frame=(0, 230, self.content_container.width, self.content_container.height - 240), flex='WH')
        candidates_tv.data_source = StaffListDataSource(candidates, '雇用', self.handle_hire_staff_action)
        self.content_container.add_subview(candidates_tv)

    def handle_hire_staff_action(self, sender):
        row = sender.row
        hired_names = {s.name for s in self.shop.staff_list}
        candidates = [c for c in constants.STAFF_CANDIDATES if c.name not in hired_names]
        
        if 0 <= row < len(candidates):
            self.shop_handler.hire_staff(self.shop, candidates[row])
    
    def handle_fire_staff_action(self, sender):
        row = sender.row
        if 0 <= row < len(self.shop.staff_list):
            self.shop_handler.fire_staff(self.shop, row)

    def show_menu_view(self):
        for v in list(self.content_container.subviews): self.content_container.remove_subview(v)
        
        current_menu_label = ui.Label(text='現在のメニュー', font=('<system-bold>', 16), frame=(15, 10, 200, 20), text_color='white')
        self.content_container.add_subview(current_menu_label)

        current_menu_tv = ui.TableView(frame=(0, 40, self.content_container.width, 150), flex='W')
        current_menu_tv.data_source = MenuListDataSource(self.shop.menu, '削除', self.handle_remove_menu_action)
        self.content_container.add_subview(current_menu_tv)
        
        addable_label = ui.Label(text='追加可能なメニュー', font=('<system-bold>', 16), frame=(15, 200, 200, 20), text_color='white')
        self.content_container.add_subview(addable_label)
        
        current_menu_names = {m.name for m in self.shop.menu}

        # --- ここからが修正箇所 ---
        # 辞書のリストではなく、MenuItemオブジェクトのリストを作成する
        addable_menus = [MenuItem(name=item['name'], price=item['price'], cost=item['cost']) for item in constants.AVAILABLE_MENU_ITEMS_MASTER_DATA if item['name'] not in current_menu_names]
        # --- ここまでが修正箇所 ---
        
        addable_menu_tv = ui.TableView(frame=(0, 230, self.content_container.width, self.content_container.height - 240), flex='WH')
        addable_menu_tv.data_source = MenuListDataSource(addable_menus, '追加', self.handle_add_menu_action)
        self.content_container.add_subview(addable_menu_tv)

    def handle_add_menu_action(self, sender):
        row = sender.row
        current_menu_names = {m.name for m in self.shop.menu}
        addable_menus = [MenuItem(name=item['name'], price=item['price'], cost=item['cost']) for item in constants.AVAILABLE_MENU_ITEMS_MASTER_DATA if item['name'] not in current_menu_names]
        if 0 <= row < len(addable_menus):
            self.shop_handler.add_menu_item(self.shop, addable_menus[row].__dict__)

    def handle_remove_menu_action(self, sender):
        row = sender.row
        if 0 <= row < len(self.shop.menu):
            self.shop_handler.remove_menu_item(self.shop, row)
            
    def back_action(self, sender):
        self.game_controller.show_city_view(self.shop.location_name)
