class NoAvailableSceneException(Exception):
    def __init__(self):
        super().__init__("Couldn't find any game scene.")


class NotASceneObjectException(Exception):
    def __init__(self, message):
        super().__init__(message)
