from ..BridgeCoreController import BridgeCoreController


class BridgeAbstractEntity(BridgeCoreController):
    def __init__(self):
        super().__init__()

    def update(self, bridge_entity_new):
        pass

    # Getter and Setter for id
    def get_id(self):
        return self.id

    def set_id(self, id):
        pass
        try:
            if id is None or id < 0:
                raise ValueError("ID cannot be None or negative.")
            self.id = id
        except ValueError as e:
            print(f"Error setting id: {e}")