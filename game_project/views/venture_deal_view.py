# views/venture_deal_view.py
import ui
import constants

class VentureDealView(ui.View):
    """ベンチャー投資の個別案件の詳細・アクション画面"""
    def __init__(self, investment_handler, deal_data, **kwargs):
        super().__init__(**kwargs)
        self.investment_handler = investment_handler
        self.game_controller = investment_handler.gc # MainControllerへの参照
        self.deal = deal_data
        self.background_color = '#0d0d0d'
        self.update()

    def update(self):
        for v in list(self.subviews): self.remove_subview(v)
        self.setup_ui()

    def setup_ui(self):
        back_button = ui.Button(title='< VC市場へ戻る')
        back_button.frame = (15, 15, 150, 30)
        back_button.tint_color = 'white'
        back_button.content_horizontal_alignment = 'left'
        back_button.action = self.game_controller.show_venture_market_view
        self.add_subview(back_button)

        scroll = ui.ScrollView(frame=self.bounds, flex='WH')
        self.add_subview(scroll)
        
        y_pos = 20
        
        title_label = ui.Label(text=self.deal['company_name'], font=('<system-bold>', 22), text_color='white', frame=(20, y_pos, self.width-40, 25), alignment=ui.ALIGN_CENTER, flex='W')
        scroll.add_subview(title_label)
        y_pos += 30

        subtitle = f"{self.deal['sector']} | {self.deal['growth_stage']}ステージ"
        subtitle_label = ui.Label(text=subtitle, font=('<system>', 14), text_color='#AEAEB2', frame=(20, y_pos, self.width-40, 20), alignment=ui.ALIGN_CENTER, flex='W')
        scroll.add_subview(subtitle_label)
        y_pos += 40

        summary_label = ui.Label(text=self.deal['business_summary'], font=('<system>', 15), text_color='white', frame=(20, y_pos, self.width-40, 40), number_of_lines=0, flex='W')
        scroll.add_subview(summary_label)
        y_pos += 55

        y_pos = self.create_dd_info_section(scroll, y_pos)
        y_pos = self.create_action_buttons(scroll, y_pos)
        
        scroll.content_size = (self.width, y_pos + 20)

    def create_dd_info_section(self, scroll, y_pos):
        dd_title = ui.Label(text='デューデリジェンス情報', font=('<system-bold>', 16), text_color='white', frame=(20, y_pos, self.width-40, 20), flex='W')
        scroll.add_subview(dd_title)
        y_pos += 25
        
        revealed_something = False
        dd_items_to_display = []
        for level in range(4):
            if self.deal.get('dd_level_performed', 0) >= level:
                for key in constants.VENTURE_DD_LEVELS_INFO[level]["info_keys_revealed"]:
                    if self.deal['revealed_info'].get(key):
                        display_name = constants.VENTURE_DD_DISPLAY_NAMES.get(key, key)
                        value = self.deal.get(key, 'N/A')
                        text = f"・{display_name}: {value}"
                        color = '#34C759' if level > 0 else 'white'
                        dd_items_to_display.append({'text': text, 'color': color})
                        revealed_something = True
        
        if not revealed_something:
             label = ui.Label(text="DD未実施です。", font=('<system>', 14), text_color='#8E8E93', frame=(30, y_pos, self.width-60, 40), flex='W', number_of_lines=0)
             label.size_to_fit()
             scroll.add_subview(label)
             y_pos += label.height + 5
        else:
            for item in dd_items_to_display:
                label = ui.Label(text=item['text'], font=('<system>', 14), text_color=item['color'], frame=(30, y_pos, self.width-60, 40), flex='W', number_of_lines=0)
                label.size_to_fit()
                scroll.add_subview(label)
                y_pos += label.height + 5
             
        return y_pos + 15
        
    def create_action_buttons(self, scroll, y_pos):
        current_dd_level = self.deal.get('dd_level_performed', 0)
        
        for level in range(1, 4):
            if current_dd_level < level:
                dd_info = constants.VENTURE_DD_LEVELS_INFO.get(level)
                if dd_info:
                    btn = ui.Button(title=f"{dd_info['name']}実行 (¥{dd_info['cost']:,})", font=('<system-bold>', 16), background_color='#555', tint_color='white', corner_radius=8)
                    btn.frame = (20, y_pos, self.width-40, 44)
                    btn.flex = 'W'
                    btn.action = self.investment_handler.confirm_venture_dd
                    btn.dd_level = level
                    btn.deal_data = self.deal
                    scroll.add_subview(btn)
                    y_pos += 54
                    
        invest_btn = ui.Button(title='この案件に投資する', font=('<system-bold>', 16), background_color='#007AFF', tint_color='white', corner_radius=8)
        invest_btn.frame = (20, y_pos, self.width-40, 44)
        invest_btn.flex = 'W'
        invest_btn.action = self.investment_handler.confirm_venture_investment
        invest_btn.deal_data = self.deal
        scroll.add_subview(invest_btn)
        y_pos += 54
        
        return y_pos
