# views/stock_detail_view.py
import ui

class StockDetailView(ui.View):
    """個別株の詳細情報を表示する画面"""
    def __init__(self, investment_handler, stock_obj, **kwargs):
        super().__init__(**kwargs)
        self.investment_handler = investment_handler
        self.game_controller = investment_handler.gc
        self.stock = stock_obj
        self.background_color = '#0d0d0d'
        self.setup_ui()

    def setup_ui(self):
        # --- ヘッダー ---
        back_button = ui.Button(title='< 株式市場へ戻る')
        back_button.frame = (15, 15, 150, 30)
        back_button.tint_color = 'white'
        back_button.content_horizontal_alignment = 'left'
        back_button.action = self.game_controller.show_stock_market_view
        self.add_subview(back_button)

        title_text = f"{self.stock.company_name} ({self.stock.ticker_symbol})"
        title_label = ui.Label(text=title_text, font=('<system-bold>', 20), text_color='white')
        title_label.size_to_fit()
        title_label.center = (self.width / 2, 40)
        self.add_subview(title_label)
        
        # --- 主要な財務指標 ---
        y_pos = 80
        stats = [
            (f"株価: ¥{self.stock.current_price:,.2f}", '#FFFFFF'),
            (f"時価総額: ¥{self.stock.market_cap:,.0f}", '#AEAEB2'),
            (f"PER: {self.stock.p_e_ratio:.2f}倍", '#AEAEB2'),
            (f"PBR: {self.stock.get_pbr_ratio():.2f}倍", '#AEAEB2')
        ]
        for i, (text, color) in enumerate(stats):
            label = ui.Label(text=text, font=('<system-bold>', 16 if i==0 else 14), text_color=color)
            label.frame = (20, y_pos + (i * 25), self.width-40, 20)
            self.add_subview(label)
        
        y_pos += len(stats) * 25 + 20
        
        # --- 売買ボタン ---
        buy_button = ui.Button(title='買い', background_color='#34C759', tint_color='white', font=('<system-bold>', 16), corner_radius=8)
        buy_button.frame = (20, y_pos, (self.width - 50)/2, 44)
        buy_button.action = lambda sender: self.investment_handler.show_trade_modal(self.stock, 'buy')
        self.add_subview(buy_button)
        
        sell_button = ui.Button(title='売り', background_color='#FF3B30', tint_color='white', font=('<system-bold>', 16), corner_radius=8)
        sell_button.frame = (buy_button.x + buy_button.width + 10, y_pos, (self.width - 50)/2, 44)
        sell_button.action = lambda sender: self.investment_handler.show_trade_modal(self.stock, 'sell')
        self.add_subview(sell_button)
