# systems/save_load_system.py
# 省略なしの完全なコードです。

import pickle
import os
from typing import Dict, Any

# --- グローバル変数 ---
SAVE_FILE_NAME = "savegame.dat"

def save_game(game_state: Dict[str, Any]):
    """
    現在のゲーム状態をファイルに保存する。
    """
    try:
        with open(SAVE_FILE_NAME, 'wb') as f: # 'wb'はバイナリ書き込みモード
            pickle.dump(game_state, f)
        print(f"\n[システム] ゲームの状態を '{SAVE_FILE_NAME}' に保存しました。")
        return True
    except Exception as e:
        print(f"\n[エラー] ゲームの保存に失敗しました: {e}")
        return False

def load_game() -> Dict[str, Any] | None:
    """
    ファイルからゲーム状態を読み込む。
    """
    if not os.path.exists(SAVE_FILE_NAME):
        print(f"\n[システム] セーブファイル '{SAVE_FILE_NAME}' が見つかりません。")
        return None
        
    try:
        with open(SAVE_FILE_NAME, 'rb') as f: # 'rb'はバイナリ読み込みモード
            game_state = pickle.load(f)
        print(f"\n[システム] '{SAVE_FILE_NAME}' からゲームの状態を読み込みました。")
        return game_state
    except Exception as e:
        print(f"\n[エラー] ゲームの読み込みに失敗しました: {e}")
        return None

def has_save_data() -> bool:
    """セーブデータの存在を確認する。"""
    return os.path.exists(SAVE_FILE_NAME)
# (ファイルの末尾などに追加)
def delete_save_data():
    """セーブデータを削除する。"""
    if has_save_data():
        try:
            os.remove(SAVE_FILE_NAME)
            print(f"[システム] セーブファイル '{SAVE_FILE_NAME}' を削除しました。")
            return True
        except Exception as e:
            print(f"[エラー] セーブファイルの削除に失敗しました: {e}")
            return False
    return True # ファイルがなくても削除成功とみなす
