import random
from typing import Final

N: Final = "n"
NE: Final = "ne"
E: Final = "e"
SE: Final = "se"
S: Final = "s"
SW: Final = "sw"
W: Final = "w"
NW: Final = "nw"
CENTER: Final = "center"


SEED = random.randint(1, 100000)


INV_IMG_SIZE: Final = (380, 290)
INV_GRID_OFFSET_PROP_TO_W: Final = 1, 36
INV_CELL_SIZE_PROP_TO_W: Final = 1, 8, 0.12
INV_CELL_OFFSET_TO_W: Final = 1, 144, 0

CRAFT_IMG_SIZE: Final = 245, 155
CRAFT_POS_OFFSET: Final = 400, 0
CRAFT_CELL_IMPERFECTION: Final = 0, 0

HOTBAR_IMG_SIZE: Final = 365, 50
HOTBAR_POS_OFFSET: Final = 0, 350
HOTBAR_CELL_IMPERFECTION: Final = -0.2, 0.1

FONT_SIZE: Final = 20
ITEM_FONT_NAME: Final = "square-deal"
NUMBER_SIZE: Final = 20, 20
NUMBER_COLOR: Final = 200, 200, 200

MAX_OBJ: Final = 100

# tous les items
APPLE = "apple"
WOOD_BLOCK = "wood_block"
LOG = "log"
STONE = "stone"
IRON_SWORD = "iron_sword"
BOOK = "book"
EMPTY = "empty"
IRON_ORE = "iron_ore"

SPE_OBJ = {
    APPLE: 10,
    IRON_SWORD: 1,
    BOOK: 1
}

ITEM_SPRITE_SIZE: Final = (32, 32)

HOLDABLE: Final = "holdable"
PLACEABLE: Final = "placeable"
SLASHABLE: Final = "sword"
DONT_SLASH = "dont_slash"

CHUNK_SIZE: Final = 40

DIRS: Final = ((1, 0), (0, 1), (-1, 0), (0, -1))

WATER_DECEL: Final = 0.45

ENEMY = "enemy"

RECIPES: Final = (
    (((LOG, LOG, EMPTY),
     (LOG, LOG, EMPTY),
     (EMPTY, EMPTY, EMPTY)),
     WOOD_BLOCK)
)


