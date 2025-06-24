# views/venture_market_view.py
import ui
from systems import venture_system

class VentureDealDataSource:
    """ベンチャー投資案件リスト用のデータソース"""
    def __init__(self, items_dict, action):
        self.section_titles = list(items_dict.keys())
        self.items_dict = items_dict
        self.action = action

    def tableview_number_of_sections(self, tableview):
        return len(self.section_titles)

    def tableview_title_for_header(self, tableview, section):
        return self.section_titles[section]
        
    def tableview_number_of_rows(self, tableview, section):
        section_title = self.section_titles[section]
        return len(self.items_dict[section_title])

    def tableview_cell_for_row(self, tableview, section, row):
        cell = ui.TableViewCell('subtitle')
        cell.background_color = '#1C1C1E'
        cell.text_label.text_color = 'white'
        cell.detail_text_label.text_color = '#AEAEB2'
        
        section_title = self.section_titles[section]
        deal = self.items_dict[section_title][row]
        
        cell.text_label.text = f"{deal['company_name']} ({deal['sector']})"
        cell.detail_text_label.text = f"ラウンド: {deal['growth_stage']} | 要求額: ¥{deal['investment_amount_required']:,}"
        cell.accessory_type = 'disclosure_indicator'
        return cell
        
    def tableview_did_select(self, tableview, section, row):
        if self.action:
            section_title = self.section_titles[section]
            deal = self.items_dict[section_title][row]
            self.action(deal)

class VentureMarketView(ui.View):
    """ベンチャーキャピタル市場の画面"""
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

        title_label = ui.Label(text='ベンチャー投資市場', font=('<system-bold>', 20), text_color='white')
        title_label.size_to_fit()
        title_label.center = (self.width / 2, 40)
        self.add_subview(title_label)
        
        # 案件データを取得・分類
        deals = {
            "【要対応】追加投資ラウンド": venture_system.get_deals_seeking_follow_on(self.game_controller.player),
            "新規投資案件": venture_system.get_available_deals_for_market()
        }
        
        tv = ui.TableView(frame=(0, 70, self.width, self.height - 70), flex='WH')
        tv.row_height = 60
        tv.separator_color = '#333'
        tv.data_source = VentureDealDataSource(deals, self.game_controller.show_venture_deal_view)
        tv.delegate = tv.data_source
        self.add_subview(tv)
