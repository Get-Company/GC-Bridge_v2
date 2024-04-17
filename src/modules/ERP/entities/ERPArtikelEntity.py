import datetime
import os
from pprint import pprint
import requests

import uuid

from ..entities.ERPAbstractEntity import ERPAbstractEntity
from src.modules.Bridge.entities.BridgeProductEntity import (
    BridgeProductEntity, BridgeProductTranslation)
from src.modules.Bridge.entities.BridgePriceEntity import BridgePriceEntity
from src.modules.Bridge.entities.BridgeTaxEntity import BridgeTaxEntity
from src.modules.Bridge.entities.BridgeCategoryEntity import BridgeCategoryEntity
from src.modules.ERP.controller.ERPMandantSteuerController import ERPMandantSteuerController
from ..entities.ERPArtikelKategorienEntity import ERPArtikelKategorienEntity
from src.modules.ERP.controller.ERPLagerController import ERPLagerController
from config import ERPConfig, GCBridgeConfig


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
            range_end=range_end,
            filter_expression="WShopKz='1'"
        )


    def map_erp_to_bridge(self):
        """
        Maps the current ERP article entity to a BridgeProductEntity.

        :return: A BridgeProductEntity instance with mapped values or None if an error occurs.
        """
        try:
            # Create a new BridgeProductEntity with the fetched values
            product_entity = BridgeProductEntity(
                id=self.get_id(),
                erp_nr=self.get_nr(),
                stock=self.get_stock(),
                storage_location=self.get_storage_location(),
                unit=self.get_unit(),
                min_purchase=self.get_min_purchase(),
                purchase_unit=self.get_purchase_unit(),
                shipping_cost_per_bundle=self.get_shipping_cost_per_bundle(),
                shipping_bundle_size=self.get_shipping_bundle_size(),
                active=self.get_active(),
                factor=self.get_factor(),
                sw6_id=self.set_sw6_id(),
                created_at=self.get_erstdat(),
                edited_at=self.get_aenddat()
            )

            return product_entity

        except Exception as e:
            # Log the error and return None
            self.logger.error(f"Error mapping ERPArtikel to Bridge: {str(e)}")
            return None

    def map_erp_translation_to_bridge(self):
        # Create a translation entity and append it to the product entity
        product_translation = BridgeProductTranslation(
            language='DE_de',
            name=self.get_name(),
            description=self.get_description(),
            edited_at=self.get_aenddat()
        )
        return product_translation

    def map_bridge_to_erp(self, bridge_entity):
        pass

    def map_erp_price_to_bridge(self):
        # Create a price entity and assign it to the product
        price = BridgePriceEntity(
            price=self.get_price(),
            rebate_quantity=self.get_rebate_quantity(),
            rebate_price=self.get_rebate_price(),
            special_price=self.get_special_price(),
            special_start_date=self.get_special_start_date(),
            special_end_date=self.get_special_end_date(),
            created_at=self.get_erstdat(),
            edited_at=self.get_aenddat()
        )
        return price

    def get_nr(self):
        """
        Fetches the article number from the dataset.
        :return: Article number or empty string if not found.
        """
        try:
            nr = self.get_("ArtNr")
            if nr is None:
                self.logger.warning("Article number is empty.")
                return None
            return str(nr)
        except Exception as e:
            self.logger.error(f"An error occurred while retrieving the article number: {str(e)}")
            return None

    def get_stock(self):
        """
        Fetches the stock quantity from the dataset.
        :return: Stock quantity as an integer or None if the value is None or can't be converted to an integer.
        """
        value = self.get_("LagMge")
        if value is None:
            self.logger.warning("Stock quantity is empty.")
            return None

        try:
            return int(value)
        except (ValueError, TypeError):
            self.logger.error(f"Error on converting '{value}' into an Integer for stock quantity.")
            return None

    def get_unit(self, raw=False):
        """
        Fetches the unit from the dataset.
        If raw is False, the '% ' will be removed if present.
        In ERPVorgangEntity the unit forwarded to ERP, where we will need the '%'
        :param raw: If True the unit will be returned with '%'
        :return: Unit or empty string if not found.
        """
        try:
            einheit = self.get_("Einh")
            if einheit is None:
                self.logger.warning("Unit is empty.")
                return ""
            if not raw:
                einheit = einheit.replace("% ", "")
            return einheit
        except Exception as e:
            self.logger.error(f"An error occurred while retrieving the unit: {str(e)}")
            return None

    def get_min_purchase(self):
        """
        Fetches the minimum purchase quantity from the dataset.

        :return: Minimum purchase quantity or None if the value is None or can't be converted to an integer.
        """
        value = self.get_("Sel10")

        if value is None or value == "":
            self.logger.warning("Mindestbestellmenge is empty")
            return 0

        try:
            return int(value)
        except (ValueError, TypeError):
            self.logger.error(f"Error on converting '{value}' into an Integer.")
            return 0

    def get_purchase_unit(self):
        """
        Fetches the purchase unit from the dataset.

        :return: Purchase unit as an integer or None if the value is None or can't be converted to an integer.
        """
        value = self.get_("Sel11")

        if value is None or value == "":
            self.logger.warning("Purchase unit is empty")
            return 0

        try:
            return int(value)
        except (ValueError, TypeError):
            self.logger.error(f"Error on converting '{value}' into an Integer.")
            return 0

    def get_shipping_cost_per_bundle(self):
        """
        Fetches the shipping cost per bundle from the dataset.
        :return: Shipping cost per bundle or None if the value is None or can't be converted to a float.
        """
        value = self.get_("Sel70")
        if value is None:
            self.logger.warning("Shipping cost per bundle is empty.")
            return None

        try:
            return float(value)
        except (ValueError, TypeError):
            self.logger.error(f"Error on converting '{value}' into a Float for shipping cost.")
            return None

    def get_shipping_bundle_size(self):
        """
        Fetches the shipping bundle size from the dataset.
        :return: Shipping bundle size or None if the value is None or can't be converted to an integer.
        """
        value = self.get_("Sel71")
        if value is None:
            self.logger.warning("Shipping bundle size is empty.")
            return None

        try:
            return int(value)
        except (ValueError, TypeError):
            self.logger.error(f"Error on converting '{value}' into an Integer for shipping bundle size.")
            return None

    def get_active(self):
        """
        Fetches the active status from the dataset.
        :return: Active status as an integer or None if the value is None or can't be converted to an integer.
        """
        value = self.get_("WShopKz")
        if value is None:
            self.logger.warning("Active status is empty.")
            return None

        try:
            return int(value)
        except (ValueError, TypeError):
            self.logger.error(f"Error on converting '{value}' into an Integer for active status.")
            return None

    def set_sw6_id(self):
        return str(uuid.uuid4().hex)

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

    def get_stschl(self):
        """
        Fetches the tax key from the dataset and extracts the key from the string.
        Example: In the artikel The Stschl and the description are combined. We just need the first digit,
        or everything before the first white space.
        :return: Tax key as an integer or None if the value is None, missing, or can't be converted to an integer.
        """
        try:
            stschl_str = self.get_("StSchl")
            if stschl_str:

                stschl_list = stschl_str.split()
                return int(stschl_list[0])
            else:
                self.logger.warning("No tax key found in the provided string.")
                return None
        except (ValueError, IndexError, TypeError) as e:
            self.logger.error(f"An error occurred while processing the tax key string: {str(e)}")
            return None

    def get_price(self, vk=0):
        """
        Fetches the price from the dataset based on the given vk and rab parameters and extracts the price from the string.
        :param vk: The vk parameter to fetch the price.
        :param rab: The rab parameter to fetch the price.
        :return: Price as a float or None if the value is None, missing, or can't be converted to a float.
        """
        try:
            price = self.get_(f"Vk{vk}.Preis")
            if price:
                return float(price)
            else:
                self.logger.warning("No price found in the provided string.")
                return None
        except (ValueError, IndexError, TypeError) as e:
            self.logger.error(f"An error occurred while processing the price string: {str(e)}")
            return None

    def get_rebate_quantity(self, vk=0, rab=0):
        """
        Fetches the rebate quantity from the dataset based on the given vk and rab parameters and extracts the quantity from the string.
        :param vk: The vk parameter to fetch the rebate quantity.
        :param rab: The rab parameter to fetch the rebate quantity.
        :return: Rebate quantity as an integer or None if the value is None, missing, or can't be converted to an integer.
        """
        try:
            rebate_quantity = self.get_(f"Vk{vk}.Rab{rab}.Mge")
            if rebate_quantity:
                return int(rebate_quantity)
            else:
                self.logger.warning("No rebate quantity found in the provided string.")
                return None
        except (ValueError, IndexError, TypeError) as e:
            self.logger.error(f"An error occurred while processing the rebate quantity string: {str(e)}")
            return None

    def get_rebate_price(self, vk=0, rab=0):
        """
        Fetches the rebate price from the dataset based on the given vk and rab parameters and extracts the price from the string.
        :param vk: The vk parameter to fetch the rebate price.
        :param rab: The rab parameter to fetch the rebate price.
        :return: Rebate price as a float or None if the value is None, missing, or can't be converted to a float.
        """
        try:
            rebate_price = self.get_(f"Vk{vk}.Rab{rab}.Pr")
            if rebate_price:
                return float(rebate_price)
            else:
                self.logger.warning("No rebate price found in the provided string.")
                return None
        except (ValueError, IndexError, TypeError) as e:
            self.logger.error(f"An error occurred while processing the rebate price string: {str(e)}")
            return None

    def get_special_price(self, vk=0):
        """
        Fetches the special price from the dataset based on the given vk parameter and extracts the price from the string.
        :param vk: The vk parameter to fetch the special price.
        :return: Special price as a float or None if the value is None, missing, or can't be converted to a float.
        """
        try:
            special_price = self.get_(f"Vk{vk}.SPr")
            if special_price:
                return float(special_price)
            else:
                self.logger.warning("No special price found in the provided string.")
                return None
        except (ValueError, IndexError, TypeError) as e:
            self.logger.error(f"An error occurred while processing the special price string: {str(e)}")
            return None

    def get_special_start_date(self, vk=0):
        """
        Fetches the special start date from the dataset based on the given vk parameter.
        :param vk: The vk parameter to fetch the special start date.
        :return: Special start date as a string or None if the value is None or missing.
        """
        try:
            special_start_date = self.get_(f"Vk{vk}.SVonDat")
            if special_start_date:
                # Convert pywintypes.datetime to standard datetime.datetime
                special_start_date = datetime.datetime(special_start_date.year, special_start_date.month, special_start_date.day, special_start_date.hour, special_start_date.minute, special_start_date.second)
                return special_start_date
            else:
                self.logger.warning("No special start date found in the provided string.")
                return None
        except (ValueError, IndexError, TypeError) as e:
            self.logger.error(f"An error occurred while processing the special start date string: {str(e)}")
            return None

    def get_special_end_date(self, vk=0):
        """
        Fetches the special end date from the dataset based on the given vk parameter.
        :param vk: The vk parameter to fetch the special end date.
        :return: Special end date as a string or None if the value is None or missing.
        """
        try:
            special_end_date = self.get_(f"Vk{vk}.SBisDat")
            if special_end_date:
                # Convert pywintypes.datetime to standard datetime.datetime
                special_end_date = datetime.datetime(special_end_date.year, special_end_date.month, special_end_date.day, special_end_date.hour, special_end_date.minute, special_end_date.second)
                return special_end_date
            else:
                self.logger.warning("No special end date found in the provided string.")
                return None
        except (ValueError, IndexError, TypeError) as e:
            self.logger.error(f"An error occurred while processing the special end date string: {str(e)}")
            return None

    def get_factor(self):
        """
        Fetches the special factor from the dataset based on the given factor parameter.
        :param factor: The factor parameter to fetch the factor.
        :return: Factor as an integer or None if the value is None or missing.
        """
        try:
            factor = self.get_(f"Sel6")
            if factor:
                # Ensure the value is an integer
                factor = int(factor)
                return factor
            else:
                self.logger.warning("No factor found in the provided string.")
                return None
        except (ValueError, IndexError, TypeError) as e:
            self.logger.error(f"An error occurred while processing the factor string: {str(e)}")
            return None

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

    def get_categories_list(self) -> list:
        """
        Retrieve all the category numbers available in the ERP.

        This method fetches each category number from 'ArtKat1' up to the maximum available
        category number determined by the `get_available_categories` method.

        Returns:
            list[int] or bool: A list of all available category numbers if successful, otherwise False.

        Raises:
            Exception: If there's an issue retrieving the category numbers.
        """
        try:
            # Initialize the ERPArtikelKategorienEntity to fetch available categories

            available_categories = ERPArtikelKategorienEntity().get_available_categories()

            # If available_categories is False or not an integer, return False
            if not isinstance(available_categories, int):
                self.logger.warning("Unable to determine the total available categories.")
                # If we are not able to get the amount of categories
                # we have to hardcode them.
                available_categories = 10
                return False

            # Retrieve each category number from 'ArtKat1' up to 'ArtKat{available_categories}'
            categories = [self.get_(f"ArtKat{i}") for i in range(1, available_categories + 1)]

            # Remove empty or None category numbers from the list
            categories = [cat for cat in categories if cat]

            # Log the successful retrieval of category numbers
            self.logger.info(f"Successfully retrieved {len(categories)} category numbers from the ERP.")

            return categories

        except Exception as e:
            self.logger.error(f"An error occurred while fetching the category numbers: {str(e)}")
            return False

    def get_storage_location(self):
        if self.get_nr():
            location = ERPLagerController(search_value=[self.get_nr(), 1]).get_entity().get_position()
            if location:
                self.logger.info("Storage location found: %s", location)
                return location
            else:
                self.logger.error("No storage location found for %s", self.get_nr())
                return None

    def __repr__(self):
        return f'Artikel {self.get_nr()} - {self.get_name()}'

