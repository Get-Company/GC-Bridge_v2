from abc import abstractmethod
from pprint import pprint

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
        # self.logger.info("%s initialized successfully for dataset: %s", self.__class__.__name__, self._dataset_entity.get_dataset_name())
        self.token_counter = 0
        self.db = db
        self.db.session.autoflush = False
        self._bridge_controller = bridge_controller
        self.search_value = None
        if search_value:
            self.search_value = search_value

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
    These Methods must be overwritten. If there is no use of it simply do a pass!
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
        id_list = []
        while not self._dataset_entity.range_eof():
            self.logger.info(f"Next Element in range: {self._dataset_entity}")
            id = self.upsert()
            if id:
                id_list.append(id)
            self._dataset_entity.range_next()
        if id_list:
            return id_list
        return True

    def sync_all_from_bridge(self, bridge_entities):
        for bridge_entity in bridge_entities:
            self.downsert(bridge_entity=bridge_entity)

    def sync_one_to_bridge(self):
        id = self.upsert()
        if id:
            return id

    def sync_one_from_bridge(self, bridge_entity):
        self.downsert(bridge_entity=bridge_entity)

    def sync_changed_to_bridge(self):
        pass

    def sync_changed_from_bridge(self, bridge_entities):
        pass

    def upsert(self):
        """
        Inserts or updates the BridgeEntity in the database based on whether it already exists or not.
        This method maps the ERPDataset to the BridgeObject, then checks if this entity is already
        present in the database. If the entity exists, it updates the entity, otherwise, it inserts a new one.
        :param args: Positional arguments passed to map_erp_to_bridge method.
        :param kwargs: Keyword arguments passed to map_erp_to_bridge method.
        """
        self.logger.info("Starting the upsert process.")
        try:
            # Map the data to a new bridge entity
            bridge_entity_new = self._dataset_entity.map_erp_to_bridge()
        except Exception as e:
            self.logger.error(f"Failed to map ERP dataset to new BridgeEntity: {e}")
            return

        try:
            # Check for existing entity
            bridge_entity_in_db = self.is_in_db(bridge_entity_new=bridge_entity_new)
        except Exception as e:
            self.logger.error(f"Failed to check if entity exists in DB: {e}")
            return

        if bridge_entity_in_db:
            self.logger.info(f"Entity found in DB, preparing to update: {bridge_entity_in_db}")
            bridge_entity_for_db = bridge_entity_in_db.update(bridge_entity_new=bridge_entity_new)
            self.db.session.merge(bridge_entity_for_db)
        else:
            self.logger.info("No existing entity found in DB, preparing to insert new entity.")
            bridge_entity_for_db = bridge_entity_new
            self.db.session.add(bridge_entity_for_db)

        try:
            # Flush it first, for we have the relations to set
            self.db.session.flush()
        except Exception as e:
            self.logger.error(f"Failed to flush DB session: {e}")
            return
        try:
            # Refresh the entity, to get it back from the flush with its id
            self.db.session.refresh(bridge_entity_for_db)
        except Exception as e:
            self.logger.error(f"Failed to refresh entity: {e}")
            return

        self.db.session.add(bridge_entity_for_db)

        try:
            # Set relations
            bridge_entity_for_db_with_relations = self.set_relations(bridge_entity_for_db)
            self.logger.info("Set relations for the entity.")
        except Exception as e:
            self.logger.error(f"Failed to set entity relations: {e}")
            return
        try:
            self.db.session.merge(bridge_entity_for_db_with_relations)
        except Exception as e:
            self.logger.error(f"Failed to merge entity with its relations into the session: {e}")
            return
        try:
            entity_id = bridge_entity_for_db_with_relations.get_id()
            print("Upserting", bridge_entity_for_db_with_relations)
            self.db.session.commit()
            self.logger.info(f"Entity successfully upserted with ID: {entity_id}")
            return entity_id
        except Exception as e:
            self.logger.error(f"Failed to commit changes to DB: {e}")

    # Direction to ERP
    def downsert(self, bridge_entity):
        erp_entity = self.get_entity().map_bridge_to_erp(bridge_entity=bridge_entity)

    @abstractmethod
    def is_in_db(self, bridge_entity_new):
        pass

    @abstractmethod
    def set_relations(self, bridge_entity):
        pass

    def _set_media_relation(self, bridge_entity):
        """
        Update the media relation for a given bridge product entity.

        :param bridge_entity: The BridgeProductEntity to set media relation for.
        :type bridge_entity: BridgeProductEntity
        :return: BridgeProductEntity with media relation set.
        :rtype: BridgeProductEntity
        """
        medias_list = bridge_entity.media
        for media in medias_list:
            media_in_db = BridgeMediaEntity.query.filter_by(file_name=media.file_name).one_or_none()

            if media_in_db:
                # Aktualisieren Sie hier das media_in_db-Objekt mit den Daten aus media, falls notwendig
                media_in_db.update(media)
                self.db.session.merge(media_in_db)
            else:
                self.db.session.add(media)  # Neues Media-Objekt zur Session hinzufügen
                bridge_entity.media.append(media)

        return bridge_entity

