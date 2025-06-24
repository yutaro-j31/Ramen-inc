# constants/map_master_data.py

# 地方(7大都市)のマスターデータ
REGIONS_MASTER = [
    {"name": "東京", "description": "日本の首都。", "rent_base": 500000, "setup_multiplier": 1.5, "sales_modifier": 1.2, "base_weekly_customer_pool": 1000},
    {"name": "大阪", "description": "西日本の経済と文化の中心。", "rent_base": 400000, "setup_multiplier": 1.2, "sales_modifier": 1.1, "base_weekly_customer_pool": 800},
    {"name": "名古屋", "description": "日本の製造業を支える巨大都市。", "rent_base": 350000, "setup_multiplier": 1.0, "sales_modifier": 1.0, "base_weekly_customer_pool": 700},
    {"name": "札幌", "description": "広大な自然に囲まれた北の拠点。", "rent_base": 250000, "setup_multiplier": 0.8, "sales_modifier": 0.9, "base_weekly_customer_pool": 500},
    {"name": "仙台", "description": "東北地方の政治経済の中心。", "rent_base": 280000, "setup_multiplier": 0.8, "sales_modifier": 0.9, "base_weekly_customer_pool": 550},
    {"name": "広島", "description": "歴史と平和の象徴、中国地方の拠点。", "rent_base": 300000, "setup_multiplier": 0.9, "sales_modifier": 0.95, "base_weekly_customer_pool": 600},
    {"name": "福岡", "description": "アジアへの玄関口として栄える九州の中心。", "rent_base": 320000, "setup_multiplier": 1.1, "sales_modifier": 1.05, "base_weekly_customer_pool": 750},
]

# 各地方の建物のマスターデータ
MAP_POINTS_MASTER = {
    "東京": [
        {"name": "渋谷の空き店舗", "point_type": "VACANT_SHOP", "coordinates": (60, 50)},
        {"name": "新宿のオフィスビル", "point_type": "REAL_ESTATE", "coordinates": (40, 55)},
        {"name": "大手町銀行本店", "point_type": "BANK", "coordinates": (50, 40)},
        {"name": "日本橋証券", "point_type": "SECURITIES", "coordinates": (55, 38)},
        # --- この行が追加された物件 ---
        {"name": "渋谷レンタルオフィス", "point_type": "RENTAL_OFFICE", "coordinates": (75, 60)}
    ],
    "大阪": [
        {"name": "心斎橋の空き店舗", "point_type": "VACANT_SHOP", "coordinates": (55, 60)},
        {"name": "梅田の商業ビル", "point_type": "REAL_ESTATE", "coordinates": (50, 50)},
        {"name": "難波銀行", "point_type": "BANK", "coordinates": (52, 65)},
        {"name": "北浜証券取引所前支店", "point_type": "SECURITIES", "coordinates": (60, 45)},
    ],
    "名古屋": [
        {"name": "栄の空き店舗", "point_type": "VACANT_SHOP", "coordinates": (50, 50)},
        {"name": "名駅前銀行", "point_type": "BANK", "coordinates": (40, 50)},
    ],
    "札幌": [
        {"name": "すすきのの空き店舗", "point_type": "VACANT_SHOP", "coordinates": (50, 50)},
        {"name": "大通銀行", "point_type": "BANK", "coordinates": (55, 45)},
    ],
    "仙台": [
        {"name": "一番町の空き店舗", "point_type": "VACANT_SHOP", "coordinates": (50, 50)},
        {"name": "青葉通証券", "point_type": "SECURITIES", "coordinates": (55, 55)},
    ],
    "広島": [
        {"name": "本通の空き店舗", "point_type": "VACANT_SHOP", "coordinates": (50, 50)},
        {"name": "紙屋町銀行", "point_type": "BANK", "coordinates": (45, 55)},
    ],
    "福岡": [
        {"name": "天神の空き店舗", "point_type": "VACANT_SHOP", "coordinates": (50, 50)},
        {"name": "博多駅前証券", "point_type": "SECURITIES", "coordinates": (60, 55)},
        {"name": "博多駅前のビル", "point_type": "REAL_ESTATE", "coordinates": (62, 50)},
    ],
}
