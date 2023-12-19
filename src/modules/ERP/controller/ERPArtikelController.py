from pprint import pprint

from sqlalchemy.exc import NoResultFound, MultipleResultsFound

import config
from ..controller.ERPAbstractController import ERPAbstractController
from ..controller.ERPMandantSteuerController import ERPMandantSteuerController
from ..entities.ERPArtikelEntity import ERPArtikelEntity
from ..controller.ERPArtikelKategorienController import ERPArtikelKategorienController
from src.modules.Bridge.entities.BridgeProductEntity import BridgeProductEntity, BridgeProductTranslation
from src.modules.Bridge.entities.BridgeProductEntity import BridgeProductEntity
from src.modules.Bridge.controller.BridgeProductController import BridgeProductController
from src.modules.Bridge.entities.BridgeTaxEntity import BridgeTaxEntity
from src.modules.Bridge.entities.BridgeCategoryEntity import BridgeCategoryEntity
from src.modules.Bridge.entities.BridgeMediaEntity import BridgeMediaEntity
from src.modules.Bridge.controller.BridgePriceController import BridgePriceController


class ERPArtikelController(ERPAbstractController):
    """
    Examples:1

        Get the Bez from the cat of the product 204116
        art_ctrl = ERPArtikelController(204116)
        categories = art_ctrl.get_categories()
        for cat in categories:
            print(ERPArtikelKategorienController(cat).get_entity().get_("Bez"))

        Get the images as a list
        art_ctrl = ERPArtikelController(204116)
        image_paths = art_ctrl.get_img>_files
        if image_paths:
            for img in image_paths:
                print(img)

        Get Tax informations
        art_ctrl = ERPArtikelController(204116)
        fields = art_ctrl.price_infos().items()
        for key,value in fields:
            print(f"{key}: {value}")

    """
    def __init__(self, search_value=None, index=None, range_end=None):
        self._dataset_entity = ERPArtikelEntity(
            search_value=search_value,
            index=index,
            range_end=range_end
        )
        self._bridge_controller = BridgeProductController()

        super().__init__(
            dataset_entity=self._dataset_entity,
            bridge_controller=self._bridge_controller
        )

    def is_in_db(self, bridge_entity_new):
        bridge_product_entity_in_db = self._bridge_controller.get_entity().query.filter_by(erp_nr=bridge_entity_new.erp_nr).one_or_none()
        if bridge_product_entity_in_db:
            self.logger.info(f"Entity {bridge_entity_new.erp_nr} found in the db!")
            return bridge_product_entity_in_db
        else:
            self.logger.info(f"No Entity {bridge_entity_new.erp_nr} found in the db!")
            return None

    """ Relations """
    def set_relations(self, bridge_entity):
        """
        Set various relations for a given bridge entity.

        This method is designed to handle relations for the given bridge entity
        with other entities such as taxes, categories, etc. The individual relations
        are set using helper methods dedicated to each type of relation.

        :param bridge_entity: The BridgeProductEntity to set relations for.
        :type bridge_entity: BridgeProductEntity
        :return: BridgeProductEntity with relations set.
        :rtype: BridgeProductEntity
        """
        # First merge the object to the db

        bridge_entity = self._set_translation_relation(bridge_entity)
        bridge_entity = self._set_price_relation(bridge_entity)
        bridge_entity = self._set_tax_relation(bridge_entity)
        bridge_entity = self._set_category_relation(bridge_entity)
        bridge_entity = self._set_media_relation(bridge_entity)
        return bridge_entity

    def _set_translation_relation(self, bridge_entity):
        try:
            # 1 Map new object
            bridge_product_translation_new = self._dataset_entity.map_erp_translation_to_bridge()
            self.logger.info(f"Looking for Translation: {self._dataset_entity.get_name()} for Product ID: {bridge_entity.id}")

            # 2 Check DB for existing entries
            bridge_product_translation_in_db = BridgeProductTranslation.query \
                .filter(BridgeProductTranslation.product_id == bridge_entity.id) \
                .filter(BridgeProductTranslation.language == "DE_de") \
                .one_or_none()

            if bridge_product_translation_in_db:
                # Update
                bridge_product_translation_for_db = bridge_product_translation_in_db.update(bridge_product_translation_new)
                self.logger.info(f"Updated existing translation: {bridge_product_translation_in_db.id}")
            else:
                # Insert
                bridge_product_translation_for_db = bridge_product_translation_new

            bridge_entity.translations.append(bridge_product_translation_for_db)

        except Exception as e:
            # Unerwarteter Fehler
            self.logger.error(f"An error occurred while setting translation relation: {str(e)}")

        return bridge_entity

    def _set_price_relation(self, bridge_entity):
        try:
            # 1 Upsert price for all marketplaces
            bridge_price_new = self._dataset_entity.map_erp_price_to_bridge()
            BridgePriceController().upsert_price_for_all_marketplaces(
                bridge_price_entity=bridge_price_new,
                bridge_product_entity=bridge_entity
            )

        except Exception as e:
            self.logger.error(f"An error occurred while setting price relation: {str(e)}")

        return bridge_entity

    def _set_tax_relation(self, bridge_entity):
        """
        Set the tax relation for a given bridge entity.
        If the tax is not found in the database, it attempts to sync the tax using the provided sync method.

        :param bridge_entity: The BridgeProductEntity to set tax relation for.
        :type bridge_entity: BridgeProductEntity
        :return: BridgeProductEntity with tax relation set.
        :rtype: BridgeProductEntity
        """
        if bridge_entity is None:
            self.logger.error("Invalid argument: bridge_entity is None.")
            raise ValueError("Invalid argument: bridge_entity is None.")

        try:
            stschl = self.get_entity().get_stschl()
            tax_in_db = BridgeTaxEntity.query.filter_by(erp_nr=stschl).one_or_none()

            # Wenn die Steuer nicht in der Datenbank gefunden wird, erfolgt ein Sync-Versuch
            if tax_in_db is None:
                self.logger.warning(f"Tax with ERP number: {stschl} not found in database. Attempting to sync.")

                # Hier den Sync-Vorgang einfügen
                tax_ctrl = ERPMandantSteuerController(config.ERPConfig.MANDANT)
                bridge_tax_entity_new = tax_ctrl.get_entity().map_erp_to_bridge(stschl=stschl)
                bridge_entity.tax = bridge_tax_entity_new

        except Exception as e:
            self.logger.error(f"An error occurred while setting tax relation: {str(e)}")

        return bridge_entity

    def _set_category_relation(self, bridge_entity):
        try:
            # Map new object
            categories_list = self.get_categories_list()
            self.logger.info(f"We have {len(categories_list)} categories to add, Categories: {categories_list} for Product ID: {bridge_entity.id}")
            if not categories_list:
                self.logger.info("No categories to add.")
                return bridge_entity
            # First clear the existing categories to avoid duplicates or obsolete relations
            bridge_entity.categories.clear()
            for category_erp_nr in categories_list:
                # Check DB for existing entries
                try:
                    category_entity = BridgeCategoryEntity.query.filter_by(erp_nr=category_erp_nr).one_or_none()
                except Exception as e:
                    self.logger.error(f"No category found with this ID {category_erp_nr}")
                    continue
                if category_entity:
                    # Update
                    bridge_entity.categories.append(category_entity)
                    self.logger.info(f"Updated existing Category Relation: {category_erp_nr}")
                else:
                    # Insert
                    self.logger.info(f"Category {category_erp_nr} not found. Sync all Categories first")
        except Exception as e:
            # Unexpected Error
            self.logger.error(f"An error occurred while setting category relation: {str(e)}")

        return bridge_entity

    def _set_media_relation(self, bridge_entity):
        # 1. Get the list of medias
        bridge_entity.medias.clear()
        images = self._dataset_entity.get_images_file_list()
        for image in images:

            # 2. Map new object
            bridge_media_entity_new = self._dataset_entity.map_erp_media_to_bridge(media=image)

            # 3 Chek if media is already in db
            media_in_db = BridgeMediaEntity().query.filter_by(file_name=bridge_media_entity_new.get_file_name()).one_or_none()

            if media_in_db:
                self.logger.info(f"Updating Media {bridge_media_entity_new.get_file_name()}")
                bridge_media_entity_for_db = media_in_db.update(bridge_media_entity_new)
            else:
                bridge_media_entity_for_db = bridge_media_entity_new

            # 4 Append to the bridge_entity
            bridge_entity.medias.append(bridge_media_entity_for_db)

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

    def get_umsatz(self,  jahr, return_field):
            ums = self._dataset_entity.get_nested_ums(jahr, return_field)
            if ums:
                self.logger.info(f"Umsatz retrieved successfully. {ums}")
            else:
                self.logger.warning("No Umsatz retrieved")
            return ums

    def get_categories_list(self):
        return self._dataset_entity.get_categories_list()

    def price_infos(self):
        infos = {
            "Steuerschlüssel": self._dataset_entity.get_("StSchl"),
            "Steuerschlüsselart": self._dataset_entity.get_("StSchlArt"),
            "Steuerverteilung": self._dataset_entity.get_("StVert"),
            "Steuerverteilung Netto": self._dataset_entity.get_("StVertNt"),
            "Steuerverteilung Steuer": self._dataset_entity.get_("StVertSt"),
            "Steuerverteilung Brutto": self._dataset_entity.get_("StVertBt"),
        }
        return infos
