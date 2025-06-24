# views/select_owner_view.py
import ui

class SelectOwnerView(ui.View):
    """取引の主体(会社/個人)を選択するモーダルビュー"""
    def __init__(self, select_action, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0.7)
        self.select_action = select_action # 'company' or 'personal' を引数に取る関数
        self.setup_ui()

    def setup_ui(self):
        card = ui.View(frame=(0, 0, self.width * 0.8, 250), background_color='#2C2C2E', corner_radius=12)
        card.center = self.center
        card.flex = 'LRTB'
        self.add_subview(card)

        title = ui.Label(text='どちらの資金で取引しますか?', font=('<system-bold>', 18), alignment=ui.ALIGN_CENTER, text_color='white')
        title.frame = (0, 20, card.width, 24)
        card.add_subview(title)
        
        btn_width = card.width - 40
        
        company_btn = ui.Button(title='会社資金', font=('<system-bold>', 16), background_color='#007AFF', tint_color='white', corner_radius=8)
        company_btn.frame = (20, 70, btn_width, 44)
        company_btn.action = self.select_company
        card.add_subview(company_btn)

        personal_btn = ui.Button(title='個人資産', font=('<system-bold>', 16), background_color='#3A3A3C', tint_color='white', corner_radius=8)
        personal_btn.frame = (20, 125, btn_width, 44)
        personal_btn.action = self.select_personal
        card.add_subview(personal_btn)

        cancel_btn = ui.Button(title='キャンセル', tint_color='gray')
        cancel_btn.frame = (20, 190, btn_width, 30)
        cancel_btn.action = lambda sender: self.close()
        card.add_subview(cancel_btn)

    def select_company(self, sender):
        self.select_action('company')
        self.close()
        
    def select_personal(self, sender):
        self.select_action('personal')
        self.close()
