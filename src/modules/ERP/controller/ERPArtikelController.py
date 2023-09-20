from ..controller.ERPAbstractController import ERPAbstractController
from ..entities.ERPArtikelEntity import ERPArtikelEntity


class ERPArtikelController(ERPAbstractController):
    def __init__(self, search_value=None):
        self.search_value = search_value
        self.dataset_entity = ERPArtikelEntity(search_value=self.search_value)

        super().__init__(
            dataset_entity=self.dataset_entity,
            search_value=self.search_value
        )

    def get_umsatz(self,  jahr, return_field):
        ums = self.dataset_entity.get_nested_ums(jahr, return_field)
        if ums:
            self.logger.info(f"Umsatz retrieved successfully. {ums}")
        else:
            self.logger.warning("No Umsatz retrieved")
        return ums
