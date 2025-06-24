# views/ma_market_view.py
import ui
from systems import acquisition_system

class MATargetListDataSource:
    """M&Aターゲットリスト用のTableViewデータソース"""
    def __init__(self, items, action):
        self.items = items
        self.action = action

    def tableview_number_of_rows(self, tableview, section):
        return len(self.items)

    def tableview_cell_for_row(self, tableview, section, row):
        cell = ui.TableViewCell('value1')
        cell.background_color = '#1C1C1E'
        cell.text_label.text_color = 'white'
        cell.detail_text_label.text_color = '#AEAEB2'
        
        company = self.items[row]
        
        cell.text_label.text = company.name
        cell.detail_text_label.text = f"業種: {company.industry} | 推定年商: ¥{company.estimated_annual_revenue:,.0f}"
        cell.accessory_type = 'disclosure_indicator'
        return cell
        
    def tableview_did_select(self, tableview, section, row):
        if self.action:
            self.action(self.items[row])

class MAMarketView(ui.View):
    """非上場M&A市場の画面"""
    def __init__(self, game_controller, **kwargs):
        super().__init__(**kwargs)
        self.game_controller = game_controller
        self.background_color = '#0d0d0d'
        self.setup_ui()

    def setup_ui(self):
        back_button = ui.Button(title='< 投資トップへ戻る')
        back_button.frame = (15, 15, 150, 30)
        back_button.tint_color = 'white'
        back_button.content_horizontal_alignment = 'left'
        back_button.action = self.game_controller.show_invest_view
        self.add_subview(back_button)

        title_label = ui.Label(text='非上場 M&A 市場', font=('<system-bold>', 20), text_color='white')
        title_label.size_to_fit()
        title_label.center = (self.width / 2, 40)
        self.add_subview(title_label)
        
        # 買収ターゲットリストを取得
        targets = acquisition_system.get_private_acquisition_targets(self.game_controller.player, self.game_controller.game_time)

        if not targets:
            info_label = ui.Label(text='現在、市場に案件はありません。', font=('<system>', 16), text_color='#8E8E93', alignment=ui.ALIGN_CENTER)
            info_label.frame = (0, 0, self.width, self.height)
            self.add_subview(info_label)
            return
            
        tv = ui.TableView(frame=(0, 70, self.width, self.height - 70), flex='WH')
        tv.row_height = 50
        tv.separator_color = '#333'
        tv.data_source = MATargetListDataSource(targets, self.game_controller.show_ma_deal_view)
        tv.delegate = tv.data_source
        self.add_subview(tv)

