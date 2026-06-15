class Inventory:
    def __init__(self):
        self._items = {}

    def add_item(self, name, price, qty):
        self._items[name] = {"price": price, "qty": qty}

    def remove_item(self, name):
        del self._items[name]

    def total_value(self):
        return sum(i["price"] * i["qty"] for i in self._items.values())
