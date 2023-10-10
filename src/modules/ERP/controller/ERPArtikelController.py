import config
from ..controller.ERPAbstractController import ERPAbstractController
from ..controller.ERPMandantSteuerController import ERPMandantSteuerController
from ..entities.ERPArtikelEntity import ERPArtikelEntity
from ..entities.ERPArtikelKategorienEntity import ERPArtikelKategorienEntity
from src.modules.Bridge.entities.BridgeProductEntity import BridgeProductEntity
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
        self._category_dataset_entity = ERPArtikelKategorienEntity()

        super().__init__(
            dataset_entity=self._dataset_entity
        )

    def is_in_db(self, bridge_entity_new: BridgeProductEntity) -> object:
        """
        Checks if a given BridgeProductEntity is already present in the database.

        :param bridge_entity_new: The BridgeProductEntity to check.
        :type bridge_entity_new: BridgeProductEntity
        :return: The existing BridgeProductEntity from the database if found, None if not found, and False if an error occurs.
        :rtype: BridgeProductEntity or bool or None
        """
        try:
            self.logger.info(f"Attempting to find BridgeProductEntity with ERP number: {bridge_entity_new.erp_nr}")
            entity_in_db = BridgeProductEntity.query.filter_by(erp_nr=bridge_entity_new.erp_nr).one_or_none()

            if entity_in_db:
                self.logger.info(f"BridgeProductEntity with ERP number: {bridge_entity_new.erp_nr} found in database.")
                return entity_in_db
            else:
                self.logger.warning(f"BridgeProductEntity with ERP number: {bridge_entity_new.erp_nr} not found in database.")
                return None

        except Exception as e:
            self.logger.error(f"An error occurred while querying the database: {str(e)}")
            return False

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
        bridge_entity = self._set_tax_relation(bridge_entity)
        bridge_entity = self._set_category_relation(bridge_entity)
        return bridge_entity

    def _set_tax_relation(self, bridge_entity):
        """
        Set the tax relation for a given bridge entity.

        :param bridge_entity: The BridgeProductEntity to set tax relation for.
        :type bridge_entity: BridgeProductEntity
        :return: BridgeProductEntity with tax relation set.
        :rtype: BridgeProductEntity
        """
        try:
            tax_ctrl = ERPMandantSteuerController(config.ERPConfig.MANDANT)
            stschl = self.get_entity().get_stschl()
            # Do an upsert with the taxes, as the tax status might have changed.
            tax_ctrl.sync_one_to_bridge(stschl=stschl)
            tax_from_db = BridgeTaxEntity.query.filter_by(erp_nr=stschl).one_or_none()

            if tax_from_db:
                bridge_entity.tax = tax_from_db
            else:
                self.logger.warning(f"Tax with ERP number: {stschl} not found in database.")

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
        if categories_list:
            for category in categories_list:
                try:
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
