# views/invest_view.py (ポートフォリオ表示機能を追加した完全版)
import ui
from systems import general_stock_market_system

class CombinedPortfolioDataSource:
    """株式とベンチャー投資の両方を表示するためのデータソース"""
    def __init__(self, player, market_data, action_handler):
        self.player = player
        self.market_data = market_data
        self.action_handler = action_handler
        
        self.sections = []
        self.data = {}
        
        # 会社保有株式
        company_stocks = list(self.player.company_portfolio.general_stock_portfolio.items())
        if company_stocks:
            self.sections.append("会社保有株式")
            self.data["会社保有株式"] = company_stocks

        # 会社VC投資
        company_vc = list(self.player.company_portfolio.active_venture_investments.values())
        if company_vc:
            self.sections.append("会社VC投資")
            self.data["会社VC投資"] = company_vc

    def tableview_number_of_sections(self, tableview):
        return len(self.sections)

    def tableview_title_for_header(self, tableview, section):
        return self.sections[section]
        
    def tableview_number_of_rows(self, tableview, section):
        section_title = self.sections[section]
        return len(self.data.get(section_title, []))

    def tableview_cell_for_row(self, tableview, section, row):
        section_title = self.sections[section]
        
        if section_title == "会社保有株式":
            return self.create_stock_cell(tableview, section, row)
        elif section_title == "会社VC投資":
            return self.create_vc_cell(tableview, section, row)
            
        return ui.TableViewCell()

    def create_stock_cell(self, tableview, section, row):
        cell = ui.TableViewCell()
        cell.background_color = '#1C1C1E'
        
        section_title = self.sections[section]
        ticker, holding = self.data[section_title][row]
        market_stock = next((s for s in self.market_data if s.ticker_symbol == ticker), None)
        
        if not market_stock: return cell

        total_shares = holding.get('cash_shares', 0) + holding.get('margin_shares', 0)
        avg_cost = holding.get('average_buy_price', 0)
        current_value = market_stock.current_price * total_shares
        total_cost = avg_cost * total_shares
        profit_loss = current_value - total_cost
        
        name_label = ui.Label(font=('<system-bold>', 16), text_color='white', text=f"{holding['company_name']} ({ticker})", frame=(15, 10, cell.content_view.width - 150, 20))
        cell.content_view.add_subview(name_label)
        
        shares_label = ui.Label(font=('<system>', 12), text_color='#AEAEB2', text=f"{total_shares:,.0f}株 @ ¥{avg_cost:,.2f}")
        shares_label.frame = (15, 32, cell.content_view.width - 150, 15)
        cell.content_view.add_subview(shares_label)
        
        pl_color = '#34C759' if profit_loss >= 0 else '#FF3B30'
        pl_sign = '+' if profit_loss >= 0 else ''
        pl_label = ui.Label(font=('<system-bold>', 16), text_color=pl_color, alignment=ui.ALIGN_RIGHT, text=f"{pl_sign}¥{profit_loss:,.0f}")
        pl_label.frame = (cell.content_view.width - 165, 10, 150, 20)
        cell.content_view.add_subview(pl_label)

        value_label = ui.Label(font=('<system>', 12), text_color='#AEAEB2', alignment=ui.ALIGN_RIGHT, text=f"現在価値: ¥{current_value:,.0f}")
        value_label.frame = (cell.content_view.width - 165, 32, 150, 15)
        cell.content_view.add_subview(value_label)
        
        return cell

    def create_vc_cell(self, tableview, section, row):
        cell = ui.TableViewCell('subtitle')
        cell.background_color = '#1C1C1E'
        cell.text_label.text_color = 'white'
        cell.detail_text_label.text_color = '#AEAEB2'
        
        section_title = self.sections[section]
        deal = self.data[section_title][row]
        
        cell.text_label.text = f"{deal.get('company_name', 'N/A')} ({deal.get('sector', 'N/A')})"
        cell.detail_text_label.text = f"ステータス: {deal.get('current_status', '不明')}"
        return cell


class InvestView(ui.View):
    """「投資」タブのトップメニュー画面"""
    def __init__(self, game_controller, investment_handler, **kwargs):
        super().__init__(**kwargs)
        self.game_controller = game_controller
        self.investment_handler = investment_handler
        self.background_color = '#0d0d0d'
        self.update()

    def did_load(self):
        self.update()

    def update(self):
        for subview in list(self.subviews): self.remove_subview(subview)
        
        title_label = ui.Label(text='投資戦略室', font=('<system-bold>', 24), text_color='white')
        title_label.size_to_fit()
        title_label.center = (self.width / 2, 50)
        self.add_subview(title_label)

        has_investment_dept = self.game_controller.player.departments.get('investment', False)
        
        y_pos = 100
        
        if has_investment_dept:
            menu_items = [
                {'title': '🚀 ベンチャー投資', 'action': self.game_controller.show_venture_market_view},
                {'title': '🤝 企業買収 (M&A)', 'action': self.game_controller.show_ma_market_view}
            ]
            for item in menu_items:
                btn = ui.Button(title=item['title'], font=('<system-bold>', 16), background_color='#2C2C2E', tint_color='white', corner_radius=10)
                btn.frame = (20, y_pos, self.width - 40, 50)
                btn.flex = 'W'
                btn.action = item['action']
                self.add_subview(btn)
                y_pos += 60
            
            y_pos += 20
            portfolio_label = ui.Label(text='会社保有ポートフォリオ', font=('<system-bold>', 16), frame=(15, y_pos, 200, 20), text_color='white')
            self.add_subview(portfolio_label)
            
            y_pos += 30
            tv = ui.TableView(frame=(0, y_pos, self.width, self.height - y_pos), flex='WH')
            tv.row_height = 60
            tv.separator_color = '#333'
            
            # --- ここから修正 ---
            # 新しいデータソースを使用
            market_data = general_stock_market_system.listed_companies_on_market
            data_source = CombinedPortfolioDataSource(self.game_controller.player, market_data, self.investment_handler)
            tv.data_source = data_source
            # tv.delegate = data_source # タップアクションが必要になったら追加
            # --- ここまで修正 ---
            self.add_subview(tv)
            
        else:
            info_label = ui.Label(text='本社で「投資部門」を設置すると、\nより高度な投資活動が可能になります。', font=('<system>', 16), text_color='#AEAEB2', number_of_lines=0, alignment=ui.ALIGN_CENTER)
            info_label.frame = (0, 0, self.width * 0.9, 100)
            info_label.center = (self.width / 2, self.height * 0.4)
            info_label.flex = 'W'
            self.add_subview(info_label)
