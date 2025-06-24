# views/stock_market_view.py (リファクタリング対応版)
import ui
from collections import defaultdict
from systems import general_stock_market_system

class StockListDataSource:
    """セクション分けされた株式リスト用のデータソース"""
    def __init__(self, section_data, section_titles, action):
        self.section_data = section_data
        self.section_titles = section_titles
        self.action = action

    def tableview_number_of_sections(self, tableview):
        return len(self.section_titles)

    def tableview_title_for_header(self, tableview, section):
        return self.section_titles[section]
        
    def tableview_number_of_rows(self, tableview, section):
        section_title = self.section_titles[section]
        return len(self.section_data.get(section_title, []))

    def tableview_cell_for_row(self, tableview, section, row):
        cell = ui.TableViewCell('value1')
        section_title = self.section_titles[section]
        stock = self.section_data[section_title][row]
        
        cell.text_label.text = f"{stock.company_name} ({stock.ticker_symbol})"
        cell.text_label.font = ('<system-bold>', 16)
        cell.detail_text_label.text = f"¥{stock.current_price:,.2f}"
        cell.accessory_type = 'disclosure_indicator'
        return cell

    def tableview_did_select(self, tableview, section, row):
        if self.action:
            section_title = self.section_titles[section]
            selected_stock = self.section_data[section_title][row]
            self.action(selected_stock.ticker_symbol)

class StockMarketView(ui.View):
    """上場企業一覧を表示する画面"""
    def __init__(self, investment_handler, **kwargs):
        super().__init__(**kwargs)
        # --- 重要な修正箇所 ---
        # このViewのアクションは investment_handler が担当
        self.investment_handler = investment_handler
        # 画面遷移など、全体に関わる命令は、ハンドラ経由でメインコントローラー(gc)に依頼
        self.game_controller = investment_handler.gc
        # --- ここまで ---
        
        self.background_color = '#0d0d0d'
        self.setup_ui()

    def setup_ui(self):
        back_button = ui.Button(title='< 投資トップへ戻る', frame=(15, 15, 150, 30), tint_color='white', content_horizontal_alignment='left')
        # 画面遷移なので、game_controller のメソッドを呼び出す
        back_button.action = self.game_controller.show_invest_view
        self.add_subview(back_button)
        
        title_label = ui.Label(text='株式市場', font=('<system-bold>', 20), text_color='white')
        title_label.size_to_fit()
        title_label.center = (self.width / 2, 40)
        self.add_subview(title_label)

        # データを業種別にグループ化
        grouped_stocks = defaultdict(list)
        for stock in general_stock_market_system.listed_companies_on_market:
            grouped_stocks[stock.sector].append(stock)
        
        for sector in grouped_stocks:
            grouped_stocks[sector].sort(key=lambda s: s.ticker_symbol)
            
        sorted_sectors = sorted(grouped_stocks.keys())
        
        # TableViewの作成
        tv = ui.TableView(frame=(0, 70, self.width, self.height - 70), flex='WH')
        tv.row_height = 50
        tv.separator_color = '#333'
        
        # 詳細画面への遷移なので、game_controller のメソッドを渡す
        data_source = StockListDataSource(grouped_stocks, sorted_sectors, self.game_controller.show_stock_detail_view)
        tv.data_source = data_source
        tv.delegate = data_source 
        
        self.add_subview(tv)

