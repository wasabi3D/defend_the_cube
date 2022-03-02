from __future__ import annotations  # Avoid circular import

import typing

if typing.TYPE_CHECKING:  # Avoid circular import
    import GameManager.MainLoopManager as Gm


ROOT: typing.Union[Gm.GameRoot, None] = None
