# views/trade_modal_view.py (修正版)
import ui
import console

class TradeModalView(ui.View):
    """株式の売買注文を行うモーダルビュー"""
    def __init__(self, investment_handler, stock, trade_type, owner_type, **kwargs):
        super().__init__(**kwargs)
        self.investment_handler = investment_handler
        self.game_controller = investment_handler.gc # メインコントローラーへの参照も保持
        self.stock = stock
        self.trade_type = trade_type 
        self.owner_type = owner_type
        
        self.background_color = (0, 0, 0, 0.7)
        self.setup_ui()

    def setup_ui(self):
        card_width = self.width * 0.9
        card_height = 320
        card = ui.View(frame=(0, 0, card_width, card_height), background_color='#2C2C2E', corner_radius=12)
        card.center = self.center
        card.flex = 'LRTB'
        self.add_subview(card)
        
        trade_type_str = "買い" if self.trade_type == 'buy' else "売り"
        owner_str = "会社" if self.owner_type == 'company' else "個人"
        title_text = f"{self.stock.company_name} ({trade_type_str}注文: {owner_str}資金)"
        
        title_label = ui.Label(text=title_text, font=('<system-bold>', 16), text_color='white', frame=(20, 20, card.width - 40, 22), alignment=ui.ALIGN_CENTER)
        card.add_subview(title_label)

        price_label = ui.Label(text=f"現在値: ¥{self.stock.current_price:,.2f}", font=('<system>', 14), text_color='#AEAEB2', frame=(20, 50, card.width - 40, 20), alignment=ui.ALIGN_CENTER)
        card.add_subview(price_label)

        y_pos = 100
        
        shares_label = ui.Label(text='株数:', frame=(20, y_pos, 80, 32), text_color='white')
        card.add_subview(shares_label)
        
        self.shares_field = ui.TextField(frame=(100, y_pos, card.width - 120, 32), placeholder='例: 100', keyboard_type=ui.KEYBOARD_NUMBER_PAD, background_color='#3A3A3C', text_color='white', corner_radius=5)
        self.shares_field.alignment = ui.ALIGN_LEFT
        self.shares_field.bordered = False
        card.add_subview(self.shares_field)
        
        y_pos += 35

        if self.trade_type == 'buy':
            player = self.game_controller.player
            cash = player.finance.get_cash() if self.owner_type == 'company' else player.money_personal
            
            max_buyable = 0
            if self.stock.current_price > 0:
                max_buyable = int(cash / self.stock.current_price)
            
            if max_buyable > 0:
                max_buy_label = ui.Label(
                    text=f'買付可能: {max_buyable:,.0f}株',
                    frame=(100, y_pos, card.width - 120, 20),
                    font=('<system>', 12),
                    text_color='#AEAEB2',
                    alignment=ui.ALIGN_RIGHT
                )
                card.add_subview(max_buy_label)
        
        y_pos += 50 
        
        confirm_btn = ui.Button(title='注文確定', frame=(20, y_pos, card.width - 40, 44), background_color='#007AFF', tint_color='white', corner_radius=8, font=('<system-bold>', 16))
        confirm_btn.action = self.confirm_trade
        card.add_subview(confirm_btn)

        y_pos += 50
        cancel_btn = ui.Button(title='キャンセル', frame=(20, y_pos, card.width - 40, 30), tint_color='gray')
        cancel_btn.action = lambda sender: self.close()
        card.add_subview(cancel_btn)

    def confirm_trade(self, sender):
        try:
            num_shares = int(self.shares_field.text)
            if num_shares <= 0: raise ValueError
        except (ValueError, TypeError):
            console.hud_alert('正しい株数を入力してください', 'error', 1)
            return
            
        # アクションの呼び出し先を investment_handler に変更
        self.investment_handler.execute_trade(self.stock, self.trade_type, self.owner_type, num_shares)
        self.close()

