# systems/stock_market_system.py
from typing import List, Dict, Any

from models.player import Player
from models.game_time import GameTime
import constants
import utils


# ★★★ このファイル固有の入力受付関数は削除しました ★★★


# --- 株式市場機能 (IPO株関連) ---

def view_owned_stocks(player: Player) -> List[Dict[str, Any]]:
    """プレイヤーが所有している上場株式の一覧を表示する"""
    print("\n--- 保有上場株式一覧 ---")
    
    # player.owned_stocks は personal_assets.portfolio.owned_stocks のショートカットと仮定
    # 実際の Player クラスの構造に合わせて要調整
    owned_stocks_list = player.personal_assets.portfolio.owned_stocks + player.company_portfolio.owned_stocks
    
    if not owned_stocks_list:
        print("現在、保有している上場株式はありません。")
        return []

    # 週次処理で株価は更新済みと想定
    for i, stock_info in enumerate(owned_stocks_list):
        company_name = stock_info.get("company_name", "不明な会社")
        ipo_value = stock_info.get("acquired_value_at_ipo", 0)
        current_value = stock_info.get("current_market_value", ipo_value)
        shares_eq = stock_info.get("shares_equivalent", 0)
        dividend_rate = stock_info.get("annual_dividend_rate", 0) * 100 # %表示
        sector = stock_info.get("sector", "不明")
        
        print(f"  {i+1}. {company_name} (セクター: {sector})")
        print(f"      保有割合(相当): {shares_eq:.1f}%")
        print(f"      IPO時評価額(自社持分): ¥{ipo_value:,.0f}")
        print(f"      現在市場評価額(自社持分): ¥{current_value:,.0f}")
        gain_loss = current_value - ipo_value
        gain_loss_percent = (gain_loss / ipo_value * 100) if ipo_value > 0 else 0
        print(f"      評価損益: ¥{gain_loss:,.0f} ({gain_loss_percent:+.1f}%)")
        print(f"      年間配当利回り(見込): {dividend_rate:.1f}% (IPO時評価額ベース)")
        print("-"*15)
        
    return owned_stocks_list

def sell_stock_action(player: Player):
    """保有株式を売却するアクション"""
    owned_stocks_list = view_owned_stocks(player) # 一覧を表示し、リストを取得
    if not owned_stocks_list:
        return

    choice = utils.get_integer_input(f"売却する株式を選択してください (1-{len(owned_stocks_list)}, 0でキャンセル): ", 0, len(owned_stocks_list))
    if choice is None or choice == 0:
        print("株式売却をキャンセルしました。")
        return

    stock_to_sell_data = owned_stocks_list[choice - 1]
    # ★ player.sell_owned_stock は会社/個人のどちらの資産かを判別する必要がある
    # この部分は、より詳細な実装で調整が必要
    owner_type = stock_to_sell_data.get("owner_type", "company") # 仮に 'company' をデフォルトとする
    stock_deal_id = stock_to_sell_data.get("deal_id") 

    if not stock_deal_id:
        print("エラー: 選択された株式情報に取引IDが見つかりません。売却できません。")
        return

    company_name = stock_to_sell_data.get("company_name", "選択した株式")
    current_value = stock_to_sell_data.get("current_market_value", stock_to_sell_data.get("acquired_value_at_ipo", 0))

    print(f"\n「{company_name}」の株式を現在の評価額 ¥{current_value:,.0f} で売却します。")
    confirm = input("よろしいですか? (y/n): ").lower()
    if confirm == 'y':
        if player.sell_owned_stock(owner_type, stock_deal_id):
            # 成功メッセージは sell_owned_stock メソッド内で表示される想定
            pass
        # else: 失敗メッセージも同様
    else:
        print("株式売却をキャンセルしました。")


def show_stock_market_menu(player: Player, game_time: 'GameTime'):
    """株式市場システム(保有株式管理)のメインメニューを表示・処理する"""
    while True:
        print("\n--- 株式市場 (保有株式管理) ---")
        print("  1: 保有株式一覧・評価額を見る")
        print("  2: 保有株式を売却する")
        print("  0: 前のメニューに戻る")

        choice = utils.get_integer_input("選択: ", 0, 2)
        if choice is None or choice == 0:
            break

        if choice == 1:
            view_owned_stocks(player)
        elif choice == 2:
            sell_stock_action(player)
