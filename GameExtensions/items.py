from GameExtensions.inventory import InventoryObject
from GameManager.resources import load_img


class Apple(InventoryObject):
    SIZE = (32, 32)

    def __init__(self):
        super().__init__("Apple", load_img("resources/items/apple.png", Apple.SIZE))

    def on_use(self):
        print("Apple")

