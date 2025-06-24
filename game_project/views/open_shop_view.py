# views/open_shop_view.py
import ui
import console

class OpenShopView(ui.View):
    """新規出店のための情報入力ビュー"""
    def __init__(self, map_handler, point, setup_cost, **kwargs):
        super().__init__(**kwargs)
        self.map_handler = map_handler
        self.point = point
        self.setup_cost = setup_cost
        
        self.background_color = (0, 0, 0, 0.7)
        self.setup_ui()

    def setup_ui(self):
        card_height = 320
        card_width = self.width * 0.9
        card = ui.View(frame=(0, 0, card_width, card_height), background_color='#2C2C2E', corner_radius=12)
        card.center = self.center
        card.flex = 'LRTB'
        self.add_subview(card)
        
        close_button = ui.Button(image=ui.Image.named('iob:close_round_24'), tint_color='gray')
        close_button.frame = (card.width - 40, 10, 30, 30)
        close_button.action = lambda sender: self.close()
        card.add_subview(close_button)
        
        title_label = ui.Label(text=f'{self.point.name}に出店', font=('<system-bold>', 18), text_color='white', frame=(20, 20, card.width - 40, 22), alignment=ui.ALIGN_CENTER)
        card.add_subview(title_label)
        
        cost_label = ui.Label(text=f'出店費用: ¥{self.setup_cost:,.0f}', font=('<system>', 14), text_color='#AEAEB2', frame=(20, 50, card.width - 40, 20), alignment=ui.ALIGN_CENTER)
        card.add_subview(cost_label)
        
        y_pos = 90
        
        shop_name_label = ui.Label(text='店名:', frame=(20, y_pos, 80, 32), text_color='white', alignment=ui.ALIGN_LEFT)
        card.add_subview(shop_name_label)
        
        self.shop_name_field = ui.TextField(frame=(110, y_pos, card.width - 130, 32), placeholder='例: ミライラーメン渋谷店', background_color='#3A3A3C', text_color='white', corner_radius=5)
        self.shop_name_field.alignment = ui.ALIGN_LEFT
        self.shop_name_field.bordered = False
        card.add_subview(self.shop_name_field)
        
        y_pos += 45

        capital_label = ui.Label(text='初期運転資金:', frame=(20, y_pos, 100, 32), text_color='white', alignment=ui.ALIGN_LEFT)
        card.add_subview(capital_label)
        
        self.capital_field = ui.TextField(frame=(130, y_pos, card.width - 150, 32), placeholder='例: 50000000', keyboard_type=ui.KEYBOARD_NUMBER_PAD, background_color='#3A3A3C', text_color='white', corner_radius=5)
        self.capital_field.alignment = ui.ALIGN_LEFT
        self.capital_field.bordered = False
        card.add_subview(self.capital_field)
        
        y_pos += 70

        confirm_btn = ui.Button(title='出店確定', frame=(20, y_pos, card.width - 40, 44), background_color='#34C759', tint_color='white', corner_radius=8, font=('<system-bold>', 16))
        confirm_btn.action = self.confirm_tapped
        card.add_subview(confirm_btn)

        y_pos += 50
        cancel_btn = ui.Button(title='キャンセル', frame=(20, y_pos, card.width - 40, 30), tint_color='gray')
        cancel_btn.action = lambda sender: self.close()
        card.add_subview(cancel_btn)

    def confirm_tapped(self, sender):
        shop_name = self.shop_name_field.text
        try:
            initial_capital = int(self.capital_field.text or 0)
        except (ValueError, TypeError):
            initial_capital = 0
        
        if not shop_name:
            console.hud_alert('店舗名を入力してください', 'error', 1)
            return
            
        self.map_handler.open_shop_action(self.point, shop_name, initial_capital)
        self.close()
