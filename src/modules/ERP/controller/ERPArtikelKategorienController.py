from ..controller.ERPAbstractController import ERPAbstractController
from ..entities.ERPArtikelKategorienEntity import ERPArtikelKategorienEntity


class ERPArtikelKategorienController(ERPAbstractController):
    def __init__(self, search_value=None, index=None, range_end=None):
        self._dataset_entity = ERPArtikelKategorienEntity(search_value=search_value, index=index, range_end=range_end)

        super().__init__(
            dataset_entity=self._dataset_entity
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

