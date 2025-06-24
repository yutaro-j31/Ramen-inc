# views/establish_hq_view.py
import ui
import constants

class EstablishHQView(ui.View):
    """本部設立の選択肢(賃貸/購入)を表示するモーダルビュー"""
    def __init__(self, rent_action, build_action, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0.7)
        
        # --- UIのセットアップ ---
        card = ui.View(frame=(0, 0, self.width * 0.9, 320), background_color='#2C2C2E', corner_radius=12)
        card.center = self.center
        card.flex = 'LRTB'
        self.add_subview(card)

        title = ui.Label(text='本部を設立する', font=('<system-bold>', 20), alignment=ui.ALIGN_CENTER, text_color='white')
        title.frame = (0, 20, card.width, 24)
        card.add_subview(title)

        # --- 賃貸オフィスの選択肢 ---
        rent_cost = constants.HQ_RENTED_INITIAL_COST
        rent_weekly = constants.HQ_RENTED_WEEKLY_RENT
        rent_btn = ui.Button(title='賃貸オフィスを契約', font=('<system-bold>', 16), background_color='#007AFF', tint_color='white', corner_radius=8)
        rent_btn.frame = (20, 70, card.width - 40, 44)
        rent_btn.action = rent_action
        card.add_subview(rent_btn)
        rent_label = ui.Label(text=f'初期費用: ¥{rent_cost:,.0f}\n週次コスト: ¥{rent_weekly:,.0f}', font=('<system>', 12), text_color='#AEAEB2', alignment=ui.ALIGN_CENTER, number_of_lines=2)
        rent_label.frame = (20, 115, card.width - 40, 30)
        card.add_subview(rent_label)
        
        # --- 自社ビル建設の選択肢 ---
        build_cost = constants.HQ_OWNED_CONSTRUCTION_COST
        build_btn = ui.Button(title='自社ビルを建設', font=('<system-bold>', 16), background_color='#34C759', tint_color='white', corner_radius=8)
        build_btn.frame = (20, 165, card.width - 40, 44)
        build_btn.action = build_action
        card.add_subview(build_btn)
        build_label = ui.Label(text=f'建設費用: ¥{build_cost:,.0f}\n(週次コストなし)', font=('<system>', 12), text_color='#AEAEB2', alignment=ui.ALIGN_CENTER, number_of_lines=2)
        build_label.frame = (20, 210, card.width - 40, 30)
        card.add_subview(build_label)

        # --- キャンセルボタン ---
        cancel_btn = ui.Button(title='キャンセル', tint_color='gray')
        cancel_btn.frame = (20, 270, card.width - 40, 30)
        cancel_btn.action = lambda sender: self.close()
        card.add_subview(cancel_btn)

