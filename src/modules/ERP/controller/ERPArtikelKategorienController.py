from ..controller.ERPAbstractController import ERPAbstractController
from ..entities.ERPArtikelKategorienEntity import ERPArtikelKategorienEntity


class ERPArtikelKategorienController(ERPAbstractController):
    def __init__(self):
        self.dataset_entity = ERPArtikelKategorienEntity()

        super().__init__(
            dataset_entity=self.dataset_entity
        )