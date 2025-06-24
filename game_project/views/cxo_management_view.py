# views/cxo_management_view.py
import ui
import console
from systems import hr_system

class CXOListDataSource:
    """CXOリスト用のTableViewデータソース"""
    def __init__(self, items, action_title, action):
        self.items = items
        self.action_title = action_title
        self.action = action

    def tableview_number_of_rows(self, tableview, section):
        return len(self.items)

    def tableview_cell_for_row(self, tableview, section, row):
        cell = ui.TableViewCell('subtitle')
        cxo = self.items[row]
        
        cell.text_label.text = f"{cxo.name} ({cxo.display_position_name})"
        cell.detail_text_label.text = f"スキル: {cxo.skill_level} | 週給: ¥{cxo.weekly_salary:,.0f}"
        
        action_button = ui.Button(title=self.action_title, font=('<system-bold>', 12), corner_radius=5, tint_color='white')
        action_button.frame = (tableview.width - 90, 7, 80, 30)
        action_button.background_color = '#C53426' if self.action_title == '解任' else '#34C759'
        action_button.row = row
        action_button.action = self.action
        cell.content_view.add_subview(action_button)
        
        return cell

class CXOManagementView(ui.View):
    """経営陣(CXO)の管理画面"""
    def __init__(self, hq_handler, **kwargs):
        super().__init__(**kwargs)
        self.hq_handler = hq_handler
        self.game_controller = hq_handler.gc
        self.background_color = '#0d0d0d'
        self.update()

    def update(self):
        """UIの再描画"""
        for v in list(self.subviews): self.remove_subview(v)
        self.setup_ui()

    def setup_ui(self):
        back_button = ui.Button(title='< 本社画面へ戻る')
        back_button.frame = (15, 15, 150, 30)
        back_button.tint_color = 'white'
        back_button.content_horizontal_alignment = 'left'
        back_button.action = self.back_action
        self.add_subview(back_button)

        title_label = ui.Label(text='経営陣の管理', font=('<system-bold>', 20), text_color='white')
        title_label.size_to_fit()
        title_label.center = (self.width / 2, 40)
        self.add_subview(title_label)
        
        player = self.game_controller.player
        
        # --- 現在の経営陣 ---
        current_cxo_label = ui.Label(text='現在の経営陣', font=('<system-bold>', 16), frame=(15, 80, 200, 20), text_color='white')
        self.add_subview(current_cxo_label)
        
        current_cxo_tv = ui.TableView(frame=(0, 110, self.width, 150), flex='W')
        current_cxo_tv.data_source = CXOListDataSource(list(player.employed_cxos.values()), '解任', self.handle_fire_action)
        self.add_subview(current_cxo_tv)
        
        # --- 候補者市場 ---
        candidates_label = ui.Label(text='CXO候補者市場', font=('<system-bold>', 16), frame=(15, 270, 200, 20), text_color='white')
        self.add_subview(candidates_label)
        
        candidates = hr_system.view_cxo_candidates(player, self.game_controller.game_time)
        
        candidates_tv = ui.TableView(frame=(0, 300, self.width, self.height - 310), flex='WH')
        candidates_tv.data_source = CXOListDataSource(candidates, '雇用', self.handle_hire_action)
        self.add_subview(candidates_tv)

    def handle_hire_action(self, sender):
        row = sender.row
        candidates = hr_system.view_cxo_candidates(self.game_controller.player, self.game_controller.game_time)
        if 0 <= row < len(candidates):
            candidate_to_hire = candidates[row]
            self.hq_handler.hire_cxo(candidate_to_hire)

    def handle_fire_action(self, sender):
        row = sender.row
        employed_cxos = list(self.game_controller.player.employed_cxos.values())
        if 0 <= row < len(employed_cxos):
            cxo_to_fire = employed_cxos[row]
            self.hq_handler.fire_cxo(cxo_to_fire.position)

    def back_action(self, sender):
        self.game_controller.show_hq_view()
