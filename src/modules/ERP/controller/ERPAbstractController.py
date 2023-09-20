from ..ERPCoreController import ERPCoreController
from ..entities.ERPAbstractEntity import ERPAbstractEntity


class ERPAbstractController(ERPCoreController):
    """
    Abstract Controller class for ERP dataset operations.

    Attributes:
        dataset_entity: An instance of ERPAbstractEntity used for accessing datasets.
    """

    def __init__(self, dataset_entity: ERPAbstractEntity, search_value=None):
        super().__init__()
        """Initialize the ERPAbstractController."""
        self._dataset_entity = dataset_entity
        self.logger.info("%s initialized successfully for dataset: %s", self.__class__.__name__, self._dataset_entity.get_dataset_name())

    def set_entity(self, dataset_entity) -> None:
        """
        Set the dataset entity for the controller.
        """
        try:
            if dataset_entity:
                self._dataset_entity = dataset_entity
                self.logger.info(f"Dataset entity {self._dataset_entity.get_dataset_name()} is set.")
            else:
                raise ValueError("Provided dataset entity is invalid or None.")
        except ValueError as e:
            self.logger.error(f"Error setting dataset entity: {str(e)}")
            raise

    def get_entity(self):
        """
        Retrieve the dataset entity of the controller.

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

    def get_all_dataset_fields(self):
        """
        Fetch all the fields of the dataset.

        Returns:
            A list of dictionaries containing field information.

        Example:
            adr_crl = ERPAdressenController()
            fields = adr_crl.get_all_dataset_fields()
            for field in fields:
                print(field)
        """
        fields = self._dataset_entity.get_all_fields()
        return fields

    def get_all_dataset_indicies(self):
        indices = self._dataset_entity.get_all_indicies()
        return indices

    def get_entity(self):
        return self._dataset_entity
