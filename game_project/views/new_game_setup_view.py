# views/new_game_setup_view.py
import ui

class NewGameSetupView(ui.View):
    """ニューゲームの設定画面"""
    def __init__(self, start_action, cancel_action, **kwargs):
        super().__init__(**kwargs)
        self.background_color = '#131A24'
        self.start_action = start_action
        self.cancel_action = cancel_action
        self.setup_ui()

    def setup_ui(self):
        # --- UI要素を配置 ---
        self.company_name_field = self.add_textfield_row('会社名:')
        self.competitors_segment = self.add_segmented_control_row('競合CPUの数:', ['3', '4', '5', '6', '7'], 2)
        self.difficulty_segment = self.add_segmented_control_row('難易度:', ['最弱', '簡単', '普通', '困難', '最恐'], 2)
        
        # --- ボタンを配置 ---
        self.add_bottom_buttons()

    def add_textfield_row(self, label_text, initial_text='マイカンパニー'):
        """ラベルとテキストフィールドの行を追加する"""
        last_y = self.get_last_view_y()
        row_view = ui.View(frame=(0, last_y + 30, self.width, 40), flex='W')
        
        label = ui.Label(text=label_text, frame=(20, 0, 110, 40), text_color='white', font=('<system>', 16))
        row_view.add_subview(label)
        
        textfield = ui.TextField(
            frame=(130, 5, row_view.width - 150, 30),
            placeholder=initial_text,
            text=initial_text,
            background_color='#3A3A3C',
            text_color='white',
            corner_radius=5,
            flex='W'
        )
        # ★★★ テキスト表示の不具合を修正 ★★★
        textfield.alignment = ui.ALIGN_LEFT
        textfield.bordered = False
        row_view.add_subview(textfield)
        self.add_subview(row_view)
        return textfield

    def add_segmented_control_row(self, label_text, segments, default_index):
        """ラベルとセグメントコントロールの行を追加する"""
        last_y = self.get_last_view_y()
        row_view = ui.View(frame=(0, last_y + 25, self.width, 40), flex='W')
        
        label = ui.Label(text=label_text, frame=(20, 0, 110, 40), text_color='white', font=('<system>', 16))
        row_view.add_subview(label)

        segment = ui.SegmentedControl(
            frame=(130, 5, row_view.width - 150, 30),
            segments=segments,
            flex='W'
        )
        segment.selected_index = default_index
        row_view.add_subview(segment)
        self.add_subview(row_view)
        return segment

    def add_bottom_buttons(self):
        """画面下部にボタンを配置する"""
        button_y = self.height - 80
        
        # キャンセルボタン
        cancel_button = ui.Button(title='キャンセル', corner_radius=8, font=('<system-bold>', 18))
        cancel_button.frame = (0, 0, 150, 44)
        cancel_button.center = (self.width * 0.28, button_y)
        cancel_button.background_color = '#555'
        cancel_button.tint_color = 'white'
        cancel_button.action = self.cancel_action
        cancel_button.flex = 'T'
        self.add_subview(cancel_button)
        
        # ゲーム開始ボタン
        start_button = ui.Button(title='ゲーム開始', corner_radius=8, font=('<system-bold>', 18))
        start_button.frame = (0, 0, 150, 44)
        start_button.center = (self.width * 0.72, button_y)
        start_button.background_color = '#34C759'
        start_button.tint_color = 'white'
        start_button.action = self.confirm_settings
        start_button.flex = 'T'
        self.add_subview(start_button)

    def get_last_view_y(self):
        """最後に追加されたUI要素の下端のY座標を取得する"""
        if not self.subviews:
            return 60
        return max(v.frame.max_y for v in self.subviews)

    def confirm_settings(self, sender):
        """設定を辞書にまとめて、コールバック関数を呼び出す"""
        settings = {
            'company_name': self.company_name_field.text or self.company_name_field.placeholder,
            'num_competitors': int(self.competitors_segment.segments[self.competitors_segment.selected_index]),
            'difficulty': self.difficulty_segment.selected_index + 1
        }
        self.start_action(settings)
