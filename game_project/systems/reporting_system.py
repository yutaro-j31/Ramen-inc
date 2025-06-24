# systems/reporting_system.py

from typing import List, Optional, Any
from models.player import Player
from models.portfolio import Portfolio

def get_status_summary(player: Player, market_data: Optional[List[Any]] = None) -> str:
    """プレイヤーと会社の現在の状況を、パネル形式のダッシュボードで生成する。"""

    # --- データ収集 ---
    
    # 会社財務
    company_cash = player.finance.get_cash()
    # --- ▼▼▼ ここが今回の修正箇所です ▼▼▼ ---
    # player.financeからではなく、playerから直接呼び出す
    company_debt = player.get_total_debt()
    
    company_assets = company_cash
    if hasattr(player.ops, 'company_properties'): 
        company_assets += sum(p.current_value for p in player.ops.company_properties)
    company_assets += player.company_portfolio.get_total_stock_value(market_data)
    
    company_net_worth = company_assets - company_debt
    credit_rating = f"{player.credit_rating} ({player.credit_rating_score})"

    # 個人資産
    personal_cash = player.personal_assets.money
    personal_properties_value = 0
    if hasattr(player.personal_assets, 'properties'): 
        personal_properties_value = sum(p.current_value for p in player.personal_assets.properties)
    personal_stock_value = player.personal_assets.portfolio.get_total_stock_value(market_data)
    personal_assets_total = personal_cash + personal_properties_value + personal_stock_value
    
    # 投資サマリー
    comp_stock_count = len(player.company_portfolio.general_stock_portfolio)
    comp_vc_count = len(player.company_portfolio.active_venture_investments)
    pers_stock_count = len(player.personal_assets.portfolio.general_stock_portfolio)
    pers_vc_count = len(player.personal_assets.portfolio.active_venture_investments)

    # 事業運営サマリー
    shop_count = len(player.ops.businesses_owned)
    hq_status = player.ops.headquarters_type
    active_depts = [dept.upper() for dept, is_active in player.ops.departments.items() if is_active]
    dept_str = ", ".join(active_depts) if active_depts else "なし"
    cxo_count = len(player.hr.employed_cxos)

    # --- 表示整形 ---
    
    width = 65
    summary = []
    
    # ヘッダー
    title = f" 🏢 {player.company_name} "
    summary.append("+" + "=" * (width-2) + "+")
    summary.append(f"|{title.center(width-2, ' ')}|")
    summary.append("+" + "=" * (width-2) + "+")

    # 会社財務パネル
    summary.append(f"| 💹 財務[会社]                                                        |")
    summary.append(f"|   現金      : ¥{company_cash:<18,.0f} | 純資産: ¥{company_net_worth:<18,.0f} |")
    summary.append(f"|   総資産    : ¥{company_assets:<18,.0f} | 総負債: ¥{company_debt:<18,.0f} |")
    summary.append(f"|   信用格付  : {credit_rating:<20} |                                |")
    summary.append("+" + "-" * (width-2) + "+")

    # 個人資産パネル
    summary.append(f"| 🧑 財務[個人]                                                        |")
    summary.append(f"|   現金      : ¥{personal_cash:<18,.0f} | 総資産: ¥{personal_assets_total:<18,.0f} |")
    summary.append("+" + "-" * (width-2) + "+")

    # 投資パネル
    summary.append(f"| 📈 投資ポートフォリオ                                               |")
    summary.append(f"| [会社] 株式: {comp_stock_count}銘柄, VC: {comp_vc_count}件".ljust(width-2) + "|")
    summary.append(f"| [個人] 株式: {pers_stock_count}銘柄, VC: {pers_vc_count}件".ljust(width-2) + "|")
    summary.append("+" + "-" * (width-2) + "+")

    # 事業運営パネル
    summary.append(f"| 🍜 事業運営                                                         |")
    summary.append(f"|   事業数: {shop_count:<2}店舗   | 本部: {hq_status:<15} |")
    summary.append(f"|   部門  : {dept_str:<20} | 経営陣: {cxo_count}名                      |")
    summary.append("+" + "-" * (width-2) + "+")

    return "\n".join(summary)


def get_portfolio_summary(player: Player, market_data: List[Any]) -> str:
    """プレイヤーの全ポートフォリオの詳細なサマリーを生成する。"""
    
    report_lines = ["\n" + "="*60, "保有ポートフォリオ一覧".center(56), "="*60]

    def format_portfolio(portfolio: Portfolio, owner_name: str):
        report_lines.append(f"\n--- {owner_name}ポートフォリオ ---")
        
        has_assets = False
        # 一般株式
        if portfolio.general_stock_portfolio:
            has_assets = True
            report_lines.append("\n【一般株式】")
            stock_value = portfolio.get_total_general_stock_value(market_data)
            report_lines.append(f"  評価額合計: ¥{stock_value:,.0f}")
            for ticker, holding in portfolio.general_stock_portfolio.items():
                total_shares = holding.get('cash_shares', 0) + holding.get('margin_shares', 0)
                report_lines.append(f"  - {holding['company_name']} ({ticker}): {total_shares:,}株 (平均取得単価: ¥{holding.get('average_buy_price', 0):,.2f})")
        
        # 空売りポジション
        if portfolio.short_positions:
            has_assets = True
            report_lines.append("\n【空売りポジション】")
            for ticker, pos in portfolio.short_positions.items():
                report_lines.append(f"  - {pos['company_name']} ({ticker}): {pos['shares']:,}株 (売建単価: ¥{pos['sell_price']:,.2f})")

        # 信用取引情報
        if portfolio.has_margin_account and portfolio.margin_loan > 0:
            has_assets = True
            report_lines.append("\n【信用取引情報】")
            report_lines.append(f"  信用負債残高: ¥{portfolio.margin_loan:,.0f}")
        
        if not has_assets:
            report_lines.append("  現在、このポートフォリオに資産はありません。")

    # 会社と個人の両方のポートフォリオをフォーマット
    format_portfolio(player.company_portfolio, "会社")
    format_portfolio(player.personal_portfolio, "個人")
    
    report_lines.append("\n" + "="*60)
    return "\n".join(report_lines)


def generate_company_financial_report(player: Player, market_data: Optional[List[Any]] = None) -> str:
    """会社の詳細な財務レポート文字列を生成する。"""
    report = []
    width = 50
    
    report.append("\n" + "="*width)
    report.append(f"  {player.company_name} 財務レポート".center(width-4))
    report.append("="*width)

    # --- 貸借対照表 (B/S) ---
    report.append("\n" + "--- 貸借対照表 (B/S) ".ljust(width-1) + "-")
    
    # 資産の部
    cash = player.finance.get_cash()
    properties_value = 0
    if hasattr(player.ops, 'company_properties'):
        properties_value = sum(p.current_value for p in player.ops.company_properties)
    stock_value = player.company_portfolio.get_total_stock_value(market_data)
    total_assets = cash + properties_value + stock_value
    report.append("\n  [資産の部]")
    report.append(f"    現金及び預金:".ljust(25) + f"¥{cash:15,.0f}")
    report.append(f"    有価証券 (株式・VC):".ljust(25) + f"¥{stock_value:15,.0f}")
    report.append(f"    固定資産 (不動産):".ljust(25) + f"¥{properties_value:15,.0f}")
    report.append(" " * 25 + "-"*17)
    report.append(f"    資産合計:".ljust(25) + f"¥{total_assets:15,.0f}")

    # 負債・純資産の部
    bank_loan = player.finance.get_total_bank_loan()
    bonds = player.finance.get_total_bonds_payable()
    margin_loan = player.company_portfolio.margin_loan
    total_liabilities = bank_loan + bonds + margin_loan
    net_worth = total_assets - total_liabilities
    report.append("\n  [負債・純資産の部]")
    report.append(f"    銀行借入金:".ljust(25) + f"¥{bank_loan:15,.0f}")
    report.append(f"    社債:".ljust(25) + f"¥{bonds:15,.0f}")
    report.append(f"    信用取引借入金:".ljust(25) + f"¥{margin_loan:15,.0f}")
    report.append(f"    負債合計:".ljust(25) + f"¥{total_liabilities:15,.0f}")
    report.append(" " * 25 + "-"*17)
    report.append(f"    純資産:".ljust(25) + f"¥{net_worth:15,.0f}")
    report.append(f"    負債・純資産合計:".ljust(25) + f"¥{total_assets:15,.0f}")
    
    # --- 損益計算書 (P/L) ---
    report.append("\n" + "--- 損益計算書 (P/L) (累積) ".ljust(width-1) + "-")
    sales = player.finance.finances.get('total_sales', 0)
    costs = player.finance.finances.get('total_costs', 0)
    net_profit = sales - costs
    report.append(f"  総売上高:".ljust(25) + f"¥{sales:15,.0f}")
    report.append(f"  総費用:".ljust(25) + f"¥{costs:15,.0f}")
    report.append(" " * 25 + "-"*17)
    report.append(f"  純利益:".ljust(25) + f"¥{net_profit:15,.0f}")
    
    report.append("="*width)
    return "\n".join(report)
