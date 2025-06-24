# views/action_modal_view.py
import ui

class ActionModalView(ui.View):
    """詳細情報の表示とアクションボタンを持つ汎用モーダルビュー"""
    def __init__(self, title, details, actions, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0.7) # 半透明の黒
        self.actions = actions # [{'title': 'ボタン名', 'action': 呼び出す関数}, ...]
        self.setup_ui(title, details)

    def setup_ui(self, title, details):
        # カード部分
        card_height = 150 + len(details) * 25 + len(self.actions) * 50
        card_width = self.width * 0.85
        card = ui.View(frame=(0, 0, card_width, card_height), background_color='#2C2C2E', corner_radius=12)
        card.center = self.center
        card.flex = 'LRTB'
        self.add_subview(card)
        
        # 閉じるボタン
        close_button = ui.Button(image=ui.Image.named('iob:close_round_24'), tint_color='gray')
        close_button.frame = (card.width - 40, 10, 30, 30)
        close_button.action = lambda sender: self.close()
        card.add_subview(close_button)
        
        # タイトル
        title_label = ui.Label(text=title, font=('<system-bold>', 18), text_color='white')
        title_label.frame = (20, 20, card.width - 60, 22)
        card.add_subview(title_label)
        
        # 詳細情報のラベル
        y_pos = 60
        for detail_text in details:
            detail_label = ui.Label(text=detail_text, font=('<system>', 14), text_color='#E5E5EA')
            detail_label.frame = (20, y_pos, card.width - 40, 20)
            card.add_subview(detail_label)
            y_pos += 25
            
        # アクションボタン
        y_pos += 20
        for item in self.actions:
            btn = ui.Button(title=item['title'], font=('<system-bold>', 16), corner_radius=8)
            btn.frame = (20, y_pos, card.width - 40, 44)
            btn.background_color = item.get('bg_color', '#007AFF')
            btn.tint_color = item.get('tint_color', 'white')
            btn.action = item['action']
            card.add_subview(btn)
            y_pos += 54
