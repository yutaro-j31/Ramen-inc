# handlers/hq_handler.py
import ui
import console
import dialogs
import constants
from systems import rnd_system
from views.establish_hq_view import EstablishHQView # <<< この行を追加

class HQActionHandler:
    def __init__(self, game_controller):
        self.gc = game_controller

    def establish_hq_tapped(self, sender):
        modal = EstablishHQView(rent_action=self.confirm_establish_hq_rented, build_action=self.confirm_establish_hq_owned, frame=self.gc.root_view.bounds, flex='WH')
        modal.present('sheet')

    def confirm_establish_hq_rented(self, sender):
        sender.superview.superview.close()
        cost = constants.HQ_RENTED_INITIAL_COST
        rent = constants.HQ_RENTED_WEEKLY_RENT
        if self.gc.player.establish_hq_rented(cost, rent):
            console.hud_alert('本社(賃貸)を設立しました!', 'success', 1.5)
            self.gc.root_view.subviews[0].update_view()
        else:
            console.hud_alert('資金が不足しています。', 'error', 1.5)

    def confirm_establish_hq_owned(self, sender):
        sender.superview.superview.close()
        cost = constants.HQ_OWNED_CONSTRUCTION_COST
        if self.gc.player.establish_hq_owned(cost):
            console.hud_alert('自社ビルが完成し、本社を設立しました!', 'success', 1.5)
            self.gc.root_view.subviews[0].update_view()
        else:
            console.hud_alert('建設費用が不足しています。', 'error', 1.5)
            
    def establish_department_tapped(self, sender):
        dept_key = sender.name
        ui.delay(lambda: self.show_department_alert(dept_key), 0.01)

    def show_department_alert(self, dept_key):
        cost_map = {"investment": constants.INVESTMENT_DEPT_SETUP_COST, "hr": constants.HR_DEPT_SETUP_COST, "rnd": constants.RND_DEPT_SETUP_COST, "marketing": constants.MARKETING_DEPT_SETUP_COST}
        cost = cost_map.get(dept_key, 0)
        dept_name_map = {"investment": "投資部門", "hr": "人事部門", "rnd": "R&D部門", "marketing": "マーケティング部門"}
        dept_name = dept_name_map.get(dept_key, dept_key.upper())
        try:
            choice = console.alert(f"{dept_name}の設置", f"設置には費用が ¥{cost:,.0f} かかります。よろしいですか?", "設置する", "キャンセル", hide_cancel_button=False)
            if choice == 1:
                if self.gc.player.establish_department(dept_key, cost):
                    console.hud_alert(f"{dept_name}を設置しました!", 'success', 1.5)
                    self.gc.root_view.subviews[0].update_view()
        except KeyboardInterrupt: pass
            
    def hire_cxo(self, candidate):
        cost = constants.CXO_RECRUITMENT_COST_BASE * constants.CXO_RECRUITMENT_COST_SKILL_MULTIPLIER.get(candidate.skill_level, 1.0)
        if self.gc.player.finance.get_cash() < cost:
            console.hud_alert('契約金が不足しています。', 'error', 1.5)
            return
        if self.gc.player.hire_cxo(candidate):
            self.gc.player.finance.record_expense(cost, 'recruitment')
            console.hud_alert(f'{candidate.name}を雇用しました。', 'success', 1.5)
            self.gc.root_view.subviews[0].update_view()
    
    def fire_cxo(self, position):
        fired_cxo = self.gc.player.fire_cxo(position)
        if fired_cxo:
            console.hud_alert(f'{fired_cxo.name}を解任しました。', 'success', 1.5)
            self.gc.root_view.subviews[0].update_view()
    
    def start_rnd_project(self, project_data):
        ui.delay(lambda: self.show_start_project_alert(project_data), 0.01)

    def show_start_project_alert(self, project_data):
        cost = project_data.get('cost_to_start', 0)
        try:
            choice = console.alert(f"{project_data['name']}", f"プロジェクトの開始には ¥{cost:,.0f} かかります。", "開始する", "キャンセル")
            if choice == 1:
                rnd_system.start_new_project(self.gc.player, project_data)
                self.gc.root_view.subviews[0].update_view()
        except KeyboardInterrupt: pass

    def fund_rnd_project(self, project_data):
        max_funding = project_data.get('max_weekly_funding', 0)
        project_id = project_data.get('id', '')
        amount_str = dialogs.text_input_dialog(title=f"{project_data['name']}への資金投入", text=f"今週の投入額を入力してください(最大: ¥{max_funding:,.0f})")
        if amount_str:
            try:
                amount = int(amount_str)
                if rnd_system.allocate_funding_to_project_from_ui(self.gc.player, project_id, amount):
                    console.hud_alert(f'¥{amount:,.0f}を投入しました', 'success', 1)
                    self.gc.root_view.subviews[0].update_view()
            except ValueError:
                console.hud_alert('数値を入力してください', 'error', 1)
