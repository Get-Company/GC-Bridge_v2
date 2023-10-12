from ..controller.ERPAbstractController import ERPAbstractController
from ..entities.ERPMandantSteuerEntity import ERPMandantSteuerEntity
from src.modules.Bridge.entities.BridgeTaxEntity import BridgeTaxEntity


class ERPMandantSteuerController(ERPAbstractController):
    """
    Examples:
    """

    def set_relations(self, bridge_entity):
        pass

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

