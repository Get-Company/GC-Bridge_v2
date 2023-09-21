from ..controller.ERPAbstractController import ERPAbstractController
from ..entities.ERPArtikelEntity import ERPArtikelEntity


class ERPArtikelController(ERPAbstractController):
    def __init__(self, search_value=None):
        self.dataset_entity = ERPArtikelEntity(search_value=search_value)

        super().__init__(
            dataset_entity=self.dataset_entity
        )

    def get_entity(self):
        """
        Retrieve the dataset entity of the controller.

        Note: This method is an implementation of the abstract method defined in
        the parent class ERPAbstractController. For a detailed explanation of its purpose
        and behavior, please refer to the documentation in ERPAbstractController.

        Returns:
            Dataset entity.

        Raises:
            ValueError: If dataset entity is not set.
        """
        if self._dataset_entity:
            return self._dataset_entity
        else:
            message = "Dataset entity is not set"
            self.logger.warning(message)
            raise ValueError(message)
        def get_umsatz(self,  jahr, return_field):
            ums = self.dataset_entity.get_nested_ums(jahr, return_field)
            if ums:
                self.logger.info(f"Umsatz retrieved successfully. {ums}")
            else:
                self.logger.warning("No Umsatz retrieved")
            return ums
