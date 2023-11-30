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
        bridge_entity = self._set_translation_relation(bridge_entity)
        bridge_entity = self._set_media_relation(bridge_entity)
        return bridge_entity

    def _set_translation_relation(self, bridge_entity):
        for translation in bridge_entity.translations:
            try:
                translation_in_db = BridgeCategoryTranslation.query \
                    .filter(BridgeCategoryTranslation.name == translation.name) \
                    .filter(BridgeCategoryTranslation.language == translation.language) \
                    .one_or_none()
                if translation_in_db:
                    translation.id = translation_in_db.id

            except NoResultFound:
                self.logger.info("No Translation found")
                # Translation not found in the database
                continue
            except MultipleResultsFound:
                # More than one translation with the same name found in the database
                self.logger.warning(f"Multiple translations found for name: {translation.name}")
            except Exception as e:
                # Handle other unexpected errors
                self.logger.error(f"An error occurred while setting translation relation: {str(e)}")
        self.logger.info("Returning bridge_entity from set_translations")
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

