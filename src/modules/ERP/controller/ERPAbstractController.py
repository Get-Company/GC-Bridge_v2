from abc import abstractmethod
from src import db

from ..ERPCoreController import ERPCoreController
from ..entities.ERPAbstractEntity import ERPAbstractEntity
from src.modules.Bridge.entities.BridgeMediaEntity import BridgeMediaEntity


class ERPAbstractController(ERPCoreController):
    """
    Abstract Controller class for ERP dataset operations.

    The Abstract Controller Class holds all general methods and attributes, which are needed for
    all child classes.

    Attributes:
        dataset_entity: An instance of ERPAbstractEntity used for accessing datasets.
    """

    def __init__(self, dataset_entity: ERPAbstractEntity, bridge_controller=None, search_value=None):
        super().__init__()
        """Initialize the ERPAbstractController."""
        self._dataset_entity = dataset_entity
        self.logger.info("%s initialized successfully for dataset: %s", self.__class__.__name__, self._dataset_entity.get_dataset_name())
        self.token_counter = 0
        self.db = db
        self.db.session.autoflush = False
        self._bridge_controller = bridge_controller

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

    def sync_all_to_bridge(self):
        # For Loop through all the datasets
        self.logger.info(f'We have a range to loop of {self._dataset_entity.get_range_count()} items.')
        while not self._dataset_entity.range_eof():
            self.logger.info(f"Next Element in range: {self._dataset_entity}")
            self.upsert()
            self._dataset_entity.range_next()

        return True

    def sync_all_from_bridge(self):
        pass

    def sync_one_to_bridge(self, *args, **kwargs):
        self.upsert(*args, **kwargs)

    def sync_one_from_bridge(self):
        pass

    def sync_changed_to_bridge(self):
        pass

    def sync_changed_from_bridge(self):
        pass

    def upsert(self, *args, **kwargs):
        """
        Inserts or updates the BridgeEntity in the database based on whether it already exists or not.

        This method maps the ERPDataset to the BridgeObject, then checks if this entity is already
        present in the database. If the entity exists, it updates the entity, otherwise, it inserts a new one.

        :param args: Positional arguments passed to map_erp_to_bridge method.
        :param kwargs: Keyword arguments passed to map_erp_to_bridge method.
        """
        try:
            # Map the ERP dataset to a new bridge entity
            bridge_entity_new = self._dataset_entity.map_erp_to_bridge(*args, **kwargs)

            # Set relations
            if bridge_entity_new:
                self.db.session.merge(bridge_entity_new)
                self.set_relations(bridge_entity=bridge_entity_new)

                # Commit the changes (either insert or update) to the database
                self.merge_it(bridge_entity=bridge_entity_new)

        except Exception as e:
            # Log the error
            self.logger.error(f"An unexpected error occurred during the upsert process: {str(e)}")

    @abstractmethod
    def set_relations(self, bridge_entity):
        """
        Establish various relations for a given bridge entity.

        This method provides a framework for setting up relations for the provided
        bridge entity. The actual relation setting mechanisms are expected to be
        implemented in child classes based on their specific requirements. When setting
        relations, it is crucial to invoke `db.session.add` on the bridge entity after
        each relation is established to ensure the integrity of the session and the
        object relationships.

        It's advised for subclasses to follow this practice, and depending on the
        specifics of the child class, this method might need to be overridden or
        extended.

        :param bridge_entity: The BridgeEntity to set relations for.
        :type bridge_entity: BridgeEntity
        :return: BridgeEntity with relations set or prepared to be set.
        :rtype: BridgeEntity
        """
        raise NotImplementedError("Child classes must implement this method.")

    def _set_media_relation(self, bridge_entity):
        """
        Set the media relation for a given bridge product entity.

        :param bridge_entity: The BridgeProductEntity to set media relation for.
        :type bridge_entity: BridgeProductEntity
        :return: BridgeProductEntity with media relation set.
        :rtype: BridgeProductEntity
        """
        medias_list = bridge_entity.media
        for media in medias_list:
            media_in_db = BridgeMediaEntity.query.filter_by(file_name=media.file_name).one_or_none()
            if media_in_db:
                media.id = media_in_db.id
        return bridge_entity

    def merge_it(self, bridge_entity):

        """Merges the new Bridge entity into the database.

        :param bridge_entity: The new Bridge entity to merge.
        :type bridge_entity: BridgeCategoryEntity
        """
        try:
            # Merge entity to session
            # if not self.db.session.is_modified(bridge_entity, include_collections=False):
            #     self.logger.info(f"Entity has changed after setting relations. Merging entity with ERP number again: {bridge_entity.erp_nr}")
            # self.db.session.merge(bridge_entity)
            # self.logger.info("Commiting entity")
            self.db.session.commit()

        except Exception as e:
            self.logger.error(f"An error occurred while merging the entity: {str(e)}")
            self.db.session.rollback()
        finally:
            self.logger.info("Closing connection")
            self.db.session.close_all()
