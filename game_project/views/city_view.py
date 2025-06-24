# views/city_view.py
import ui
import console

class MapPointButton(ui.View):
    def __init__(self, point_data, action=None, **kwargs):
        super().__init__(**kwargs)
        self.action = action
        self.point_data = point_data
        
        icons = {
            'VACANT_SHOP': 'iob:ios7_cart_outline_32',
            'BANK': 'iob:social_usd_outline_32',
            'REAL_ESTATE': 'iob:ios7_home_outline_32',
            'SECURITIES': 'iob:arrow_graph_up_right_32'
        }
        icon_name = icons.get(point_data.point_type, 'iob:location_32')
        
        icon_view = ui.ImageView(frame=(0, 0, self.width, self.height - 15))
        icon_view.image = ui.Image.named(icon_name)
        icon_view.tint_color = 'white'
        icon_view.content_mode = ui.CONTENT_SCALE_ASPECT_FIT
        icon_view.flex = 'WH'
        self.add_subview(icon_view)
        
        label = ui.Label(frame=(0, self.height - 15, self.width, 15), text=point_data.name, font=('<system>', 9), text_color='white', alignment=ui.ALIGN_CENTER, flex='W')
        self.add_subview(label)
        
        tap_button = ui.Button(frame=self.bounds, action=self.button_tapped, flex='WH')
        self.add_subview(tap_button)
        
    def button_tapped(self, sender):
        if self.action:
            self.action(self)

class CityView(ui.View):
    """選択された都市(地方)の詳細マップを表示するクラス"""
    
    def __init__(self, map_handler, region, **kwargs):
        super().__init__(**kwargs)
        self.map_handler = map_handler
        self.game_controller = map_handler.gc
        self.region = region
        self.background_color = '#152532'
        self.setup_ui()

    def setup_ui(self):
        try:
            city_image = ui.ImageView(frame=self.bounds, flex='WH', image=ui.Image.named('img/city_background.png'), content_mode=ui.CONTENT_SCALE_TO_FILL)
            self.add_subview(city_image)
        except Exception as e:
            self.background_color = '#152532'
            print(f"警告: 地図画像 'img/city_background.png' が見つかりません。({e})")

        back_button = ui.Button(title='< 日本地図へ戻る', frame=(15, 15, 150, 30), tint_color='white', content_horizontal_alignment='left', action=self.back_action)
        self.add_subview(back_button)

        title_label = ui.Label(text=f'🏙️ {self.region.name}', font=('<system-bold>', 24), text_color='white', flex='W')
        title_label.size_to_fit()
        title_label.center = (self.width / 2, 40)
        self.add_subview(title_label)
        
        for point in self.region.map_points:
            coords = point.coordinates
            px = self.width * (coords[0] / 100.0)
            py = self.height * (coords[1] / 100.0)

            if point.point_type == 'OWNED_SHOP':
                shop_button = ui.Button(title=f'🏢 {point.name}', font=('<system-bold>', 12), background_color=(0.2, 0.6, 0.2, 0.8), tint_color='white', corner_radius=5, flex='LRTB')
                shop_button.size_to_fit()
                shop_button.width += 20
                shop_button.height += 10
                shop_button.center = (px, py)
                shop_button.name = point.name
                shop_button.action = self.map_point_tapped
                self.add_subview(shop_button)
            else:
                point_button = MapPointButton(point, action=self.map_point_tapped, frame=(0, 0, 80, 50), center=(px, py), flex='LRTB')
                self.add_subview(point_button)
                
    def map_point_tapped(self, sender):
        point_name = sender.name if isinstance(sender, ui.Button) else sender.point_data.name
        self.map_handler.show_map_point_details(self.region.name, point_name)

    def back_action(self, sender):
        self.game_controller.show_map_view()
