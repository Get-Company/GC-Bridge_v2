from ..ERPCoreController import ERPCoreController
from ..entities.ERPAbstractEntity import ERPAbstractEntity
from abc import abstractmethod
from src import db


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
        self.db = db
        self.token_counter = 0

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

    @abstractmethod
    def get_entity(self):
        """
        Retrieve the dataset entity of the controller.

        Abstract Method! Is abstract because:
        - By marking this method as abstract, we ensure that any subclass
          of this class MUST implement this method. This is a way to enforce
          a certain structure on all subclasses.
        - This is useful in large projects or when working with teams to ensure
          that certain methods are always present in subclasses.
        - Additionally, modern IDEs like PyCharm can recognize these abstract methods
          and provide code suggestions/completions based on both parent and child entities.
          This assists developers in correctly implementing necessary methods when creating
          subclasses.

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

    def get_img_files(self):
        img_list = self.get_entity().get_images_file_list()
        if img_list:
            return img_list
        else:
            return False

    """     
    Abstract Methods, defined in ModulesCoreController
    These Methods must bes overwritten. If there is no use of it simply do a pass!
    """

    def sync_all_to_bridge(self):
        # 1. Get all datasets
        dataset = self.get_entity()
        dataset.range_first()

        # 2. For Loop through all the datasets
        while not dataset.range_eof():
            self.upsert()
            dataset.range_next()

        return True

    def sync_all_from_bridge(self):
        pass

    def sync_one_to_bridge(self, dataset=None, id=None):
        self.upsert()

    def sync_one_from_bridge(self):
        pass

    def sync_changed_to_bridge(self):
        pass

    def sync_changed_from_bridge(self):
        pass

    def upsert(self):
        # Map the ERPDataset to the BridgeObject
        bridge_entity_new = self._dataset_entity.map_erp_to_bridge()
        # Query for an existing entry
        bridge_entity_in_db = self.is_in_db(bridge_entity_new)

        if bridge_entity_in_db:
            # Forward the existing id to the new entity
            bridge_entity_new.id = bridge_entity_in_db.id

        # Now merge everything
        self.merge(bridge_entity_new)

    @abstractmethod
    def is_in_db(self, bridge_entity_new):
        """
        This is needed in the child classes. Since we have to do
        a specific search.

        Example:
        erp_nr=bridge_entity_new.erp_nr
        BridgeCategoryEntity.query.filter_by(erp_nr=bridge_entity_new.erp_nr).one_or_none()

        """
        pass

    def merge(self, bridge_entity_new):
        """Merges the new Bridge entity into the database.

        :param bridge_entity_new: The new Bridge entity to merge.
        :type bridge_entity_new: BridgeCategoryEntity
        """
        try:
            self.logger.info(f"Merging entity with ERP number: {bridge_entity_new.erp_nr}")
            text = bridge_entity_new.translations[0].description
            name = bridge_entity_new.translations[0].name
            self.token_counter += self.count_tokens(text=text)
            print(name, self.count_tokens(text=text), "Tokens - Accumulated:", self.token_counter)
            self.db.session.merge(bridge_entity_new)
            self.db.session.commit()
        except Exception as e:
            self.logger.error(f"An error occurred while merging the entity: {str(e)}")
            self.db.session.rollback()
