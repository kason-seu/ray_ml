class TooError(Exception):
    """:raise when a tool eccounters an error"""

    def __init__(self, message):
        self.message = message