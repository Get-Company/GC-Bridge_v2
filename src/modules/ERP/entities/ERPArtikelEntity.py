from ..entities.ERPAbstractEntity import ERPAbstractEntity
from src.modules.Bridge.entities.BridgeProductEntity import BridgeProductEntity, BridgeProductTranslation


class ERPArtikelEntity(ERPAbstractEntity):
    """
    Representation of an ERP article entity inherited from ERPAbstractEntity.
    """

    def __init__(self, search_value=None, index=None, range_end=None):
        """
        Initializer for ERPArtikelEntity.

        :param search_value: The value used for searching.
        :param index: The index for the dataset, defaults to 'Nr' if not provided.
        :param range_end: The range end value.
        """
        super().__init__(
            dataset_name="Artikel",
            dataset_index=index or "Nr",
            search_value=search_value,
            range_end=range_end
        )

    def map_erp_to_bridge(self):
        """
        Maps the current ERP article entity to a BridgeProductEntity.

        :return: A BridgeProductEntity instance with mapped values.
        """
        try:
            product_entity = BridgeProductEntity(
                erp_nr=self.get_nr(),
                stock=self.get_stock(),
                unit=self.get_unit(),
                min_purchase=self.get_min_purchase(),
                purchase_unit=self.get_purchase_unit(),
                shipping_cost_per_bundle=self.get_shipping_cost_per_bundle(),
                shipping_bundle_size=self.get_shipping_bundle_size()
            )

            # Always creat a German translation
            product_translation = BridgeProductTranslation(
                language='DE_de',
                name=self.get_name(),
                description=self.get_description(),
            )
            product_entity.translations.append(product_translation)

            return product_entity
        except Exception as e:
            self.logger.error(f"Error mapping ERPArtikel to Bridge: {str(e)}")
            return None

    def get_nr(self):
        """
        Fetches the article number from the dataset.

        :return: Article number.
        """
        return self.get_("ArtNr")

    def get_stock(self):
        """
        Fetches the stock quantity from the dataset.

        :return: Stock quantity.
        """
        return self.get_("LagMge")

    def get_unit(self):
        """
        Fetches the unit from the dataset, removes '% ' if present.

        :return: Unit.
        """
        einheit = self.get_("Einh")
        einheit = einheit.replace("% ", "")
        return einheit

    def get_min_purchase(self):
        """
        Fetches the minimum purchase quantity from the dataset.

        :return: Minimum purchase quantity.
        """
        return self.get_("Sel10")

    def get_purchase_unit(self):
        """
        Fetches the purchase unit from the dataset.

        :return: Purchase unit.
        """
        return self.get_("Sel11")

    def get_shipping_cost_per_bundle(self):
        """
        Fetches the shipping cost per bundle from the dataset.

        :return: Shipping cost per bundle.
        """
        return self.get_("Sel70")

    def get_shipping_bundle_size(self):
        """
        Fetches the shipping bundle size from the dataset.

        :return: Shipping bundle size.
        """
        return self.get_("Sel71")

    def get_name(self) -> str:
        """
        Retrieves the name of the product from the ERP dataset.

        :return: The name of the product.
        :rtype: str
        """
        try:
            name = self.get_("KuBez5")
            if name is not None:
                return name
            else:
                self.logger.warning("No name found for the product.")
                return ""
        except Exception as e:
            self.logger.error(f"An error occurred while retrieving the name: {str(e)}")
            return ""

    def get_description(self) -> str:
        """
        Retrieves the description of the product from the ERP dataset.

        :return: The description of the product.
        :rtype: str
        """
        try:
            description = self.get_("Bez5")
            if description is not None:
                return description
            else:
                self.logger.warning("No description found for the product.")
                return ""
        except Exception as e:
            self.logger.error(f"An error occurred while retrieving the description: {str(e)}")
            return ""

    def get_nested_ums(self, jahr, return_field):
        """
        Retrieve the revenue in euros for a specified year.

        :param jahr: The year for which the revenue is to be retrieved.
        :param return_field: The field from which the revenue is to be retrieved.
        :return: Revenue in euros for the specified year.
        """
        ums = self.get_nested_("Ums", "Jahr", jahr, return_field)
        return ums

    def get_nested_stgums(self, jahr, return_field):
        """
        Retrieve the piece revenue for a specified year.

        :param jahr: The year for which the piece revenue is to be retrieved.
        :param return_field: The field from which the piece revenue is to be retrieved.
        :return: Piece revenue for the specified year.
        """
        stg_ums = self.get_nested_("StGUms", "Jahr", jahr, return_field)
        return stg_ums

    def get_nested_sliums(self, jahr, return_field):
        """
        Retrieve the revenue of the bill of materials (Stückliste) for a specified year.

        :param jahr: The year for which the revenue of the bill of materials is to be retrieved.
        :param return_field: The field from which the revenue of the bill of materials is to be retrieved.
        :return: Revenue of the bill of materials for the specified year.
        """
        sli_ums = self.get_nested_("SLiUms", "Jahr", jahr, return_field)
        return sli_ums


