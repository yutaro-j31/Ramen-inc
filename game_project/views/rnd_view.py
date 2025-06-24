# views/rnd_view.py
import ui
import console
from systems import rnd_system

class RNDProjectListDataSource:
    """R&Dプロジェクトリスト用のTableViewデータソース"""
    def __init__(self, items, project_type, action):
        self.items = items
        self.project_type = project_type
        self.action = action

    def tableview_number_of_rows(self, tableview, section):
        return len(self.items)

    def tableview_cell_for_row(self, tableview, section, row):
        cell = ui.TableViewCell('subtitle')
        project = self.items[row]
        cell.text_label.text = project.get('name', 'N/A')
        
        action_title = ''
        if self.project_type == 'available':
            cost = project.get('cost_to_start', 0)
            cell.detail_text_label.text = f"開始費用: ¥{cost:,.0f} | 必要RP: {project.get('research_points_needed', 0)}"
            action_title = '開始'
        else: # active
            progress = (project.get('points_accrued', 0) / project.get('research_points_needed', 1)) * 100
            cell.detail_text_label.text = f"進捗: {progress:.1f}%"
            action_title = '資金投入'
            
        action_button = ui.Button(title=action_title, font=('<system-bold>', 12), corner_radius=5, tint_color='white')
        action_button.frame = (tableview.width - 90, 7, 80, 30)
        action_button.background_color = '#34C759' if action_title == '開始' else '#007AFF'
        action_button.row = row
        action_button.action = self.action
        cell.content_view.add_subview(action_button)
        
        return cell

class RNDView(ui.View):
    """研究開発の管理画面"""
    def __init__(self, hq_handler, **kwargs):
        super().__init__(**kwargs)
        self.hq_handler = hq_handler
        self.game_controller = hq_handler.gc
        self.background_color = '#0d0d0d'
        self.update()

    def update(self):
        for subview in self.subviews:
            if isinstance(subview, (ui.TableView, ui.Label)) and subview.name == 'content':
                self.remove_subview(subview)
        self.setup_ui()
        
    def setup_ui(self):
        if not any(v.name == 'back_button' for v in self.subviews):
            back_button = ui.Button(title='< 本社画面へ戻る', name='back_button')
            back_button.frame = (15, 15, 150, 30)
            back_button.tint_color = 'white'
            back_button.content_horizontal_alignment = 'left'
            back_button.action = self.back_action
            self.add_subview(back_button)

            title_label = ui.Label(text='研究開発センター', font=('<system-bold>', 20), text_color='white')
            title_label.size_to_fit()
            title_label.center = (self.width / 2, 40)
            self.add_subview(title_label)

        player = self.game_controller.player
        
        # --- 進行中のプロジェクト ---
        active_label = ui.Label(name='content', text='進行中のプロジェクト', font=('<system-bold>', 16), frame=(15, 80, 200, 20), text_color='white')
        self.add_subview(active_label)
        
        active_projects = [p for p in player.effects.active_rnd_bonuses.values() if not p.get('is_permanent')]
        active_tv = ui.TableView(frame=(0, 110, self.width, 150), flex='W', name='content')
        active_tv.data_source = RNDProjectListDataSource(active_projects, 'active', self.handle_fund_action)
        self.add_subview(active_tv)
        
        # --- 開始可能なプロジェクト ---
        available_label = ui.Label(name='content', text='開始可能なプロジェクト', font=('<system-bold>', 16), frame=(15, 270, 200, 20), text_color='white')
        self.add_subview(available_label)
        
        available_projects = rnd_system.list_available_projects(player)
        available_tv = ui.TableView(frame=(0, 300, self.width, self.height - 310), flex='WH', name='content')
        available_tv.data_source = RNDProjectListDataSource(available_projects, 'available', self.handle_start_action)
        self.add_subview(available_tv)

    def handle_start_action(self, sender):
        row = sender.row
        available = rnd_system.list_available_projects(self.game_controller.player)
        if 0 <= row < len(available):
            self.hq_handler.start_rnd_project(available[row])

    def handle_fund_action(self, sender):
        row = sender.row
        active_projects = [p for p in self.game_controller.player.effects.active_rnd_bonuses.values() if not p.get('is_permanent')]
        if 0 <= row < len(active_projects):
            self.hq_handler.fund_rnd_project(active_projects[row])

    def back_action(self, sender):
        self.game_controller.show_hq_view()
