# constants/property_master_data.py

PROPERTIES_MASTER = [
    {
        "name": "新宿のオフィスビル",
        "property_type": "オフィス",
        "location": "東京",
        "purchase_price": 200_000_000,
        "weekly_rent_income": 1_500_000,
        "weekly_maintenance_cost": 200_000
    },
    {
        "name": "銀座の商業ビル",
        "property_type": "商業施設",
        "location": "東京",
        "purchase_price": 500_000_000,
        "weekly_rent_income": 3_000_000,
        "weekly_maintenance_cost": 500_000
    },
    {
        "name": "梅田の商業ビル",
        "property_type": "商業施設",
        "location": "大阪",
        "purchase_price": 180_000_000,
        "weekly_rent_income": 1_300_000,
        "weekly_maintenance_cost": 180_000
    },
    {
        "name": "博多駅前のビル",
        "property_type": "オフィス",
        "location": "福岡",
        "purchase_price": 150_000_000,
        "weekly_rent_income": 1_100_000,
        "weekly_maintenance_cost": 150_000
    },
    # --- ここからが追加された物件 ---
    {
        "name": "渋谷レンタルオフィス",
        "property_type": "レンタルオフィス",
        "location": "東京",
        "purchase_price": 20000000, # 契約金
        "weekly_rent_income": 0,
        "weekly_maintenance_cost": 2000000 # 週次賃料
    }
]
