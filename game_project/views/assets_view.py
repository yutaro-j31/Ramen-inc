# views/assets_view.py
import ui
from systems import general_stock_market_system
from .portfolio_data_source import PortfolioDataSource # ★★★ 変更点 ★★★

class AssetsView(ui.View):
    """個人資産タブ画面"""
    def __init__(self, game_controller, **kwargs):
        super().__init__(**kwargs)
        self.game_controller = game_controller
        self.background_color = '#0d0d0d'
    
    def did_load(self):
        self.update()

    def update(self):
        for v in list(self.subviews): self.remove_subview(v)

        title = ui.Label(text='個人資産ポートフォリオ', font=('<system-bold>', 24), text_color='white')
        title.size_to_fit()
        title.center = (self.width / 2, 40)
        self.add_subview(title)
        
        tv_container = ui.View(frame=(0, 80, self.width, self.height - 80), flex='WH')
        self.add_subview(tv_container)

        portfolio = self.game_controller.player.personal_portfolio
        market_data = general_stock_market_system.listed_companies_on_market
        
        tv = ui.TableView(frame=tv_container.bounds, flex='WH')
        tv.row_height = 60
        tv.separator_color = '#333'
        tv.data_source = PortfolioDataSource(portfolio, market_data)
        tv_container.add_subview(tv)
