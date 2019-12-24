class SlotDispenser:

    def __init__(self) -> None:
        self.current_slot = 0

    def get_slot(self, of_size):
        current = self.current_slot
        self.current_slot += of_size
        return current

    def reset(self):
        self.current_slot = 0
