from ..SW6CoreController import SW6CoreController


class SW6AbstractController(SW6CoreController):

    def __init__(self):
        super().__init__()

    def sync_all_to_bridge(self):
        pass

    def sync_all_from_bridge(self):
        pass

    def sync_one_to_bridge(self):
        pass

    def sync_one_from_bridge(self):
        pass

    def sync_changed_to_bridge(self):
        pass

    def sync_changed_from_bridge(self):
        pass