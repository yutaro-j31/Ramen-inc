# views/game_view.py
import ui
import console

# --- 各タブのコンテンツViewをインポート ---
from .hq_view import HQView 
from .map_view import MapView
from .invest_view import InvestView 
from .assets_view import AssetsView

class NavButton(ui.View):
    """アイコンとラベルを組み合わせたナビゲーションボタン"""
    def __init__(self, image_name, text, action=None, **kwargs):
        super().__init__(**kwargs)
        self.action = action
        
        iv_height = 28
        label_height = 12
        padding_top = 5
        
        self.image_view = ui.ImageView(frame=(0, padding_top, self.width, iv_height))
        self.image_view.image = ui.Image.named(image_name)
        self.image_view.content_mode = ui.CONTENT_SCALE_ASPECT_FIT
        self.image_view.tint_color = '#8E8E93'
        self.image_view.flex = 'W'
        self.add_subview(self.image_view)
        
        self.label = ui.Label(frame=(0, self.image_view.y + iv_height, self.width, label_height))
        self.label.text = text
        self.label.font = ('<system>', 10)
        self.label.text_color = '#8E8E93'
        self.label.alignment = ui.ALIGN_CENTER
        self.label.flex = 'W'
        self.add_subview(self.label)
        
        tap_button = ui.Button(frame=self.bounds, action=self.button_tapped, flex='WH')
        self.add_subview(tap_button)

    def button_tapped(self, sender):
        if self.action:
            self.action(self)
            
    def set_selected(self, selected):
        color = '#007AFF' if selected else '#8E8E93'
        self.image_view.tint_color = color
        self.label.text_color = color

class GameUIView(ui.View):
    """メインゲーム画面の骨格となるView"""
    def __init__(self, game_controller, game_handler, hq_handler, investment_handler, map_handler, **kwargs):
        super().__init__(**kwargs)
        self.game_controller = game_controller
        self.game_handler = game_handler
        self.hq_handler = hq_handler
        self.investment_handler = investment_handler
        self.map_handler = map_handler
        self.background_color = '#000000'
        
        self.header = self.create_header()
        self.add_subview(self.header)
        
        self.nav_bar = self.create_nav_bar()
        self.add_subview(self.nav_bar)
        
        # --- コンテンツエリアのセットアップ ---
        self.content_views = {}
        self.current_content_view = None
        
        content_frame = self.get_content_frame()
        
        self.content_views['hq'] = HQView(self.game_controller, self.hq_handler, frame=content_frame, flex='WH')
        self.content_views['map'] = MapView(self.game_controller, self.map_handler, frame=content_frame, flex='WH')
        self.content_views['invest'] = InvestView(self.game_controller, self.investment_handler, frame=content_frame, flex='WH')
        self.content_views['assets'] = AssetsView(self.game_controller, frame=content_frame, flex='WH')

        # 初期タブを設定
        self.switch_tab('map')

    def get_content_frame(self):
        header_h = self.header.height
        nav_h = self.nav_bar.height
        return (0, header_h, self.width, self.height - header_h - nav_h)

    def create_header(self):
        header_height = 94 
        header = ui.View(frame=(0, 0, self.width, header_height), name='header', flex='W')
        header.background_color = '#1C1C1E'
        
        close_button = ui.Button(image=ui.Image.named('iob:close_round_24'))
        close_button.frame = (15, 54, 30, 30)
        close_button.tint_color = 'white'
        close_button.action = self.game_controller.exit_game
        header.add_subview(close_button)
        
        self.company_name_label = ui.Label(frame=(55, 54, 200, 30), text="マイカンパニー", font=('<system-bold>', 18), text_color='white')
        header.add_subview(self.company_name_label)
        
        self.cash_label = ui.Label(frame=(self.width - 215, 54, 200, 30), text="¥0", font=('<system-bold>', 18), text_color='#34C759', alignment=ui.ALIGN_RIGHT, flex='L')
        header.add_subview(self.cash_label)
        
        self.date_label = ui.Label(frame=(self.width - 215, 24, 200, 30), text="----年--月--週", font=('<system>', 14), text_color='#AEAEB2', alignment=ui.ALIGN_RIGHT, flex='L')
        header.add_subview(self.date_label)
        
        return header
        
    def create_nav_bar(self):
        nav_height = 83
        nav_bar = ui.View(frame=(0, self.height - nav_height, self.width, nav_height), name='nav_bar', flex='WT')
        nav_bar.background_color = '#1C1C1E'
        
        self.nav_buttons = []
        tab_items = [
            {'id': 'hq', 'icon': 'building.2.fill', 'text': '本社'},
            {'id': 'invest', 'icon': 'chart.bar.xaxis', 'text': '投資'},
            {'id': 'map', 'icon': 'map.fill', 'text': 'マップ'},
            {'id': 'assets', 'icon': 'person.crop.circle.fill', 'text': '資産'}
        ]
        
        tab_width = (self.width - 90) / len(tab_items)
        for i, item in enumerate(tab_items):
            btn = NavButton(item['icon'], item['text'], action=self.tab_tapped)
            btn.frame = (10 + i * tab_width, 0, tab_width, 50)
            btn.flex = 'L'
            btn.name = item['id']
            nav_bar.add_subview(btn)
            self.nav_buttons.append(btn)
            
        next_week_btn = ui.Button(title='週送り', frame=(self.width - 80, 8, 70, 36), background_color='#007AFF', tint_color='white', corner_radius=18, font=('<system-bold>', 14), action=self.game_handler.process_next_week, flex='L')
        nav_bar.add_subview(next_week_btn)
        
        return nav_bar

    def tab_tapped(self, sender):
        self.switch_tab(sender.name)
        
    def switch_tab(self, tab_id):
        for btn in self.nav_buttons:
            btn.set_selected(btn.name == tab_id)
        
        new_view = self.content_views.get(tab_id)
        if new_view:
            self.switch_content(new_view)
            
    def switch_content(self, new_view):
        if self.current_content_view:
            self.current_content_view.hidden = True
            
        if new_view:
            if new_view not in self.subviews:
                self.add_subview(new_view)
                new_view.send_to_back()
            
            new_view.hidden = False
            self.current_content_view = new_view
            
            if hasattr(new_view, 'update'):
                new_view.update()
                
    def update_view(self):
        if not self.game_controller.player: return
        
        player = self.game_controller.player
        game_time = self.game_controller.game_time
        
        self.company_name_label.text = player.company_name
        self.cash_label.text = f"¥{player.finance.get_cash():,.0f}"
        self.date_label.text = game_time.get_date_string()

        if self.current_content_view and hasattr(self.current_content_view, 'update'):
            self.current_content_view.update()
