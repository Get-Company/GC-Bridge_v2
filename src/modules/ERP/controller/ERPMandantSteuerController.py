from ..controller.ERPAbstractController import ERPAbstractController
from ..entities.ERPMandantSteuerEntity import ERPMandantSteuerEntity
from src.modules.Bridge.entities.BridgeTaxEntity import BridgeTaxEntity


class ERPMandantSteuerController(ERPAbstractController):
    """
    Examples:
    """

    def __init__(self, search_value=None, index=None, range_end=None):
        self._dataset_entity = ERPMandantSteuerEntity(
            search_value=search_value,
            index=index,
            range_end=range_end
        )
        super().__init__(
            dataset_entity=self._dataset_entity
        )
        self._tax_dataset = None

    def set_tax_dataset(self, tax_dataset):
        self._tax_dataset = tax_dataset

    def get_tax_dataset(self):
        if self._tax_dataset:
            return self._tax_dataset
        else:
            self.logger.error("no Tax Dataset is set. Can't return.")

    def is_in_db(self, bridge_entity_new: BridgeTaxEntity) -> object:
        """
        Checks if a given BridgeTaxEntity is already present in the database.

        :param bridge_entity_new: The BridgeTaxEntity to check.
        :type bridge_entity_new: BridgeTaxEntity
        :return: The existing BridgeTaxEntity from the database if found, otherwise False.
        :rtype: BridgeTaxEntity or bool
        """
        try:
            # Attempt to query the database for the given BridgeTaxEntity.
            self.logger.info(f"Attempting to find BridgeTaxEntity with ERP number: {bridge_entity_new.erp_nr}")
            entity_in_db = BridgeTaxEntity.query.filter_by(erp_nr=bridge_entity_new.erp_nr).one_or_none()

            if entity_in_db:
                # If the entity is found in the database, log the success and return the entity.
                self.logger.info(f"BridgeTaxEntity with ERP number: {bridge_entity_new.erp_nr} found in database.")
                return entity_in_db
            else:
                # If the entity is not found in the database, log the failure and return False.
                self.logger.warning(
                    f"BridgeTaxEntity with ERP number: {bridge_entity_new.erp_nr} not found in database.")
                return False

        except Exception as e:
            # If any exception occurs while querying the database, log the error and return False.
            self.logger.error(f"An error occurred while querying the database for BridgeTaxEntity: {str(e)}")
            return False

    def upsert(self, *args, **kwargs):
        # Map the ERPDataset to the BridgeObject
        bridge_entity_new = self._dataset_entity.map_erp_to_bridge(**kwargs)
        # Query for an existing entry
        bridge_entity_in_db = self.is_in_db(bridge_entity_new)

        if bridge_entity_in_db:
            # Forward the existing id to the new entity
            bridge_entity_new.id = bridge_entity_in_db.id

        # Now merge everything
        self.merge(bridge_entity_new)


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

    def get_tax_fields_by_stschl(self, stschl):
        tax_fields = self._dataset_entity.get_tax_fields(stschl=stschl)
        return tax_fields

