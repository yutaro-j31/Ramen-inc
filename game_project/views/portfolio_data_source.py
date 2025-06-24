# views/portfolio_data_source.py
import ui
from systems import general_stock_market_system

class PortfolioDataSource:
    """保有株式リスト用のデータソース(共通)"""
    def __init__(self, portfolio, market_data):
        self.portfolio_data = portfolio
        self.market_data = market_data
        self.tickers = list(self.portfolio_data.general_stock_portfolio.keys())

    def tableview_number_of_rows(self, tableview, section):
        return len(self.tickers)

    def tableview_cell_for_row(self, tableview, section, row):
        cell = ui.TableViewCell()
        cell.background_color = '#1C1C1E'
        ticker = self.tickers[row]
        holding = self.portfolio_data.general_stock_portfolio[ticker]
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
