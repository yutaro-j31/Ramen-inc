# views/hq_view.py
import ui
import console

class PortfolioListDataSource:
    """事業ポートフォリオ用のTableViewデータソース"""
    def __init__(self, items):
        self.items = items

    def tableview_number_of_rows(self, tableview, section):
        return len(self.items)

    def tableview_cell_for_row(self, tableview, section, row):
        cell = ui.TableViewCell('value1')
        cell.background_color = '#1C1C1E'
        cell.text_label.text_color = 'white'
        cell.detail_text_label.text_color = '#AEAEB2'
        
        item = self.items[row]
        cell.text_label.text = item.get('name', 'N/A')
        cost = item.get('cost', 0)
        cell.detail_text_label.text = f"{item.get('type', 'N/A')} | 取得費用: ¥{cost:,.0f}"
        return cell

class HQView(ui.View):
    """「本社」タブで表示される画面全体。"""
    def __init__(self, game_controller, hq_handler, **kwargs):
        super().__init__(**kwargs)
        self.game_controller = game_controller
        self.hq_handler = hq_handler
        self.name = '本社画面'
        self.background_color = '#0d0d0d'
        
        self.scroll_view = ui.ScrollView(frame=self.bounds, flex='WH')
        self.add_subview(self.scroll_view)
        
        self.update()

    def update(self):
        """ゲームの状態に合わせてUIを再描画する"""
        for subview in list(self.scroll_view.subviews):
            self.scroll_view.remove_subview(subview)
            
        player = self.game_controller.player
        
        # --- 本社が未設立か設立済みかで表示を切り替える ---
        if player.ops.headquarters_type == 'なし':
            # 本社が未設立の場合の表示
            info_label = ui.Label(text='本社がありません。\nマップから貸しオフィスを契約して、\n事業の拠点を構えましょう。',
                                  font=('<system>', 16),
                                  text_color='#AEAEB2',
                                  number_of_lines=0,
                                  alignment=ui.ALIGN_CENTER)
            info_label.frame = (0, 0, self.width, self.height - 200)
            info_label.flex = 'WH'
            self.scroll_view.add_subview(info_label)
        else:
            # 本社設立後の通常の表示
            y_pos = 15
            y_pos = self.create_hq_status_card(y_pos)
            y_pos = self.create_departments_card(y_pos)
            y_pos = self.create_shop_management_card(y_pos)
            y_pos = self.create_cxo_card(y_pos)
            y_pos = self.create_rnd_card(y_pos)
            y_pos = self.create_portfolio_card(y_pos)
            self.scroll_view.content_size = (self.width, y_pos + 20)

    def create_card(self, y, height, title):
        """UIカードを生成するヘルパーメソッド"""
        card = ui.View(frame=(10, y, self.width - 20, height), flex='W')
        card.background_color = '#2C2C2E'
        card.corner_radius = 12
        
        title_label = ui.Label(frame=(15, 10, card.width - 30, 20), flex='W')
        title_label.text = title
        title_label.font = ('<system-bold>', 16)
        title_label.text_color = '#E5E5EA'
        self.scroll_view.add_subview(card)
        card.add_subview(title_label)
        
        return card, y + height + 15

    def create_hq_status_card(self, y):
        player = self.game_controller.player
        hq_type = player.ops.headquarters_type
        
        card, next_y = self.create_card(y, 80, '🏢 本社ステータス')
        
        status_text = f"形態: {hq_type}"
        cost_text = ""
        if hq_type == '賃貸オフィス':
            cost_text = f"週次家賃: ¥{player.ops.hq_weekly_rent:,.0f}"
        
        status_label = ui.Label(text=status_text, frame=(20, 40, 300, 20), text_color='white')
        cost_label = ui.Label(text=cost_text, frame=(20, 60, 300, 20), font=('<system>', 12), text_color='#AEAEB2')
        card.add_subview(status_label)
        card.add_subview(cost_label)
            
        return next_y

    def create_departments_card(self, y):
        card, next_y = self.create_card(y, 150, '📊 部門管理')
        depts_info = [
            {'key': 'investment', 'name': '投資部門'},
            {'key': 'hr', 'name': '人事部門'},
            {'key': 'rnd', 'name': 'R&D部門'},
            {'key': 'marketing', 'name': 'マーケティング部門'}
        ]
        
        for i, dept in enumerate(depts_info):
            is_active = self.game_controller.player.ops.departments.get(dept['key'], False)
            
            title = f"✓ {dept['name']}" if is_active else f"✗ {dept['name']}"
            bg_color = '#304A3A' if is_active else '#555'
            tint_color = '#34C759' if is_active else 'white'
            
            btn_width = (card.width - 45) / 2
            btn_x = 15 + (i % 2) * (btn_width + 15)
            btn_y = 50 + (i // 2) * 45
            
            btn = ui.Button(title=title, frame=(btn_x, btn_y, btn_width, 35), background_color=bg_color, tint_color=tint_color, corner_radius=8, font=('<system-bold>', 14), flex='W')
            btn.name = dept['key']
            
            if not is_active:
                btn.action = self.hq_handler.establish_department_tapped
            
            card.add_subview(btn)
        return next_y
        
    def create_shop_management_card(self, y):
        player = self.game_controller.player
        shop_count = len(player.ops.businesses_owned)
        card, next_y = self.create_card(y, 80, f'🍜 店舗運営 ({shop_count}店舗)')
        
        if shop_count > 0:
            manage_button = ui.Button(title='店舗一覧・管理', font=('<system-bold>', 14))
            manage_button.frame = (card.width - 150, 40, 130, 32)
            manage_button.flex = 'L'
            manage_button.background_color = '#007AFF'
            manage_button.tint_color = 'white'
            manage_button.corner_radius = 8
            manage_button.action = self.game_controller.show_shop_list_view
            card.add_subview(manage_button)
        else:
            status_label = ui.Label(text='まだ運営中の店舗はありません。', frame=(20, 45, 300, 20), font=('<system>', 14), text_color='#8E8E93')
            card.add_subview(status_label)
        return next_y
        
    def create_cxo_card(self, y):
        player = self.game_controller.player
        cxo_count = len(player.employed_cxos)
        
        card, next_y = self.create_card(y, 80, f'👥 経営陣 (CXO) ({cxo_count}名)')

        if not player.departments.get('hr', False):
            status_label = ui.Label(text='人事部門を設置すると、経営陣を雇用できます。', frame=(20, 45, 300, 20), font=('<system>', 12), text_color='#8E8E93')
            card.add_subview(status_label)
        else:
            manage_button = ui.Button(title='経営陣を管理', font=('<system-bold>', 14))
            manage_button.frame = (card.width - 150, 40, 130, 32)
            manage_button.flex = 'L'
            manage_button.background_color = '#007AFF'
            manage_button.tint_color = 'white'
            manage_button.corner_radius = 8
            manage_button.action = self.game_controller.show_cxo_management_view
            card.add_subview(manage_button)
            
        return next_y
        
    def create_rnd_card(self, y):
        player = self.game_controller.player
        active_projects_count = sum(1 for proj in player.effects.active_rnd_bonuses.values() if not proj.get('is_permanent'))
        
        card, next_y = self.create_card(y, 80, f'🔬 研究開発 (R&D) ({active_projects_count}件 進行中)')

        if not player.departments.get('rnd', False):
            status_label = ui.Label(text='R&D部門を設置すると、研究開発を行えます。', frame=(20, 45, 300, 20), font=('<system>', 12), text_color='#8E8E93')
            card.add_subview(status_label)
        else:
            manage_button = ui.Button(title='研究開発を行う', font=('<system-bold>', 14))
            manage_button.frame = (card.width - 150, 40, 130, 32)
            manage_button.flex = 'L'
            manage_button.background_color = '#007AFF'
            manage_button.tint_color = 'white'
            manage_button.corner_radius = 8
            manage_button.action = self.game_controller.show_rnd_management_view
            card.add_subview(manage_button)
            
        return next_y
        
    def create_portfolio_card(self, y):
        portfolio = self.game_controller.player.corp_dev.acquired_companies_log
        card_height = 50 + len(portfolio) * 50 if portfolio else 80
        card, next_y = self.create_card(y, card_height, f'📈 事業ポートフォリオ ({len(portfolio)}件)')
        
        if not portfolio:
            info_label = ui.Label(text='M&Aで取得した事業はありません。', font=('<system>', 14), text_color='#8E8E93', frame=(20, 45, card.width - 40, 20))
            card.add_subview(info_label)
        else:
            tv = ui.TableView(frame=(0, 40, card.width, card.height - 45), flex='WH')
            tv.row_height = 50
            tv.data_source = PortfolioListDataSource(portfolio)
            tv.separator_color = '#333'
            card.add_subview(tv)
            
        return next_y
