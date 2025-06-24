# views/take_loan_view.py
import ui
import console

class TakeLoanView(ui.View):
    """融資申込の専用モーダルビュー"""
    def __init__(self, loan_product, confirm_action, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0.7)
        self.loan_product = loan_product
        self.confirm_action = confirm_action
        self.setup_ui()

    def setup_ui(self):
        card_width = self.width * 0.9
        card_height = 350
        card = ui.View(frame=(0, 0, card_width, card_height), background_color='#2C2C2E', corner_radius=12)
        card.center = self.center
        card.flex = 'LRTB'
        self.add_subview(card)
        
        # タイトル
        title_text = f"{self.loan_product['product_name']} 申込"
        title_label = ui.Label(text=title_text, font=('<system-bold>', 18), text_color='white', frame=(20, 20, card.width - 40, 22), alignment=ui.ALIGN_CENTER)
        card.add_subview(title_label)

        # ローン詳細
        details = [
            f"銀行名: {self.loan_product['bank_name']}",
            f"最大融資額: ¥{self.loan_product['customized_max_amount']:,.0f}",
            f"週利: {self.loan_product['customized_rate']*100:.4f}%",
            f"返済期間: {self.loan_product['repayment_weeks']}週"
        ]
        y_pos = 60
        for text in details:
            detail_label = ui.Label(text=text, font=('<system>', 14), text_color='#AEAEB2', frame=(20, y_pos, card.width - 40, 20))
            card.add_subview(detail_label)
            y_pos += 22

        y_pos += 15
        # 金額入力
        amount_label = ui.Label(text='融資希望額:', frame=(20, y_pos, 100, 32), text_color='white')
        card.add_subview(amount_label)
        
        self.amount_field = ui.TextField(frame=(130, y_pos, card.width - 150, 32), placeholder='金額を入力', keyboard_type=ui.KEYBOARD_NUMBER_PAD, background_color='#3A3A3C', text_color='white', corner_radius=5)
        self.amount_field.alignment = ui.ALIGN_LEFT
        self.amount_field.bordered = False
        card.add_subview(self.amount_field)
        
        y_pos += 60
        # 申込ボタン
        confirm_btn = ui.Button(title='この条件で申し込む', frame=(20, y_pos, card.width - 40, 44), background_color='#007AFF', tint_color='white', corner_radius=8, font=('<system-bold>', 16))
        confirm_btn.action = self.confirm_tapped
        card.add_subview(confirm_btn)
        
        y_pos += 50
        cancel_btn = ui.Button(title='キャンセル', frame=(20, y_pos, card.width - 40, 30), tint_color='gray')
        cancel_btn.action = lambda sender: self.close()
        card.add_subview(cancel_btn)

    def confirm_tapped(self, sender):
        try:
            amount = int(self.amount_field.text)
            if amount <= 0: raise ValueError
        except (ValueError, TypeError):
            console.hud_alert('正しい金額を入力してください', 'error', 1)
            return
        
        self.confirm_action(amount)
        self.close()
