# views/title_view.py
import ui

class TitleView(ui.View):
    """タイトル画面の見た目を定義するクラス"""
    
    def __init__(self, new_game_action, load_game_action, exit_action, has_save_data=False, **kwargs):
        super().__init__(**kwargs)
        self.name = 'タイトル画面'
        self.background_color = '#131A24' # 深い青色の背景
        
        # --- アクション関数の保持 ---
        self.new_game_action = new_game_action
        self.load_game_action = load_game_action
        self.exit_action = exit_action
        
        # --- UIのセットアップ ---
        self.setup_ui(has_save_data)

    def setup_ui(self, has_save_data):
        # ゲームタイトルのラベル
        title_label = ui.Label(frame=(0, 0, self.width, 100))
        title_label.text = 'Ramen inc'
        title_label.font = ('<system-bold>', 36)
        title_label.text_color = 'white'
        title_label.alignment = ui.ALIGN_CENTER
        title_label.center = (self.width / 2, self.height * 0.3)
        title_label.flex = 'W'
        self.add_subview(title_label)
        
        # --- ボタンの作成 ---
        btn_width = 300
        btn_height = 50
        
        button_vertical_spacing = 20 # ボタン間の垂直方向の間隔

        # 1. 新しいビジネスの開始ボタン
        new_game_btn = self.create_main_button(
            title='新しいビジネスの開始',
            frame=(0, 0, btn_width, btn_height),
            action=self.new_game_action
        )
        new_game_btn.center = (self.width / 2, self.height * 0.5) # 気持ち上に移動
        self.add_subview(new_game_btn)

        # 2. 既存のビジネスを開くボタン
        load_game_btn_y = new_game_btn.frame.max_y + button_vertical_spacing
        load_game_btn = self.create_main_button(
            title='既存のビジネスを開く',
            frame=(0, load_game_btn_y, btn_width, btn_height),
            action=self.load_game_action
        )
        load_game_btn.center = (self.width / 2, load_game_btn_y + btn_height / 2)
        # セーブデータがない場合は非表示
        load_game_btn.hidden = not has_save_data
        self.add_subview(load_game_btn)

        # 3. 終了ボタン
        exit_btn = self.create_main_button(
            title='終了する',
            frame=(0, 0, btn_width, btn_height),
            action=self.exit_action,
            is_secondary=True
        )
        exit_btn.center = (self.width / 2, self.height - 100) # 少し下に移動し、他のボタンとの間隔を調整
        self.add_subview(exit_btn)

    def create_main_button(self, title, frame, action, is_secondary=False):
        """タイトル画面用のボタンを生成するヘルパーメソッド"""
        btn = ui.Button(frame=frame)
        btn.title = title
        btn.font = ('<system-bold>', 18)
        btn.corner_radius = 8
        btn.flex = 'W'
        
        if is_secondary:
            btn.background_color = '#4A4A4A'
            btn.tint_color = 'white'
        else:
            btn.background_color = '#E9C46A' # アクセントカラー
            btn.tint_color = '#264653'
        
        btn.action = action
        return btn

