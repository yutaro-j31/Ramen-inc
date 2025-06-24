# models/region.py
from typing import List
from models.map_point import MapPoint

class Region:
    """
    東京、大阪などの大まかなエリアを表すクラス。
    """
    def __init__(self, name: str, description: str):
        self.name: str = name
        self.description: str = description
        self.map_points: List[MapPoint] = [] # この地域に存在する建物や場所のリスト

    def add_map_point(self, point: MapPoint):
        self.map_points.append(point)

    def __str__(self) -> str:
        return f"{self.name}"

