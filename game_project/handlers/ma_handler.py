# handlers/ma_handler.py
import ui
import console
import dialogs
import unicodedata
import traceback
import constants
from systems import acquisition_system

class MA_ActionHandler:
    def __init__(self, game_controller):
        self.gc = game_controller # GameControllerへの参照を保持

    def confirm_due_diligence(self, sender):
        """DD実行の確認ダイアログを表示する"""
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
            except KeyboardInterrupt:
                pass
        ui.delay(do_alert, 0.01)

    def propose_acquisition(self, sender):
        """買収提案額を入力するダイアログを表示する"""
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
            except KeyboardInterrupt:
                pass
                
        ui.delay(do_dialog, 0.01)

