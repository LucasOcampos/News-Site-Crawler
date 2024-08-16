class WrongLocation(Exception):
    def __init__(self):
        super().__init__("Browser ended up at a incorrect url.")
