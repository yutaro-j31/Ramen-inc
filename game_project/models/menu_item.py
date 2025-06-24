# models/menu_item.py

class MenuItem:
    """
    飲食店のメニューアイテムを表すクラス。
    名前、販売価格、原価を持つ。
    """
    def __init__(self, name: str, price: float, cost: float):
        if price < 0 or cost < 0:
            raise ValueError("Price and cost cannot be negative.")
        if cost > price:
            # 警告は出すが、設定自体は許容する(例:客寄せ商品)
            print(f"Warning: Cost (¥{cost:,.2f}) for '{name}' is higher than its price (¥{price:,.2f}).")
        self.name: str = name
        self.price: float = price
        self.cost: float = cost # この原価が変動費の計算に使われる

    def __repr__(self) -> str: # リスト内などで見やすいように __repr__ を採用
        return f"MenuItem(name='{self.name}', price={self.price:,.2f}, cost={self.cost:,.2f})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, MenuItem):
            return NotImplemented
        return self.name == other.name

    def __hash__(self) -> int:
        return hash(self.name)

