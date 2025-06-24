# handlers/banking_handler.py
import ui
import console
from views.take_loan_view import TakeLoanView

class BankingActionHandler:
    def __init__(self, game_controller):
        self.gc = game_controller

    def show_take_loan_modal(self, loan_product):
        max_amount = loan_product['customized_max_amount']
        if max_amount <= 0:
            console.alert('融資不可', '現在の格付けでは、このローン商品は利用できません。', 'OK', hide_cancel_button=True)
            return

        def confirm_loan_action(amount):
            if not (0 < amount <= max_amount):
                console.alert('入力エラー', f'融資希望額は¥1 ~ ¥{max_amount:,.0f}の範囲で入力してください。')
                return

            if self.gc.player.take_loan(
                amount=float(amount),
                weekly_rate=loan_product['customized_rate'],
                lender_name=loan_product['bank_name'],
                product_name=loan_product['product_name'],
                repayment_weeks=loan_product['repayment_weeks'],
                game_time=self.gc.game_time
            ):
                console.hud_alert('融資が実行されました', 'success', 1.5)
                self.gc.root_view.subviews[0].update_view()

        modal = TakeLoanView(loan_product, confirm_loan_action, frame=self.gc.root_view.bounds, flex='WH')
        modal.present('fade')
