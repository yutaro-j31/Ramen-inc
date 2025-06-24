# models/map_point.py
from typing import Any, Tuple, Optional

class MapPoint:
    """
    地図上の個別の地点(建物など)を表すクラス。
    """
    def __init__(self, name: str, point_type: str, coordinates: Tuple[int, int], linked_object: Optional[Any] = None):
        self.name: str = name
        # 例:「新宿の空き店舗」「みずほ銀行 渋谷支店」
        self.point_type: str = point_type
        # "VACANT_SHOP", "BANK", "REAL_ESTATE", "SECURITIES"など
        self.coordinates: Tuple[int, int] = coordinates
        # 将来のグラフィック用 (x, y) 座標
        self.linked_object: Optional[Any] = linked_object
        # 実際のPropertyオブジェクトやBankオブジェクトなどへの参照

    def __str__(self) -> str:
        # point_typeを日本語に変換する辞書
        type_display = {
            "VACANT_SHOP": "空き店舗",
            "REAL_ESTATE": "不動産",
            "BANK": "銀行",
            "SECURITIES": "証券会社"
        }
        display_name = type_display.get(self.point_type, self.point_type)
        return f"[{display_name}] {self.name}"

