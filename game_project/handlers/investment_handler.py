# handlers/investment_handler.py (修正版)
import ui
import console
import dialogs
import unicodedata
import traceback
import constants
from systems import acquisition_system, venture_system, general_stock_market_system
from views.select_owner_view import SelectOwnerView
from views.trade_modal_view import TradeModalView

class InvestmentActionHandler:
    def __init__(self, game_controller):
        self.gc = game_controller # GameControllerへの参照

    # --- M&A関連のアクション ---
    def confirm_due_diligence(self, sender):
        target = sender.company_target
        def do_alert():
            cost = constants.MA_PRIVATE_COMPANY_DD_COST
            try:
                choice = console.alert('確認', f'デューデリジェンスを実行しますか?\n費用: ¥{cost:,.0f}', '実行', 'キャンセル', hide_cancel_button=False)
                if choice == 1:
                    if acquisition_system.perform_due_diligence(self.gc.player, target):
                        console.hud_alert('デューデリジェンスを実行しました。', 'success', 1.5)
                        self.gc.show_ma_deal_view(target)
                    else:
                        console.hud_alert('費用が不足しています。', 'error', 1.5)
            except KeyboardInterrupt: pass
        ui.delay(do_alert, 0.01)

    def propose_acquisition(self, sender):
        target = sender.company_target
        def do_dialog():
            try:
                title = '買収提案'
                message = f'提案額を入力してください (最低: ¥{target.asking_price_min:,.0f} 以上)'
                amount_str = dialogs.input_alert(title, message, '', '提案する', hide_cancel_button=False)
                if not amount_str: return
                
                normalized_str = unicodedata.normalize('NFKC', amount_str)
                cleaned_str = normalized_str.replace(',', '').replace('円', '').strip()
                
                total_value = 0
                if '億' in cleaned_str:
                    parts = cleaned_str.split('億', 1)
                    if parts[0]: total_value += float(parts[0]) * 100_000_000
                    cleaned_str = parts[1]
                
                if '万' in cleaned_str:
                    parts = cleaned_str.split('万', 1)
                    if parts[0]: total_value += float(parts[0]) * 10_000
                    cleaned_str = parts[1]
                
                if cleaned_str: total_value += float(cleaned_str)
                
                offer_amount = int(total_value)
                
                if offer_amount < target.asking_price_min:
                    console.alert('提案エラー', '提案額が相手企業の最低希望買収価格を下回っています。', 'OK')
                    return
                if self.gc.player.finance.get_cash() < offer_amount:
                    console.alert('エラー', '買収資金が不足しています。', 'OK')
                    return
                
                if acquisition_system.make_acquisition_offer(self.gc.player, target, float(offer_amount), self.gc.game_time):
                    console.alert('交渉成立!', f'「{target.name}」の買収に成功しました。', 'OK')
                    self.gc.show_ma_market_view()
                else:
                    console.alert('交渉決裂', '相手企業はあなたの提案に合意しませんでした。', 'OK')

            except (ValueError, TypeError):
                console.hud_alert('無効な金額です。数値を入力してください。', 'error', 1.5)
            except KeyboardInterrupt: pass
        ui.delay(do_dialog, 0.01)

    # --- ベンチャー投資関連のアクション ---
    def confirm_venture_dd(self, sender):
        deal = sender.deal_data
        level = sender.dd_level
        cost = constants.VENTURE_DD_LEVELS_INFO[level]['cost']
        
        def do_alert():
            try:
                choice = console.alert('DD実行確認', f"費用 ¥{cost:,.0f} でデューデリジェンスを実行しますか?", '実行', 'キャンセル')
                if choice == 1:
                    if venture_system.perform_dd(self.gc.player, deal, level):
                        console.hud_alert('DDを実行しました。', 'success', 1.5)
                        self.gc.show_venture_deal_view(deal)
                    else:
                        console.hud_alert('費用が不足しています。', 'error', 1.5)
            except KeyboardInterrupt: pass
        ui.delay(do_alert, 0.01)

    def confirm_venture_investment(self, sender):
        deal = sender.deal_data
        def do_dialog():
            try:
                owner_type_choice = dialogs.alert('投資主体を選択', '', '会社資金', '個人資産', 'キャンセル')
                if owner_type_choice == 1: owner = 'company'
                elif owner_type_choice == 2: owner = 'personal'
                else: return

                if venture_system.execute_investment(self.gc.player, deal, owner, self.gc.game_time):
                    console.hud_alert(f"「{deal['company_name']}」への投資を実行しました。", 'success', 2)
                    self.gc.show_venture_market_view()
                else:
                    console.hud_alert("投資に失敗しました。資金などを確認してください。", 'error', 2)
            except KeyboardInterrupt: pass
        ui.delay(do_dialog, 0.01)
        
    # --- 株式売買関連のアクション ---
    def show_trade_modal(self, stock_object, trade_type):
        def owner_selected_action(owner_type):
            self.present_trade_modal(stock_object, trade_type, owner_type)
        modal = SelectOwnerView(select_action=owner_selected_action, frame=self.gc.root_view.bounds, flex='WH')
        modal.present('fade')

    def present_trade_modal(self, stock_object, trade_type, owner_type):
        # --- ここを修正 ---
        # self.gc (MainUIController) ではなく self (InvestmentActionHandler) を渡す
        modal = TradeModalView(self, stock_object, trade_type, owner_type, frame=self.gc.root_view.bounds, flex='WH')
        # --- ここまで修正 ---
        modal.present('fade')
        
    def execute_trade(self, stock, trade_type, owner_type, num_shares):
        if trade_type == 'buy':
            if self.gc.player.buy_stock_on_cash(owner_type, stock.ticker_symbol, stock.company_name, num_shares, stock.current_price):
                console.hud_alert(f'{num_shares}株の買い注文が約定しました。', 'success', 1.5)
        elif trade_type == 'sell':
            if self.gc.player.sell_stock(owner_type, stock.ticker_symbol, num_shares, stock.current_price):
                console.hud_alert(f'{num_shares}株の売り注文が約定しました。', 'success', 1.5)
        self.gc.root_view.subviews[0].update_view()
