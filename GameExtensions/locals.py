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


INV_IMG_SIZE: Final = (380, 290)
INV_GRID_OFFSET_PROP_TO_W: Final = 1, 36
INV_CELL_SIZE_PROP_TO_W: Final = 1, 8, 0.12
INV_CELL_OFFSET_TO_W: Final = 1, 144, 0

HOTBAR_IMG_SIZE: Final = 365, 50
HOTBAR_POS_OFFSET: Final = 0, 350
HOTBAR_CELL_IMPERFECTION: Final = -0.2, 0.1

FONT_SIZE: Final = 20
ITEM_FONT_NAME: Final = "square-deal"
NUMBER_SIZE: Final = 20, 20
NUMBER_COLOR: Final = 200, 200, 200

MAX_OBJ: Final = 100

SPE_OBJ: Final = {
    "apple": 10,
    "sand": 6
}

ITEM_SPRITE_SIZE: Final = (32, 32)

HOLDABLE: Final = "holdable"
PLACEABLE: Final = "placeable"

CHUNK_SIZE = 40

DIRS = ((1, 0), (0, 1), (-1, 0), (0, -1))

