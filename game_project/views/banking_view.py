# views/banking_view.py
import ui
from systems import banking_system

class LoanListDataSource:
    def __init__(self, items, action):
        self.items = items
        self.action = action

    def tableview_number_of_rows(self, tableview, section):
        return len(self.items)

    def tableview_cell_for_row(self, tableview, section, row):
        cell = ui.TableViewCell('subtitle')
        product = self.items[row]
        rate_percent = product['customized_rate'] * 100
        
        cell.text_label.text = f"{product['bank_name']} - {product['product_name']}"
        cell.detail_text_label.text = f"最大融資額: ¥{product['customized_max_amount']:,.0f} | 週利: {rate_percent:.4f}%"
        cell.accessory_type = 'disclosure_indicator'
        return cell
        
    def tableview_did_select(self, tableview, section, row):
        if self.action:
            self.action(self.items[row])

class BankingView(ui.View):
    """銀行のメイン画面"""
    def __init__(self, game_controller, banking_handler, **kwargs):
        super().__init__(**kwargs)
        self.game_controller = game_controller
        self.banking_handler = banking_handler
        self.background_color = '#0d0d0d'
        self.setup_ui()

    def setup_ui(self):
        back_button = ui.Button(title='< マップへ戻る')
        back_button.frame = (15, 15, 150, 30)
        back_button.tint_color = 'white'
        back_button.content_horizontal_alignment = 'left'
        back_button.action = self.game_controller.show_city_view_from_child
        self.add_subview(back_button)

        title_label = ui.Label(text='銀行', font=('<system-bold>', 20), text_color='white')
        title_label.size_to_fit()
        title_label.center = (self.width / 2, 40)
        self.add_subview(title_label)
        
        player = self.game_controller.player
        credit_label = ui.Label(text=f"あなたの会社の信用格付け: {player.credit_rating} ({player.credit_rating_score})", font=('<system>', 14), text_color='#AEAEB2')
        credit_label.size_to_fit()
        credit_label.center = (self.width / 2, 70)
        self.add_subview(credit_label)
        
        # 融資商品リスト
        loan_products = banking_system.get_customized_loan_products(player)
        
        tv = ui.TableView(frame=(0, 100, self.width, self.height - 100), flex='WH')
        tv.row_height = 60
        data_source = LoanListDataSource(loan_products, self.banking_handler.show_take_loan_modal)
        tv.data_source = data_source
        tv.delegate = data_source
        self.add_subview(tv)
