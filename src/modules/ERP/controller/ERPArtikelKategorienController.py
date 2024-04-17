from pprint import pprint

from sqlalchemy.exc import NoResultFound, MultipleResultsFound

from ..controller.ERPAbstractController import ERPAbstractController
from ..entities.ERPArtikelKategorienEntity import ERPArtikelKategorienEntity
from src.modules.Bridge.controller.BridgeCategoryController import BridgeCategoryController
from src.modules.Bridge.entities.BridgeCategoryEntity import BridgeCategoryEntity, BridgeCategoryTranslation


class ERPArtikelKategorienController(ERPAbstractController):
    def __init__(self, search_value=None, index=None, range_end=None):
        self._dataset_entity = ERPArtikelKategorienEntity(
            search_value=search_value,
            index=index,
            range_end=range_end
        )

        self._bridge_controller = BridgeCategoryController()

        super().__init__(
            dataset_entity=self._dataset_entity,
            bridge_controller=self._bridge_controller
        )

    def set_relations(self, bridge_entity):
        # bridge_entity = self._set_translation_relation(bridge_entity)
        # bridge_entity = self._set_media_relation(bridge_entity)
        return bridge_entity

    def is_in_db(self, bridge_entity_new):
        bridge_entity_in_db = self._bridge_controller.get_entity().query.filter_by(erp_nr=bridge_entity_new.erp_nr).one_or_none()
        if bridge_entity_in_db:
            self.logger.info(f"Entity {bridge_entity_new.erp_nr} found in the db!")
            return bridge_entity_in_db
        else:
            self.logger.info(f"No Entity {bridge_entity_new.erp_nr} found in the db!")
            return None

    def _set_translation_relation(self, bridge_entity):
        try:
            # 1 Map new object
            bridge_category_translation_new = self._dataset_entity.map_erp_translation_to_bridge()

            self.logger.info(f"Looking for Translation: {self._dataset_entity.get_name()} for Category ID: {bridge_entity.id}")

            # 2 Check DB for existing entries
            bridge_category_translation_in_db = BridgeCategoryTranslation.query \
                .filter(BridgeCategoryTranslation.category_id == bridge_entity.id) \
                .filter(BridgeCategoryTranslation.language == "DE_de") \
                .one_or_none()

            if bridge_category_translation_in_db:
                # Update
                bridge_product_translation_for_db = bridge_category_translation_in_db.update(bridge_category_translation_new)
                self.logger.info(f"Updated existing translation: {bridge_category_translation_in_db.id}")
            else:
                # Insert
                bridge_product_translation_for_db = bridge_category_translation_new

            bridge_entity.translations.append(bridge_product_translation_for_db)

        except Exception as e:
            # Unerwarteter Fehler
            self.logger.error(f"An error occurred while setting translation relation: {str(e)}")

        return bridge_entity

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
