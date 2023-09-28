from ..controller.ERPAbstractController import ERPAbstractController
from ..entities.ERPArtikelKategorienEntity import ERPArtikelKategorienEntity
from src.modules.Bridge.entities.BridgeCategoryEntity import BridgeCategoryEntity, BridgeCategoryTranslation


class ERPArtikelKategorienController(ERPAbstractController):
    def __init__(self, search_value=None, index=None, range_end=None):
        self._dataset_entity = ERPArtikelKategorienEntity(search_value=search_value, index=index, range_end=range_end)

        super().__init__(
            dataset_entity=self._dataset_entity
        )

    def is_in_db(self, bridge_entity_new: BridgeCategoryEntity) -> object:
        """
        Checks if a given BridgeCategoryEntity is already present in the database.

        :param bridge_entity_new: The BridgeCategoryEntity to check.
        :type bridge_entity_new: BridgeCategoryEntity
        :return: The existing BridgeCategoryEntity from the database if found, otherwise False.
        :rtype: BridgeCategoryEntity or bool
        """
        try:
            # Attempt to query the database for the given BridgeCategoryEntity.
            self.logger.info(f"Attempting to find BridgeCategoryEntity with ERP number: {bridge_entity_new.erp_nr}")
            entity_in_db = BridgeCategoryEntity.query.filter_by(erp_nr=bridge_entity_new.erp_nr).one_or_none()

            if entity_in_db:
                # If the entity is found in the database, log the success and return the entity.
                self.logger.info(f"BridgeCategoryEntity with ERP number: {bridge_entity_new.erp_nr} found in database.")
                return entity_in_db
            else:
                # If the entity is not found in the database, log the failure and return False.
                self.logger.warning(f"BridgeCategoryEntity with ERP number: {bridge_entity_new.erp_nr} not found in database.")
                return False

        except Exception as e:
            # If any exception occurs while querying the database, log the error and return False.
            self.logger.error(f"An error occurred while querying the database: {str(e)}")
            return False

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


