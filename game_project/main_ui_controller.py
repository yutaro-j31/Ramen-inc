# main_ui_controller.py (完全版)
import ui
import console
import dialogs
import unicodedata
import traceback

# --- UI画面のビューをインポート ---
from views.title_view import TitleView
from views.new_game_setup_view import NewGameSetupView
from views.game_view import GameUIView
from views.city_view import CityView
from views.action_modal_view import ActionModalView
from views.open_shop_view import OpenShopView
from views.shop_management_view import ShopManagementView
from views.shop_list_view import ShopListView
from views.establish_hq_view import EstablishHQView
from views.rnd_view import RNDView
from views.cxo_management_view import CXOManagementView
from views.invest_view import InvestView
from views.stock_market_view import StockMarketView
from views.stock_detail_view import StockDetailView
from views.trade_modal_view import TradeModalView
from views.select_owner_view import SelectOwnerView
from views.banking_view import BankingView
from views.take_loan_view import TakeLoanView
from views.ma_market_view import MAMarketView
from views.ma_deal_view import MADealView
from views.venture_market_view import VentureMarketView
from views.venture_deal_view import VentureDealView

# --- ゲームロジックのクラスとシステムをインポート ---
from models.player import Player
from models.game_time import GameTime
import constants
from systems import (
    save_load_system, map_system, general_stock_market_system, 
    competitor_ai_system, hr_system, venture_system, acquisition_system
)
# --- ハンドラをインポート ---
from handlers.game_handler import GameActionHandler
from handlers.map_handler import MapActionHandler
from handlers.hq_handler import HQActionHandler
from handlers.investment_handler import InvestmentActionHandler
from handlers.banking_handler import BankingActionHandler
from handlers.shop_handler import ShopActionHandler


class MainUIController:
    """UI全体の画面遷移やアクションを管理する司令塔クラス"""
    
    def __init__(self):
        w, h = ui.get_screen_size()
        self.root_view = ui.View(frame=(0, 0, w, h), name='root')
        self.root_view.present('fullscreen', hide_title_bar=True, animated=False)
        
        self.player = None
        self.game_time = None
        self.game_regions = []
        self.setup_view = None
        
        # --- ハンドラをインスタンス化 ---
        self.game_handler = GameActionHandler(self)
        self.map_handler = MapActionHandler(self)
        self.hq_handler = HQActionHandler(self)
        self.investment_handler = InvestmentActionHandler(self)
        self.banking_handler = BankingActionHandler(self)
        self.shop_handler = ShopActionHandler(self)
        
        self.show_title_screen()

    # --- 画面表示/遷移メソッド ---
    def show_title_screen(self):
        for v in list(self.root_view.subviews):
            self.root_view.remove_subview(v)
        has_save = save_load_system.has_save_data()
        title_view = TitleView(new_game_action=self.show_new_game_setup, load_game_action=self.load_game, exit_action=self.exit_game, has_save_data=has_save, frame=self.root_view.bounds, flex='WH')
        self.root_view.add_subview(title_view)

    def show_new_game_setup(self, sender):
        if self.setup_view and self.setup_view.on_screen:
            return
        self.setup_view = NewGameSetupView(start_action=self.confirm_new_game_settings, cancel_action=self.close_modal_view, frame=self.root_view.bounds)
        self.setup_view.present('sheet')

    def confirm_new_game_settings(self, settings):
        if self.setup_view:
            self.setup_view.close()
        console.hud_alert('ゲームデータを初期化中...', 'success', 2.0)
        self.player = Player(company_name=settings['company_name'], initial_personal_money=constants.INITIAL_PERSONAL_MONEY, initial_company_money=constants.INITIAL_COMPANY_MONEY)
        self.game_time = GameTime(start_year=2025, start_month=6, start_week=2)
        
        self.game_regions = map_system.initialize_map()
        hr_system.refresh_cxo_candidate_market(self.game_time)
        general_stock_market_system.initialize_general_stock_market(constants.NUMBER_OF_LISTED_COMPANIES, self.game_time.current_year)
        competitor_ai_system.initialize_competitors(settings['num_competitors'], settings['difficulty'], self.game_time)
        
        self.show_game_screen()
        
    def show_game_screen(self):
        for v in list(self.root_view.subviews):
            self.root_view.remove_subview(v)
        game_view = GameUIView(
            game_controller=self, 
            game_handler=self.game_handler, 
            hq_handler=self.hq_handler, 
            investment_handler=self.investment_handler, 
            map_handler=self.map_handler,
            frame=self.root_view.bounds, flex='WH'
        )
        self.root_view.add_subview(game_view)
        game_view.update_view()

    def show_map_view(self):
        self.root_view.subviews[0].switch_tab('map')
        
    def show_city_view(self, region_name):
        target_region = next((r for r in self.game_regions if r.name == region_name), None)
        if target_region:
            game_view = self.root_view.subviews[0]
            city_view = CityView(self.map_handler, target_region, frame=game_view.get_content_frame(), flex='WH')
            game_view.switch_content(city_view)
        else:
            console.hud_alert(f'エラー: {region_name}のデータが見つかりません', 'error', 1)

    def show_city_view_from_child(self, sender):
        if self.player.ops.businesses_owned:
            last_shop_location = self.player.ops.businesses_owned[-1].location_name
            self.show_city_view(last_shop_location)
        else:
            self.show_map_view()

    def show_hq_view(self):
        self.root_view.subviews[0].switch_tab('hq')

    def show_invest_view(self, sender=None):
        self.root_view.subviews[0].switch_tab('invest')
        
    def show_shop_list_view(self, sender):
        """店舗一覧画面を表示する"""
        game_view = self.root_view.subviews[0]
        shop_list_v = ShopListView(self, self.shop_handler, frame=game_view.get_content_frame(), flex='WH')
        game_view.switch_content(shop_list_v)
        
    def show_shop_management_view(self, shop_object):
        if not shop_object:
            console.hud_alert('エラー: 店舗オブジェクトが見つかりません', 'error', 1)
            return
        game_view = self.root_view.subviews[0]
        shop_view = ShopManagementView(self.shop_handler, shop_object, frame=game_view.get_content_frame(), flex='WH')
        game_view.switch_content(shop_view)
        
    def show_cxo_management_view(self, sender):
        game_view = self.root_view.subviews[0]
        cxo_view = CXOManagementView(self.hq_handler, frame=game_view.get_content_frame(), flex='WH')
        game_view.switch_content(cxo_view)

    def show_rnd_management_view(self, sender):
        game_view = self.root_view.subviews[0]
        rnd_view = RNDView(self.hq_handler, frame=game_view.get_content_frame(), flex='WH')
        game_view.switch_content(rnd_view)
    
    def show_stock_market_view(self, sender=None):
        game_view = self.root_view.subviews[0]
        stock_market_v = StockMarketView(self.investment_handler, frame=game_view.get_content_frame(), flex='WH')
        game_view.switch_content(stock_market_v)

    def show_stock_detail_view(self, ticker_symbol):
        target_stock = next((s for s in general_stock_market_system.listed_companies_on_market if s.ticker_symbol == ticker_symbol), None)
        if target_stock:
            game_view = self.root_view.subviews[0]
            stock_detail_v = StockDetailView(self.investment_handler, target_stock, frame=game_view.get_content_frame(), flex='WH')
            game_view.switch_content(stock_detail_v)
        else:
            console.hud_alert(f'エラー: 銘柄 {ticker_symbol} が見つかりません', 'error', 1.5)

    def show_banking_view(self, sender=None):
        if sender and hasattr(sender, 'superview') and sender.superview and hasattr(sender.superview, 'superview') and sender.superview.superview:
                sender.superview.superview.close()
        game_view = self.root_view.subviews[0]
        banking_v = BankingView(self, self.banking_handler, frame=game_view.get_content_frame(), flex='WH')
        game_view.switch_content(banking_v)

    def show_ma_market_view(self, sender=None):
        game_view = self.root_view.subviews[0]
        ma_view = MAMarketView(self, frame=game_view.get_content_frame(), flex='WH')
        game_view.switch_content(ma_view)

    def show_ma_deal_view(self, company_target):
        game_view = self.root_view.subviews[0]
        deal_view = MADealView(self.investment_handler, company_target, frame=game_view.get_content_frame(), flex='WH')
        game_view.switch_content(deal_view)

    def show_venture_market_view(self, sender=None):
        venture_system.refresh_venture_deal_market(self.game_time)
        game_view = self.root_view.subviews[0]
        vc_view = VentureMarketView(self, frame=game_view.get_content_frame(), flex='WH')
        game_view.switch_content(vc_view)

    def show_venture_deal_view(self, deal_data):
        game_view = self.root_view.subviews[0]
        deal_view = VentureDealView(self.investment_handler, deal_data, frame=game_view.get_content_frame(), flex='WH')
        game_view.switch_content(deal_view)
        
    def close_modal_view(self, sender):
        if self.setup_view and self.setup_view.on_screen:
            self.setup_view.close()
        elif sender and sender.superview:
            if hasattr(sender.superview, 'close'):
                 sender.superview.close()

    # --- ゲーム進行・初期化メソッド ---

    def process_next_week(self):
        console.hud_alert('週を進めています...', 'success', 0.5)
        self.game_time.advance_week()
        
        market_data = general_stock_market_system.listed_companies_on_market
        self.player.process_weekly_updates(self.game_time, market_data)
        
        if self.game_time.is_quarter_end():
            self.player.process_quarterly_updates(self.game_time, market_data)

        if self.root_view.subviews:
            game_view = self.root_view.subviews[0]
            if hasattr(game_view, 'update_view'):
                game_view.update_view()
    
    def load_game(self, sender):
        console.hud_alert('ロード機能は現在開発中です', 'error', 1)

    def exit_game(self, sender):
        self.root_view.close()


if __name__ == '__main__':
    main_controller = MainUIController()
