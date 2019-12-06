class LexingError(ValueError):
    pass


class ParsingError(ValueError):

    def __init__(self, message, token, *args: object) -> None:
        super().__init__(*args)
        self.message = message
        self.token = token


class ErrorCounter:

    def __init__(self) -> None:
        self.counter = 0

    def inc(self):
        self.counter += 1

    def reset(self):
        self.counter = 0
