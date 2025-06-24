# systems/general_stock_market_system.py
import random
import string
from typing import List, Dict, Any, Optional

from models.player import Player
from models.game_time import GameTime
from models.listed_company import ListedCompany
import constants
from systems import reporting_system
import utils

# --- モジュールレベル変数 ---
listed_companies_on_market: List[ListedCompany] = []

# --- 市場の初期化・更新 ---
def initialize_general_stock_market(num_companies: int, start_year: int):
    """一般株式市場を初期化し、企業詳細情報を含む上場企業を生成する"""
    global listed_companies_on_market
    listed_companies_on_market = []
    
    def _generate_random_ticker_symbol(length: int = constants.TICKER_SYMBOL_LENGTH) -> str:
        return "".join(random.choices(string.digits, k=length))

    def _generate_random_company_name() -> str:
        parts = []
        if random.random() < 0.7: parts.append(random.choice(constants.COMPANY_NAME_ELEMENTS_PREFIX))
        parts.append(random.choice(constants.COMPANY_NAME_ELEMENTS_MIDDLE))
        if random.random() < 0.8: parts.append(random.choice(constants.COMPANY_NAME_ELEMENTS_SUFFIX))
        return "".join(parts)

    used_tickers = set() 
    tiers = list(constants.MARKET_CAP_TIERS.keys())
    weights = [constants.MARKET_CAP_TIER_WEIGHTS[t] for t in tiers]

    for i in range(num_companies):
        while True: 
            ticker = _generate_random_ticker_symbol()
            if ticker not in used_tickers:
                used_tickers.add(ticker)
                break
        
        name = _generate_random_company_name()
        sector = random.choice(constants.STOCK_SECTORS)
        founded_year = start_year - random.randint(5, 80)
        
        description = random.choice(constants.COMPANY_DESCRIPTION_TEMPLATES).format(
            sector=sector, founded_year=founded_year
        )
        
        num_shareholders = random.randint(3, 5)
        shareholders = random.sample(constants.MAJOR_SHAREHOLDER_NAMES, num_shareholders)
        major_shareholders = []
        remaining_stake = 25.0 + random.uniform(-5.0, 5.0)
        for j, sh_name in enumerate(shareholders):
            if j == len(shareholders) - 1:
                stake = remaining_stake
            else:
                stake = random.uniform(3.0, 7.0)
            
            if remaining_stake - stake < 0:
                stake = remaining_stake
            
            major_shareholders.append({"name": sh_name, "stake": round(stake, 2)})
            remaining_stake -= stake
        
        earnings_forecast = {
            "sales_growth": round(random.uniform(-0.02, 0.10), 3),
            "profit_growth": round(random.uniform(-0.05, 0.15), 3)
        }
        
        chosen_tier_name = random.choices(tiers, weights=weights, k=1)[0]
        tier_range = constants.MARKET_CAP_TIERS[chosen_tier_name]
        market_cap = random.uniform(tier_range["min"], tier_range["max"])
        market_cap = round(market_cap / 1_000_000) * 1_000_000

        initial_price = random.uniform(constants.INITIAL_STOCK_PRICE_RANGE[0], constants.INITIAL_STOCK_PRICE_RANGE[1])
        initial_price = max(1.0, round(initial_price))

        shares_outstanding = max(1, int(round(market_cap / initial_price))) if initial_price > 0 else 0
        market_cap = initial_price * shares_outstanding 

        initial_pbr = random.uniform(constants.INITIAL_PBR_MULTIPLIER_RANGE[0], constants.INITIAL_PBR_MULTIPLIER_RANGE[1])

        company = ListedCompany(
            ticker_symbol=ticker, company_name=name, sector=sector,
            initial_market_cap=market_cap, initial_price=initial_price,
            shares_outstanding=shares_outstanding, founded_year=founded_year,
            initial_pbr_multiplier=initial_pbr,
            description=description,
            major_shareholders=major_shareholders,
            earnings_forecast=earnings_forecast
        )
        listed_companies_on_market.append(company)
    
    print(f"{num_companies}社の一般上場企業が市場に生成されました。")

def update_all_stock_prices_and_events(game_time: GameTime, player: Player):
    """市場に上場している全企業の株価とイベントを更新する。"""
    if not listed_companies_on_market: return
    
    current_economic_phase = game_time.current_economic_phase
    for company in listed_companies_on_market:
        if company.is_subsidiary and company.ticker_symbol != player.ipo.company_ticker_symbol:
            continue
        
        company.update_stock_price(current_economic_phase)
        company.process_earnings_announcement(game_time)
        company.process_dividend_payment(player, game_time)

    from systems import competitor_ai_system
    if competitor_ai_system and competitor_ai_system.competitor_companies:
        for comp in competitor_ai_system.competitor_companies:
            if hasattr(comp, 'is_company_public') and comp.is_company_public:
                comp.update_stock_price(current_economic_phase)
                comp.process_earnings_announcement(game_time)

def show_market_overview():
    """一般株式市場の概況(銘柄一覧など)を表示する"""
    if not listed_companies_on_market:
        print("現在、市場に上場している企業はありません。")
        return

    print("\n--- 一般株式市場 銘柄一覧 ---")
    for i, company in enumerate(listed_companies_on_market):
        print(f"  {i+1:<2}. {company.company_name} ({company.ticker_symbol}) - 株価: ¥{company.current_price:,.2f}")

def display_detailed_stock_info(company: ListedCompany):
    """企業の詳細情報を表示する"""
    print("\n" + "="*50)
    print(f"企業詳細: {company.company_name} ({company.ticker_symbol})")
    print("="*50)
    
    print(f"\n【企業概要】")
    print(f"  {company.description}")
    print(f"  セクター: {company.sector} | 設立: {company.founded_year}年")

    print("\n【主要株主】")
    for shareholder in company.major_shareholders:
        print(f"  - {shareholder['name']}: {shareholder['stake']:.2f}%")

    print("\n【財務指標】")
    print(f"  株価: ¥{company.current_price:,.2f}")
    print(f"  時価総額: ¥{company.market_cap:,.0f}")
    print(f"  PER (株価収益率): {company.p_e_ratio:.2f}倍")
    print(f"  PBR (株価純資産倍率): {company.get_pbr_ratio():.2f}倍")
    print(f"  配当利回り (年率): {company.get_current_annual_dividend_yield_estimate()*100:.2f}%")

    print("\n【業績推移 (四半期)】")
    if not company.quarterly_results_history:
        print("  業績データがありません。")
    else:
        for result in company.quarterly_results_history:
            print(f"  - {result['year']}年 第{result['quarter']}四半期: 売上 ¥{result['sales']:,.0f}, 純利益 ¥{result['profit']:,.0f}")

    print("\n【業績予想】")
    forecast = company.earnings_forecast
    print(f"  来期売上成長率予測: {forecast['sales_growth']:.2%}")
    print(f"  来期純利益成長率予測: {forecast['profit_growth']:.2%}")
    
    print("\n" + "="*50)

def select_owner(player: Player) -> Optional[str]:
    """取引の主体(会社か個人か)を選択させる"""
    print("\nどちらの資金で取引しますか?")
    print("1: 会社")
    print("2: 個人")
    print("0: キャンセル")
    owner_choice = utils.get_integer_input("選択: ", 0, 2)
    if owner_choice == 1: return "company"
    if owner_choice == 2: return "personal"
    return None

def handle_trade(player: Player, company: ListedCompany, game_time: GameTime, owner_type: str, action: str):
    """実際の売買処理を行う"""
    is_buy = "買い" in action
    is_sell = "売り" in action
    is_margin = "信用" in action
    is_short = "空売り" in action
    is_cover = "買い戻し" in action

    portfolio_to_check = player.company_portfolio if owner_type == "company" else player.personal_portfolio
    
    if is_buy:
        max_fund = player.finance.get_cash() if owner_type == "company" else player.money_personal
        if company.current_price <= 0:
            print("株価が0のため取引できません。"); return
        
        max_buyable = int(max_fund / company.current_price)
        if is_margin:
            max_buyable = int(max_fund / (company.current_price * constants.INITIAL_MARGIN_REQUIREMENT_RATIO))
        
        prompt = f"何株購入しますか? (最大: {max_buyable:,}株): "
        num_shares = utils.get_integer_input(prompt, 1, max_buyable if max_buyable > 0 else None)
        if num_shares:
            if is_margin:
                if player.buy_stock_on_margin(owner_type, company.ticker_symbol, company.company_name, num_shares, company.current_price):
                    print("信用買い付けが完了しました。")
            else:
                if player.buy_stock_on_cash(owner_type, company.ticker_symbol, company.company_name, num_shares, company.current_price):
                    print("現物買い付けが完了しました。")

    elif is_sell:
        holding = portfolio_to_check.general_stock_portfolio.get(company.ticker_symbol)
        if not holding:
            print("その銘柄は保有していません。"); return
        
        max_sellable = holding.get('cash_shares', 0) + holding.get('margin_shares', 0)
        prompt = f"何株売却しますか? (最大: {max_sellable:,}株): "
        num_shares = utils.get_integer_input(prompt, 1, max_sellable)
        if num_shares:
            if player.sell_stock(owner_type, company.ticker_symbol, num_shares, company.current_price):
                print("株式を売却しました。")
    
    elif is_short:
        prompt = f"何株空売りしますか?: "
        num_shares = utils.get_integer_input(prompt, 1)
        if num_shares:
            if player.short_sell_stock(owner_type, company.ticker_symbol, company.company_name, num_shares, company.current_price, game_time):
                print("空売りが完了しました。")
            
    elif is_cover:
        position = portfolio_to_check.short_positions.get(company.ticker_symbol)
        if not position:
            print("その銘柄の空売りポジションはありません。"); return
        
        max_coverable = position['shares']
        prompt = f"何株買い戻しますか? (最大: {max_coverable:,}株): "
        num_shares = utils.get_integer_input(prompt, 1, max_coverable)
        if num_shares:
            if player.buy_to_cover_short(owner_type, company.ticker_symbol, num_shares, company.current_price):
                print("買い戻しが完了しました。")

def trade_stocks_menu(player: Player, game_time: GameTime):
    """銘柄を選択し、取引アクションを選択させる"""
    show_market_overview()
    ticker_to_find = input("取引したい銘柄のティッカーシンボルを入力 (0で戻る): ").strip().upper()
    if not ticker_to_find or ticker_to_find == '0': return
    
    selected_company = next((c for c in listed_companies_on_market if c.ticker_symbol == ticker_to_find), None)
    if not selected_company:
        print("銘柄が見つかりません。"); return
        
    display_detailed_stock_info(selected_company)

    owner = select_owner(player)
    if not owner: return
    
    actions = ["現物買い", "売り"]
    portfolio_to_check = player.company_portfolio if owner == "company" else player.personal_portfolio
    if portfolio_to_check.has_margin_account:
        actions.extend(["信用買い", "空売り", "買い戻し"])
    
    print("\n取引の種類を選択してください:")
    for i, action in enumerate(actions):
        print(f"  {i+1}: {action}")
    print("  0: キャンセル")
    
    action_choice = utils.get_integer_input("選択: ", 0, len(actions))
    if action_choice is None or action_choice == 0: return
    
    selected_action = actions[action_choice - 1]
    handle_trade(player, selected_company, game_time, owner, selected_action)

def manage_margin_account(player: Player):
    """信用取引口座の開設を管理する"""
    print("\n--- 信用取引口座の管理 ---")
    owner_type = select_owner(player)
    if not owner_type: return

    portfolio = player.company_portfolio if owner_type == "company" else player.personal_portfolio
    
    if portfolio.has_margin_account:
        print(f"{owner_type.capitalize()} は既に信用取引口座を持っています。")
        return

    print("信用取引口座を開設すると、手持ち資金以上の取引(信用買い)や、株を借りて売る(空売り)が可能になります。")
    print("ただし、追証のリスクが伴います。")
    print(f"開設費用: ¥{constants.MARGIN_ACCOUNT_OPENING_COST:,.0f}")
    
    confirm = input("口座を開設しますか? (y/n): ").lower()
    if confirm == 'y':
        if player.open_margin_account(owner_type):
            print(f"{owner_type.capitalize()} の信用取引口座を開設しました。")
        else:
            print("口座開設に失敗しました。")
    else:
        print("口座開設をキャンセルしました。")

def view_player_portfolio(player: Player):
    """プレイヤーの保有ポートフォリオを表示する"""
    market_data = listed_companies_on_market
    print(reporting_system.get_portfolio_summary(player, market_data))

def handle_margin_call(player: Player, owner_type: str, shortfall: float, market_data: List[ListedCompany], game_time: GameTime):
    """追証の処理を行う"""
    print("\n" + "!"*50)
    print(f"!!! 【緊急警告】追証が発生しました ({owner_type.capitalize()}) !!!")
    print(f"維持率が{constants.MAINTENANCE_MARGIN_REQUIREMENT_RATIO*100:.0f}%を下回りました。")
    print(f"不足金額: ¥{shortfall:,.0f}")
    print("不足金額を入金するか、ポジションの一部を決済して、維持率を回復させる必要があります。")
    print("!"*50)
    
    while shortfall > 0:
        print("\n--- 追証対応 ---")
        print(f"現在の不足金額: ¥{shortfall:,.0f}")
        print("1: 現金を入金して解消する")
        print("2: 保有ポジションを強制決済して解消する")
        
        choice = utils.get_integer_input("選択: ", 1, 2)
        if choice is None:
            print("対応が必要です。選択してください。")
            continue

        if choice == 1:
            if owner_type == "company":
                print(f"個人資産から会社へ入金します。現在の個人資産: ¥{player.money_personal:,.0f}")
                amount = utils.get_integer_input("入金額: ", 1, int(player.money_personal))
                if amount:
                    player.deposit_from_personal_to_company(amount)
            else: # personal
                print("個人の追証を現金で解消するには、他の資産を売却するか、会社から役員報酬を得る必要があります。")
                print("(このメニューからは直接入金できません)")

        elif choice == 2:
            print("\n--- 強制決済を開始します ---")
            portfolio = player.company_portfolio if owner_type == "company" else player.personal_portfolio
            
            positions_to_liquidate = []
            for ticker, holding in portfolio.general_stock_portfolio.items():
                # 信用取引分と現物分を合わせて売却対象とする
                total_shares = holding.get('cash_shares', 0) + holding.get('margin_shares', 0)
                if total_shares > 0:
                    company = next((c for c in market_data if c.ticker_symbol == ticker), None)
                    if company:
                        current_value = total_shares * company.current_price
                        positions_to_liquidate.append({
                            "ticker": ticker,
                            "value": current_value,
                            "shares": total_shares
                        })
            
            positions_to_liquidate.sort(key=lambda x: x['value'], reverse=True)

            if not positions_to_liquidate:
                print("決済できるポジションがありません。破産のリスクがあります。")
                break

            for position in positions_to_liquidate:
                ticker = position["ticker"]
                shares_to_sell = position["shares"]
                
                company = next((c for c in market_data if c.ticker_symbol == ticker), None)
                if not company: continue

                print(f"  ポジション「{company.company_name}」({shares_to_sell}株)を強制的に売却します...")
                player.sell_stock(owner_type, ticker, shares_to_sell, company.current_price)
                
                is_still_margin_call, new_shortfall = player.check_margin_call(owner_type, market_data)
                if not is_still_margin_call:
                    print("...追証は解消されました。")
                    shortfall = 0 
                    break
                else:
                    shortfall = new_shortfall
                    print(f"  ...まだ不足しています。不足額: ¥{shortfall:,.0f}")
            
            if shortfall > 0:
                print("全てのポジションを売却しましたが、追証を解消できませんでした。")
            break
            
        is_still_margin_call, new_shortfall = player.check_margin_call(owner_type, market_data)
        if not is_still_margin_call:
            print("追証は解消されました。")
            break
        else:
            shortfall = new_shortfall

def show_general_stock_market_menu(player: Player, game_time: GameTime):
    """一般株式市場のメインメニュー"""
    while True:
        print("\n--- 一般株式市場 ---")
        print("1: 市場概況・銘柄一覧を見る")
        print("2: 株式を売買する")
        print("3: 保有ポートフォリオを見る")
        print("4: 信用取引口座を管理する")
        print("0: 前のメニューに戻る")

        choice = utils.get_integer_input("選択: ", 0, 4)
        if choice is None or choice == 0: break
        
        if choice == 1:
            show_market_overview()
            ticker = input("詳細を見たい銘柄のティッカーシンボルを入力 (Enterのみで戻る): ").strip().upper()
            if ticker:
                company = next((c for c in listed_companies_on_market if c.ticker_symbol == ticker), None)
                if company:
                    display_detailed_stock_info(company)
                else:
                    print("銘柄が見つかりません。")
        elif choice == 2:
            trade_stocks_menu(player, game_time)
        elif choice == 3:
            view_player_portfolio(player)
        elif choice == 4:
            manage_margin_account(player)
