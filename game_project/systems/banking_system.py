# systems/banking_system.py
import random
from typing import List, Dict, Any, Optional

from models.player import Player
from models.game_time import GameTime
import constants
import utils


# --- 銀行機能 ---

def show_loan_status(player: Player):
    """現在のローンと社債の状況を詳細に表示する"""
    print("\n--- 現在の負債状況 ---")
    
    # 銀行ローン
    if not player.finance.active_loans:
        print("  銀行からの借入金はありません。")
    else:
        print(f"  銀行借入金総額: ¥{player.finance.get_total_bank_loan():,.0f}")
        print("  ローン契約一覧:")
        for i, loan in enumerate(player.finance.active_loans):
            print(f"    {i+1}. ID: ...{loan.loan_id[-6:]} | {loan.lender_name}「{loan.product_name}」")
            print(f"        残高: ¥{loan.remaining_principal:,.0f}, 週利: {loan.weekly_rate:.4%}, 返済進捗: {loan.weeks_repaid}/{loan.total_weeks}週")

    # 社債
    if not player.finance.outstanding_bonds:
        print("\n  発行済みの社債はありません。")
    else:
        print(f"\n  社債発行残高: ¥{player.finance.get_total_bonds_payable():,.0f}")
        print("  発行済み社債一覧:")
        for i, bond in enumerate(player.finance.outstanding_bonds):
            print(f"    {i+1}. {bond}")


def take_out_loan(player: Player, game_time: GameTime):
    """ローンを組む"""
    print("\n--- ローン借入 ---")
    if not constants.BANK_LOAN_PRODUCTS:
        print("現在、利用可能なローン商品がありません。")
        return

    print(f"あなたの会社の現在の信用格付け: {player.credit_rating} (スコア: {player.credit_rating_score})")
    print("  (格付けが高いほど、より有利な条件で融資を受けられます)")

    if player.finance.active_loans:
        print(f"注意: 現在既に {len(player.finance.active_loans)} 件のローン契約があります。総負債額: ¥{player.finance.get_total_bank_loan():,.0f}")
    
    print("\n利用可能なローン商品:")
    
    customized_loan_products = []
    for product in constants.BANK_LOAN_PRODUCTS:
        modifiers = constants.CREDIT_RATING_LOAN_MODIFIERS.get(player.credit_rating, {})
        interest_adjustment = modifiers.get("interest_rate_adjustment", 0.0)
        loan_multiplier = modifiers.get("max_loan_multiplier", 1.0)
        customized_rate = product['interest_rate_weekly'] + interest_adjustment
        customized_max_amount = int(product['max_amount'] * loan_multiplier)

        customized_product_info = product.copy()
        customized_product_info['customized_rate'] = max(0.0001, customized_rate)
        customized_product_info['customized_max_amount'] = customized_max_amount
        customized_loan_products.append(customized_product_info)

    for i, product in enumerate(customized_loan_products):
        print(f"  {i+1}. {product['bank_name']} - {product['product_name']}")
        print(f"      あなたの条件 -> 最大融資額: ¥{product['customized_max_amount']:,.0f}, 週利: {product['customized_rate']*100:.3f}%")
        print(f"      (基本条件: 最大 ¥{product['max_amount']:,.0f}, 週利 {product['interest_rate_weekly']*100:.3f}%)")

    product_choice = utils.get_integer_input(
        f"ローン商品を選択してください (1-{len(customized_loan_products)}, 0でキャンセル): ", 0, len(customized_loan_products)
    )
    if product_choice is None or product_choice == 0:
        print("ローン借入をキャンセルしました。"); return

    selected_product = customized_loan_products[product_choice - 1]
    max_loan_amount = selected_product['customized_max_amount']
    
    if max_loan_amount <= 0:
        print("あなたの現在の信用格付けでは、このローン商品を借りることはできません。"); return

    loan_amount_prompt = f"借入希望額を入力してください (最大 ¥{max_loan_amount:,.0f}): "
    amount_to_borrow_input = utils.get_integer_input(loan_amount_prompt, 1, int(max_loan_amount))
    
    if amount_to_borrow_input is None:
        print("ローン借入をキャンセルしました。"); return
    
    player.take_loan(
        amount=float(amount_to_borrow_input), 
        weekly_rate=float(selected_product['customized_rate']),
        lender_name=selected_product['bank_name'],
        product_name=selected_product['product_name'],
        repayment_weeks=selected_product['repayment_weeks'],
        game_time=game_time 
    )


def repay_loan_action(player: Player, game_time: GameTime): 
    """プレイヤーに返済するローンを選択させ、返済処理を行う。"""
    print("\n--- ローン返済 ---")
    if not player.finance.active_loans:
        print("現在、返済可能なローンはありません。"); return

    print("返済するローンを選択してください:")
    for i, loan in enumerate(player.finance.active_loans):
        print(f"  {i+1}. {loan}")
    print("  0. キャンセル")
    
    loan_choice = utils.get_integer_input("選択: ", 0, len(player.finance.active_loans))
    if loan_choice is None or loan_choice == 0:
        print("ローン返済をキャンセルしました。"); return

    selected_loan = player.finance.active_loans[loan_choice - 1]
    
    print(f"\n--- 「{selected_loan.product_name}」(ID: ...{selected_loan.loan_id[-6:]}) の返済 ---")
    print(f"  現在のローン残高: ¥{selected_loan.remaining_principal:,.0f}")
    
    max_repayment = min(player.finance.get_cash(), selected_loan.remaining_principal)
    if max_repayment <= 0:
        print("現在、このローンに対して返済できる資金がありません。"); return

    repayment_amount_prompt = f"返済額を入力してください (最大 ¥{max_repayment:,.0f}, 'full'で残高全額): "
    
    amount_to_repay = None
    while True:
        user_input = input(repayment_amount_prompt).strip().lower()
        if user_input == 'full':
            amount_to_repay = selected_loan.remaining_principal
            break
        try:
            amount_to_repay = float(user_input)
            if amount_to_repay <= 0:
                print("返済額は0より大きい値を入力してください。")
            elif amount_to_repay > max_repayment:
                print(f"返済額が返済可能額 (¥{max_repayment:,.0f}) を超えています。")
            else:
                break
        except ValueError:
            print("有効な数値を入力してください。")
            
    if amount_to_repay is None or amount_to_repay <= 0:
        print("ローン返済を中止しました。"); return

    player.repay_loan(selected_loan.loan_id, amount_to_repay)


def issue_bond_menu(player: Player, game_time: GameTime):
    """社債発行のメニュー"""
    print("\n--- 社債発行 (投資銀行業務) ---")
    if not player.is_company_public:
        print("社債を発行できるのは上場企業のみです。")
        return

    rating = player.credit_rating
    spread = constants.BOND_CREDIT_SPREADS.get(rating)
    if spread is None:
        print(f"あなたの会社の信用格付け({rating})では、社債を発行できません。")
        return

    print(f"現在の信用格付け: {rating}")
    estimated_coupon_rate = constants.BOND_BASE_YIELD + spread
    print(f"  -> これに基づき発行利率 (年利) の目安: {estimated_coupon_rate:.2%}")

    principal = utils.get_integer_input("発行希望額(額面)を入力してください (例: 100000000): ", 10_000_000)
    if principal is None: return

    print("発行年数を選択してください:")
    for i, year in enumerate(constants.BOND_MATURITY_YEARS_OPTIONS):
        print(f"  {i+1}: {year}年債")
    year_choice = utils.get_integer_input("選択: ", 1, len(constants.BOND_MATURITY_YEARS_OPTIONS))
    if year_choice is None: return
    maturity_years = constants.BOND_MATURITY_YEARS_OPTIONS[year_choice - 1]
    
    fee = principal * constants.BOND_ISSUANCE_FEE_RATE
    net_proceeds = principal - fee

    print("\n--- 社債発行内容の確認 ---")
    print(f"  発行額 (額面): ¥{principal:,.0f}")
    print(f"  年数: {maturity_years}年")
    print(f"  年利 (クーポンレート): {estimated_coupon_rate:.2%}")
    print(f"  発行手数料 ({constants.BOND_ISSUANCE_FEE_RATE:.1%}): ¥{fee:,.0f}")
    print(f"  手取額 (会社現金に加算): ¥{net_proceeds:,.0f}")
    
    confirm = input("この条件で社債を発行しますか? (y/n): ").lower()
    if confirm == 'y':
        if player.finance.get_cash() >= fee:
            player.finance.finances['cash'] -= fee 
            player.issue_bond(
                principal=float(principal),
                annual_coupon_rate=estimated_coupon_rate,
                maturity_years=maturity_years,
                game_time=game_time
            )
        else:
            print("発行手数料を支払うための現金が不足しています。")
    else:
        print("社債の発行をキャンセルしました。")


def show_banking_menu(player: Player, game_time: GameTime):
    """銀行システムのメインメニューを表示・処理する"""
    while True:
        print("\n--- 銀行・資金調達 ---")
        print(f"  あなたの会社の信用格付け: {player.credit_rating} (スコア: {player.credit_rating_score})")
        show_loan_status(player) 
        
        print("\n  1: ローンを組む (銀行融資)")
        print("  2: ローンを返済する")
        
        next_option = 3
        if player.is_company_public:
            print(f"  {next_option}: 社債を発行する (市場調達)")
        
        print("  0: 前のメニューに戻る")

        max_choice = next_option if player.is_company_public else 2
        choice = utils.get_integer_input("選択: ", 0, max_choice)
        if choice is None: continue

        if choice == 1:
            take_out_loan(player, game_time) 
        elif choice == 2:
            repay_loan_action(player, game_time)
        elif choice == 3 and player.is_company_public:
            issue_bond_menu(player, game_time)
        elif choice == 0:
            break

def get_customized_loan_products(player: Player) -> List[Dict[str, Any]]:
    """プレイヤーの信用格付けに応じてカスタマイズされたローン商品リストを返す"""
    customized_products = []
    
    # ★★★ 1. 現在借りているローンの商品名リストを作成 ★★★
    active_loan_product_names = {loan.product_name for loan in player.finance.active_loans}
    
    for product in constants.BANK_LOAN_PRODUCTS:
        # ★★★ 2. 既に借りているローンはリストから除外 ★★★
        if product['product_name'] in active_loan_product_names:
            continue

        modifiers = constants.CREDIT_RATING_LOAN_MODIFIERS.get(player.credit_rating, {})
        interest_adjustment = modifiers.get("interest_rate_adjustment", 0.0)
        loan_multiplier = modifiers.get("max_loan_multiplier", 1.0)
        
        customized_rate = product['interest_rate_weekly'] + interest_adjustment
        customized_max_amount = int(product['max_amount'] * loan_multiplier)
        
        custom_product = product.copy()
        custom_product['customized_rate'] = max(0.0001, customized_rate)
        custom_product['customized_max_amount'] = customized_max_amount
        customized_products.append(custom_product)
        
    return customized_products
