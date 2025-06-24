# views/shop_list_view.py
import ui

class ShopListDataSource:
    """店舗リスト用のTableViewデータソース"""
    def __init__(self, items, action):
        self.items = items
        self.action = action

    def tableview_number_of_rows(self, tableview, section):
        return len(self.items)

    def tableview_cell_for_row(self, tableview, section, row):
        shop = self.items[row]
        cell = ui.TableViewCell('value1')
        cell.background_color = '#1C1C1E'
        cell.text_label.text_color = 'white'
        cell.detail_text_label.text_color = '#AEAEB2'
        
        cell.text_label.text = shop.name
        cell.detail_text_label.text = f"設備レベル: {shop.equipment_level} | スタッフ: {len(shop.staff_list)}名"
        cell.accessory_type = 'disclosure_indicator'
        return cell
        
    def tableview_did_select(self, tableview, section, row):
        if self.action:
            selected_shop = self.items[row]
            self.action(selected_shop)

class ShopListView(ui.View):
    """所有店舗の一覧画面"""
    def __init__(self, game_controller, shop_handler, **kwargs):
        super().__init__(**kwargs)
        self.game_controller = game_controller
        self.shop_handler = shop_handler
        self.background_color = '#0d0d0d'
        self.setup_ui()

    def setup_ui(self):
        back_button = ui.Button(title='< 本社画面へ戻る')
        back_button.frame = (15, 15, 150, 30)
        back_button.tint_color = 'white'
        back_button.content_horizontal_alignment = 'left'
        back_button.action = self.game_controller.show_hq_view
        self.add_subview(back_button)

        title_label = ui.Label(text='店舗一覧', font=('<system-bold>', 20), text_color='white')
        title_label.size_to_fit()
        title_label.center = (self.width / 2, 40)
        self.add_subview(title_label)
        
        shops = self.game_controller.player.ops.businesses_owned
        
        tv = ui.TableView(frame=(0, 70, self.width, self.height - 70), flex='WH')
        tv.row_height = 50
        tv.separator_color = '#333'
        # タップされたら、shop_handlerのshow_shop_managementメソッドを呼び出す
        data_source = ShopListDataSource(shops, self.shop_handler.show_shop_management)
        tv.data_source = data_source
        tv.delegate = data_source
        self.add_subview(tv)
