from sqlalchemy.exc import NoResultFound, MultipleResultsFound

import config
from ..controller.ERPAbstractController import ERPAbstractController
from ..controller.ERPMandantSteuerController import ERPMandantSteuerController
from ..entities.ERPArtikelEntity import ERPArtikelEntity
from ..entities.ERPArtikelKategorienEntity import ERPArtikelKategorienEntity
from src.modules.Bridge.entities.BridgeProductEntity import BridgeProductEntity, BridgeProductTranslation, BridgePriceEntity
from src.modules.Bridge.controller.BridgeProductController import BridgeProductController
from src.modules.Bridge.entities.BridgeTaxEntity import BridgeTaxEntity
from src.modules.Bridge.entities.BridgeCategoryEntity import BridgeCategoryEntity


class ERPArtikelController(ERPAbstractController):
    """
    Examples:

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
        return bridge_entity

    def _set_translation_relation(self, bridge_entity):
        for translation in bridge_entity.translations:
            try:
                self.logger.info(f"Looking for Translation: {translation.name} for Product ID: {translation.product_id}")
                translation_in_db = BridgeProductTranslation.query \
                    .filter(BridgeProductTranslation.name == translation.name) \
                    .filter(BridgeProductTranslation.name != "") \
                    .filter(BridgeProductTranslation.product_id == bridge_entity.id) \
                    .one_or_none()
                translation.id = translation_in_db.id
            except NoResultFound:
                # Translation not found in the database
                pass
            except MultipleResultsFound:
                # More than one translation with the same name found in the database
                self.logger.warning(f"Multiple translations found for name: {translation.name}")
            except Exception as e:
                # Handle other unexpected errors
                self.logger.error(f"An error occurred while setting translation relation: {str(e)}")
        return bridge_entity

    def _set_price_relation(self, bridge_entity):
        try:
            self.logger.info(f"Looking for Price related to Product ID: {bridge_entity.id}")
            price_in_db = BridgePriceEntity.query \
                .filter(BridgePriceEntity.product_id == bridge_entity.id) \
                .one_or_none()

            if price_in_db:
                bridge_entity.prices.id = price_in_db.id
            else:
                self.logger.info(f"No price found for Product ID: {bridge_entity.id}")

        except MultipleResultsFound:
            # More than one price with the same product_id found in the database
            self.logger.warning(f"Multiple prices found for Product ID: {bridge_entity.id}")
        except Exception as e:
            # Handle other unexpected errors
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
        try:
            stschl = self.get_entity().get_stschl()
            tax_from_db = BridgeTaxEntity.query.filter_by(erp_nr=stschl).one_or_none()

            if tax_from_db:
                self.logger.info(f"Added Tax with ERP number: {tax_from_db.erp_nr} to product.")
                bridge_entity.tax = tax_from_db
            else:
                self.logger.warning(f"Tax with ERP number: {stschl} not found in database. Attempting to sync.")

                # If tax is not found, attempt to sync it.
                tax_ctrl = ERPMandantSteuerController(config.ERPConfig.MANDANT)
                tax_ctrl.sync_one_to_bridge(stschl=stschl)

                # After syncing, attempt to retrieve the tax again from the database.
                tax_from_db_after_sync = BridgeTaxEntity.query.filter_by(erp_nr=stschl).one_or_none()
                if tax_from_db_after_sync:
                    bridge_entity.tax = tax_from_db_after_sync
                else:
                    self.logger.error(f"Tax with ERP number: {stschl} still not found in database after syncing.")

        except Exception as e:
            self.logger.error(f"An error occurred while setting tax relation: {str(e)}")

        return bridge_entity

    def _set_category_relation(self, bridge_entity):
        """
        Set the category relation for a given bridge entity.

        :param bridge_entity: The BridgeProductEntity to set category relation for.
        :type bridge_entity: BridgeProductEntity
        :return: BridgeProductEntity with category relation set.
        :rtype: BridgeProductEntity
        """
        categories_list = self.get_categories_list()
        bridge_entity.categories = []
        if categories_list:
            for category in categories_list:
                try:
                    self.logger.info(f"Searching BridgeCategoryEntity for {category}")
                    category_ntt = BridgeCategoryEntity.query.filter_by(erp_nr=category).one_or_none()

                    if category_ntt:
                        bridge_entity.categories.append(category_ntt)
                        self.logger.info(f"Added category with ERP number: {category} to product.")
                    else:
                        self.logger.warning(f"Category with ERP number: {category} not found in database.")

                except Exception as e:
                    self.logger.error(f"An error occurred while adding category with ERP number: {category} to product. Error: {str(e)}")

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