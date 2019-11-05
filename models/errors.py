class LexingError(ValueError):
    pass


class ParsingError(ValueError):

    def __init__(self, message, token, *args: object) -> None:
        super().__init__(*args)
        self.message = message
        self.token = token
