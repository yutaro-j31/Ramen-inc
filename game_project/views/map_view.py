# views/map_view.py (修正版)
import ui
import console

class MapView(ui.View):
    """「マップ」タブで表示される地方選択画面"""
    def __init__(self, game_controller, map_handler, **kwargs):
        super().__init__(**kwargs)
        self.game_controller = game_controller
        self.map_handler = map_handler
        self.background_color = '#0d0d0d'
        self.update()

    def update(self):
        for subview in list(self.subviews):
            self.remove_subview(subview)
        
        try:
            map_image = ui.ImageView(frame=self.bounds, flex='WH')
            map_image.image = ui.Image.named('img/map_japan.png')
            map_image.content_mode = ui.CONTENT_SCALE_ASPECT_FIT
            self.add_subview(map_image)
        except Exception as e:
            self.background_color = '#1C2630'
            print(f"警告: 地図画像 'img/map_japan.png' が見つかりません。({e})")

        region_coords = {
            '札幌': (0.55, 0.31), '仙台': (0.77, 0.40),
            '東京': (0.75, 0.53), '名古屋': (0.65, 0.60),
            '大阪': (0.50, 0.60), '広島': (0.45, 0.65),
            '福岡': (0.25, 0.53)
        }
        regions = self.game_controller.game_regions

        for region in regions:
            coords = region_coords.get(region.name)
            if coords:
                btn = ui.Button(title=f'  {region.name}  ')
                btn.size_to_fit() 
                btn.center = (self.width * coords[0], self.height * coords[1])
                btn.flex = 'LRTB' 
                btn.background_color = (0.1, 0.1, 0.1, 0.75)
                btn.tint_color = 'white'
                btn.corner_radius = btn.height / 2 
                btn.border_color = '#007AFF'
                btn.border_width = 1
                btn.name = region.name
                btn.action = self.region_button_tapped
                self.add_subview(btn)
                
    def region_button_tapped(self, sender):
        # 画面遷移は game_controller が担当
        self.game_controller.show_city_view(sender.name)

