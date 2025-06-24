# views/ma_deal_view.py
import ui
import constants

class MADealView(ui.View):
    """M&Aの個別案件の交渉画面"""
    def __init__(self, investment_handler, company_target, **kwargs):
        super().__init__(**kwargs)
        self.investment_handler = investment_handler
        # 画面遷移など、全体に関わる動作はメインコントローラーを呼び出す
        self.game_controller = investment_handler.gc 
        self.company = company_target
        self.background_color = '#0d0d0d'
        self.update()

    def update(self):
        """画面の再描画"""
        for v in list(self.subviews): self.remove_subview(v)
        self.setup_ui()

    def setup_ui(self):
        # 戻るボタン
        back_button = ui.Button(title='< M&A市場へ戻る')
        back_button.frame = (15, 15, 150, 30)
        back_button.tint_color = 'white'
        back_button.content_horizontal_alignment = 'left'
        back_button.action = self.game_controller.show_ma_market_view
        self.add_subview(back_button)

        # スクロールビュー
        scroll = ui.ScrollView(frame=self.bounds, flex='WH')
        self.add_subview(scroll)
        
        y_pos = 20
        
        # --- 企業情報 ---
        title_label = ui.Label(text=self.company.name, font=('<system-bold>', 22), text_color='white', frame=(20, y_pos, self.width-40, 25), alignment=ui.ALIGN_CENTER, flex='W')
        scroll.add_subview(title_label)
        y_pos += 30

        industry_label = ui.Label(text=self.company.industry, font=('<system>', 14), text_color='#AEAEB2', frame=(20, y_pos, self.width-40, 20), alignment=ui.ALIGN_CENTER, flex='W')
        scroll.add_subview(industry_label)
        y_pos += 40

        # --- 財務情報 ---
        details = [
            f"推定年商: ¥{self.company.estimated_annual_revenue:,.0f}",
            f"推定純利益: ¥{self.company.get_estimated_net_profit():,.0f} (利益率: {self.company.estimated_net_profit_margin*100:.1f}%)",
            f"従業員数: {self.company.employee_count}人",
            f"希望買収価格帯: ¥{self.company.asking_price_min:,.0f} ~ ¥{self.company.asking_price_max:,.0f}"
        ]
        for text in details:
            label = ui.Label(text=text, font=('<system>', 15), text_color='white', frame=(20, y_pos, self.width-40, 20), flex='W')
            scroll.add_subview(label)
            y_pos += 25
        y_pos += 15

        # --- DD情報 ---
        y_pos = self.create_dd_info_section(scroll, y_pos)
        
        # --- アクションボタン ---
        y_pos = self.create_action_buttons(scroll, y_pos)
        
        scroll.content_size = (self.width, y_pos + 20)

    def create_dd_info_section(self, scroll, y_pos):
        dd_title = ui.Label(text='デューデリジェンス情報:', font=('<system-bold>', 16), text_color='white', frame=(20, y_pos, self.width-40, 20), flex='W')
        scroll.add_subview(dd_title)
        y_pos += 25

        if self.company.dd_performed:
            dd_details = [
                f"強み: {self.company.dd_revealed_strength}",
                f"弱み: {self.company.dd_revealed_weakness}",
            ]
            for text in dd_details:
                label = ui.Label(text=f"・{text}", font=('<system>', 14), text_color='#34C759', frame=(30, y_pos, self.width-50, 40), number_of_lines=0, flex='W')
                label.size_to_fit()
                scroll.add_subview(label)
                y_pos += label.height + 5
        else:
            label = ui.Label(text="未実施です。", font=('<system>', 14), text_color='#8E8E93', frame=(30, y_pos, self.width-50, 20), flex='W')
            scroll.add_subview(label)
            y_pos += 22
             
        return y_pos + 20
        
    def create_action_buttons(self, scroll, y_pos):
        dd_button = ui.Button(title=f"デューデリジェンス実行 (¥{constants.MA_PRIVATE_COMPANY_DD_COST:,.0f})", font=('<system-bold>', 16), background_color='#555', tint_color='white', corner_radius=8)
        dd_button.frame = (20, y_pos, self.width-40, 44)
        dd_button.flex = 'W'
        dd_button.enabled = not self.company.dd_performed
        dd_button.action = self.investment_handler.confirm_due_diligence
        dd_button.company_target = self.company
        scroll.add_subview(dd_button)
        y_pos += 54
        
        propose_button = ui.Button(title='買収を提案する', font=('<system-bold>', 16), background_color='#007AFF', tint_color='white', corner_radius=8)
        propose_button.frame = (20, y_pos, self.width-40, 44)
        propose_button.flex = 'W'
        propose_button.action = self.investment_handler.propose_acquisition
        propose_button.company_target = self.company
        scroll.add_subview(propose_button)
        y_pos += 54
        
        return y_pos
