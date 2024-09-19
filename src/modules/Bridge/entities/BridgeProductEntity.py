import uuid
from pprint import pprint
from typing import Union

from sqlalchemy import update
from config import SW6Config

from src import db
import datetime

from src.modules.ModulesCoreController import generate_uuid
from src.modules.Bridge.entities.BridgeMediaEntity import BridgeProductsMediaAssoc, BridgeMediaEntity
from .BridgeCategoryEntity import BridgeProductsCategoriesAssoc


class TranslationWrapper:
    def __init__(self, translation):
        self.translation = translation

    def __getattr__(self, name):
        if self.translation:
            return getattr(self.translation, name)
        return None


class BridgeProductEntity(db.Model):
    __tablename__ = 'bridge_product_entity'

    id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True)
    erp_nr = db.Column(db.String(255), nullable=False, unique=True)
    stock = db.Column(db.Integer(), nullable=False)
    storage_location = db.Column(db.String(255), nullable=True)
    unit = db.Column(db.String(255), nullable=True)
    min_purchase = db.Column(db.Integer(), nullable=True)
    purchase_unit = db.Column(db.Integer(), nullable=True)
    shipping_cost_per_bundle = db.Column(db.Float(), nullable=True)
    shipping_bundle_size = db.Column(db.Integer(), nullable=True)
    is_active = db.Column(db.Boolean(), nullable=False, default=True)
    factor = db.Column(db.Integer(), nullable=True)
    sort = db.Column(db.Integer(), nullable=True)
    sw6_id = db.Column(db.CHAR(36), default=generate_uuid(), nullable=False)
    sw6_media_id = db.Column(db.CHAR(36), default=generate_uuid(), nullable=False)
    created_at = db.Column(db.DateTime(), nullable=True, default=datetime.datetime.now())
    edited_at = db.Column(db.DateTime(), nullable=True, default=datetime.datetime.now())

    # Relations
    translations = db.relationship(
        'BridgeProductTranslation',
        backref='product',
        lazy='subquery',
        cascade='all, delete-orphan'
    )

    tax_id = db.Column(db.Integer(), db.ForeignKey('bridge_tax_entity.id'), nullable=True)

    marketplace_prices_assoc = db.relationship('BridgeProductMarketplacePriceAssoc', back_populates='product')

    order_details = db.relationship('BridgeOrderDetailsEntity', back_populates='product')

    categories_assoc = db.relationship("BridgeProductsCategoriesAssoc", back_populates="product")

    @property
    def categories(self):
        """
        Returns a list of categories associated with the product.

        This property navigates through the relationship with the
        "BridgeProductsCategoriesAssoc" entity,
        collecting all the associated "BridgeCategoryEntity" objects,
        effectively giving us all the categories related to this product.

        :return: List of "BridgeCategoryEntity" objects associated with the product.
        """
        return [assoc.category for assoc in self.categories_assoc]

    def get_images(self):
        """
        Returns the media associated with this product.

        Returns:
            list[BridgeMediaEntity]: A list of media entities associated with this product.
        """
        return [assoc.media for assoc in self.media_assocs]

    def get_prod_cat_assoc(self, category):
        assoc = BridgeProductsCategoriesAssoc.query.filter(
            BridgeProductsCategoriesAssoc.product_id == self.get_id(),
            BridgeProductsCategoriesAssoc.category_id == category.id
        ).one_or_none()
        if assoc:
            return assoc

    def get_id(self):
        """Gets the id of the product.

        Returns:
            int: The id code of the product.
        """
        return self.id

    # Getter and Setter for erp_nr
    def get_erp_nr(self):
        """Gets the ERP number of the product."""
        return self.erp_nr

    def set_erp_nr(self, erp_nr):
        """Sets the ERP number of the product."""
        try:
            if not erp_nr:
                raise ValueError("ERP number cannot be empty.")
            self.erp_nr = erp_nr
        except Exception as e:
            raise ValueError(f"Error setting ERP number: {e}")

    # Getter and Setter for stock
    def get_stock(self):
        """Gets the stock of the product."""
        return self.stock

    def set_stock(self, stock):
        """Sets the stock of the product."""
        try:
            if stock < 0:
                raise ValueError("Stock cannot be negative.")
            self.stock = stock
        except Exception as e:
            raise ValueError(f"Error setting stock: {e}")

    # Getter for storage_location
    def get_storage_location(self):
        """Gets the storage location of the product."""
        return self.storage_location

    # Setter for storage_location
    def set_storage_location(self, storage_location):
        """Sets the storage location of the product."""
        self.storage_location = storage_location

    # Getter and Setter for unit
    def get_unit(self):
        """Gets the unit of the product."""
        return self.unit

    def set_unit(self, unit):
        """Sets the unit of the product."""
        self.unit = unit

    # Getter and Setter for min_purchase
    def get_min_purchase(self):
        """Gets the minimum purchase of the product."""
        return self.min_purchase

    def set_min_purchase(self, min_purchase):
        """Sets the minimum purchase of the product."""
        try:
            if min_purchase is not None and min_purchase < 0:
                raise ValueError("Minimum purchase cannot be negative.")
            self.min_purchase = min_purchase
        except Exception as e:
            raise ValueError(f"Error setting minimum purchase: {e}")

    # Getter and Setter for purchase_unit
    def get_purchase_unit(self):
        """Gets the purchase unit of the product."""
        return self.purchase_unit

    def set_purchase_unit(self, purchase_unit):
        """Sets the purchase unit of the product."""
        self.purchase_unit = purchase_unit

    # Getter and Setter for shipping_cost_per_bundle
    def get_shipping_cost_per_bundle(self):
        """Gets the shipping cost per bundle of the product."""
        return self.shipping_cost_per_bundle

    def set_shipping_cost_per_bundle(self, shipping_cost_per_bundle):
        """Sets the shipping cost per bundle of the product."""
        try:
            if shipping_cost_per_bundle is not None and shipping_cost_per_bundle < 0:
                raise ValueError("Shipping cost per bundle cannot be negative.")
            self.shipping_cost_per_bundle = shipping_cost_per_bundle
        except Exception as e:
            raise ValueError(f"Error setting shipping cost per bundle: {e}")

    # Getter and Setter for shipping_bundle_size
    def get_shipping_bundle_size(self):
        """Gets the shipping bundle size of the product."""
        return self.shipping_bundle_size

    def set_shipping_bundle_size(self, shipping_bundle_size):
        """Sets the shipping bundle size of the product."""
        try:
            if shipping_bundle_size is not None and shipping_bundle_size < 0:
                raise ValueError("Shipping bundle size cannot be negative.")
            self.shipping_bundle_size = shipping_bundle_size
        except Exception as e:
            raise ValueError(f"Error setting shipping bundle size: {e}")

    def get_is_active(self):
        """Gets the active status of the product."""
        return self.is_active

    def set_is_active(self, is_active: bool):
        """Sets the active status of the product."""
        if isinstance(is_active, bool):
            self.is_active = is_active
        else:
            raise TypeError(f"Expected boolean value, got {type(is_active).__name__}")

    def get_factor(self):
        if hasattr(self, 'factor') and self.factor:
            return self.factor
        return False

    def set_factor(self, factor):
        """

        Sets the price factor of the product.
        """
        try:
            if factor is not None and not isinstance(factor, int):
                raise ValueError("Factor must be an integer.")
            self.factor = factor
        except Exception as e:
            raise ValueError(f"Error setting factor: {e}")

    def get_sort(self):
        if hasattr(self, 'sort') and self.sort:
            return self.sort
        return False

    def set_sort(self, sort):
        """

        Sets the sort row.
        """
        try:
            if sort is not None and not isinstance(sort, int):
                raise ValueError("Sort must be an integer.")
            self.sort = sort
        except Exception as e:
            raise ValueError(f"Error setting sort: {e}")

    def get_sw6_id(self):
        if self.sw6_id:
            return self.sw6_id
        else:
            return None

    def set_sw6_id(self, sw6_id=None):
        if not sw6_id:
            sw6_id = uuid.uuid4().hex
        self.sw6_id = sw6_id

    def get_sw6_media_id(self):
        if self.sw6_media_id:
            return self.sw6_media_id
        else:
            return None

    def set_sw6_media_id(self, sw6_media_id):
        self.sw6_media_id = sw6_media_id

    # Getter and Setter for created_at
    def get_created_at(self):
        """Gets the creation date and time of the product."""
        return self.created_at

    def set_created_at(self, created_at):
        """Sets the creation date and time of the product."""
        self.created_at = created_at

    # Getter and Setter for edited_at
    def get_edited_at(self):
        """Gets the last edited date and time of the product."""
        return self.edited_at

    def set_edited_at(self, edited_at):
        """Sets the last edited date and time of the product."""
        self.edited_at = edited_at

    def get_cover_image(self):
        """
        Method to fetch the cover image for the product

        :return: BridgeMediaEntity object
        """
        try:
            # Get the association entry with the smallest 'sort' value
            media_assoc = BridgeProductsMediaAssoc.query.filter_by(product_id=self.id) \
                .order_by(BridgeProductsMediaAssoc.sort.asc()).first()

            if media_assoc:
                # Get the corresponding BridgeMediaEntity entry
                cover_image = BridgeMediaEntity.query.get(media_assoc.media_id)
                return cover_image
            else:
                return None

        except Exception as e:
            print(f"Error occurred while retrieving cover image: {str(e)}")
            return None

    def update(self, bridge_entity_new):
        """
        Updates the current BridgeProductEntity instance with values from a new instance.

        Args:
            bridge_entity_new (BridgeProductEntity): The new BridgeProductEntity instance with updated values.
        """
        # Update ERP number
        self.set_erp_nr(bridge_entity_new.get_erp_nr())

        # Update stock
        self.set_stock(bridge_entity_new.get_stock())

        # Update storage_location
        self.set_storage_location(bridge_entity_new.get_storage_location())

        # Update unit
        self.set_unit(bridge_entity_new.get_unit())

        # Update minimum purchase
        self.set_min_purchase(bridge_entity_new.get_min_purchase())

        # Update purchase unit
        self.set_purchase_unit(bridge_entity_new.get_purchase_unit())

        # Update shipping cost per bundle
        self.set_shipping_cost_per_bundle(bridge_entity_new.get_shipping_cost_per_bundle())

        # Update active
        # This is done by its own method
        # self.set_active(bridge_entity_new.get_active())

        # Update factor
        self.set_factor(bridge_entity_new.get_factor())

        # Update Sort
        self.set_sort(bridge_entity_new.get_sort())

        # Update shipping bundle size
        self.set_shipping_bundle_size(bridge_entity_new.get_shipping_bundle_size())

        # Update edited_at
        self.set_edited_at(bridge_entity_new.get_edited_at())

        self.translations = bridge_entity_new.translations

        """
        Do not update SW6 ids
        """

        # Update sw6_id
        # self.set_sw6_id(bridge_entity_new.get_sw6_id())

        # Update sw6 media id
        # self.set_sw6_media_id(bridge_entity_new.get_sw6_media_id())

        return self

    """
    Special getter and setter
    """

    def get_translation(self, language_code="DE_de"):
        """
        Gets the translation of the product based on the provided language code.

        Args:
            language_code (str): The language code to get the translation for. Defaults to 'DE_de'.

        Returns:
            TranslationWrapper: The translation wrapper of the product for the provided language code.
        """
        try:
            # Finds the translation with the given language code using list comprehension
            translation = next((t for t in self.translations if t.language == language_code), None)

            return TranslationWrapper(translation)

        except Exception as e:
            # Logs any encountered error
            print(f"An error occurred while getting translation for Product: {str(e)}")

            return None

    def get_price_entity_for_marketplace(self, marketplace_id=1):
        """
        Fetches the `BridgePriceEntity` instance associated with the specified marketplace
        from `bridge_price_entity` associated with the `BridgeProductEntity` instance.
        The default marketplace_id is 1.

        :param marketplace_id: The ID of the marketplace to get the price entity from. Defaults to 1.
        :return: The associated `BridgePriceEntity` instance or None if the value is None or if a related price entity doesn't exist.
        """
        try:
            # Traverse through the marketplace_prices_assoc of the product entity,
            # looking for assoc with the provided marketplace_id
            assoc = next((assoc for assoc in self.marketplace_prices_assoc
                          if assoc.marketplace_id == marketplace_id), None)

            # If assoc with provided marketplace_id and associated price entity is found,
            # return the price entity.
            if assoc and assoc.price:
                return assoc.price
        except Exception as e:
            # Log any potential error and return None in case of any exception.
            print(f"An error occurred while fetching the price entity: {str(e)}")

        # Return None if no matching assoc or associated price entity is found.
        return None

    def get_shipping_cost(self, shipping: Union[str, float] = None, no_shipping_from: float = None) -> Union[
        str, float]:
        """
        Returns the shipping cost for this BridgeProductEntity object.
        If the product has a fixed shipping cost per bundle, it returns that value.
        Otherwise, it checks the current price of the product and returns the shipping cost
        if the price is below the threshold for free shipping.

        Args:
            shipping (str or float, optional): The shipping cost to return if applicable.
                If a string, should be in the format "1,23" with the decimal separator as a comma.
                If a float, should be the shipping cost in EUR.
                Defaults to '5,95'.
            no_shipping_from (float, optional): The price threshold for free shipping.
                Defaults to 99.0.

        Returns:
            str or float: The shipping cost if applicable, or 0 if the price is above the threshold for free shipping.
                If the shipping cost is returned as a float, it will be rounded to two decimal places.
        """
        if not shipping:
            shipping = SW6Config.SHIPPING_FEE['DE']

        if not no_shipping_from:
            no_shipping_from = SW6Config.SHIPPING_FREE['DE']

        if self.shipping_cost_per_bundle is not None:
            # If the product has a fixed shipping cost per bundle, return that value.
            return self.shipping_cost_per_bundle

        elif self.prices is not None:
            # If the product has at least one price, check the current price and return the shipping cost if applicable.
            current_price = self.get_price_entity_for_marketplace().get_current_best_price()
            if self.factor is not None:
                current_price = current_price / self.factor
            if current_price <= no_shipping_from:
                # If the current price is below the threshold for free shipping, return the shipping cost.
                if isinstance(shipping, str):
                    # If the shipping cost is given as a string, convert it to a float with comma as decimal separator.
                    shipping = float(shipping.replace(',', '.'))
                return round(shipping, 2)  # Round to two decimal places.
        # If the product has no fixed shipping cost per bundle and no prices, return 0.
        return 0

    def __repr__(self):
        """
        Translation - ok
        Price
        Tax
        Category
        Media
        :return:
        """

        return f'Bridge Product Entity: {self.get_translation("DE_de").name} ID: {self.id}'


class BridgeProductTranslation(db.Model):
    __tablename__ = 'bridge_product_translation'

    id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True)
    language = db.Column(db.String(5), nullable=False)  # language format: 'DE_de', 'GB_en', etc.
    name = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text(), nullable=True)
    created_at = db.Column(db.DateTime(), nullable=True, default=datetime.datetime.now())
    edited_at = db.Column(db.DateTime(), nullable=True, default=datetime.datetime.now())

    # Relations
    product_id = db.Column(db.Integer(), db.ForeignKey('bridge_product_entity.id', ondelete='CASCADE'), nullable=False)

    def get_id(self):
        """Gets the id of the product translation.

        Returns:
            int: The id of the translation.
        """
        return self.id

    def get_language(self):
        """Gets the language of the product translation.

        Returns:
            str: The language code of the translation.
        """
        return self.language

    def set_language(self, language):
        """Sets the language of the product translation.

        Args:
            language (str): The language code to be set.

        Raises:
            ValueError: If the provided language code is not valid.
        """
        try:
            if not language:
                raise ValueError("Language code cannot be empty.")
            # Add any specific validation for language format here
            self.language = language
        except Exception as e:
            raise ValueError(f"Error setting language: {e}")

    def get_name(self):
        """Gets the name of the product translation."""
        return self.name

    def set_name(self, name):
        """Sets the name of the product translation."""
        self.name = name

    def get_description(self):
        """Gets the description of the product translation."""
        return self.description

    def set_description(self, description):
        """Sets the description of the product translation."""
        self.description = description

    def get_created_at(self):
        """Gets the creation date and time of the product translation."""
        return self.created_at

    def set_created_at(self, created_at):
        """Sets the creation date and time of the product translation."""
        self.created_at = created_at

    def get_edited_at(self):
        """Gets the last edited date and time of the product translation."""
        return self.edited_at

    def set_edited_at(self, edited_at):
        """Sets the last edited date and time of the product translation."""
        self.edited_at = edited_at

    def get_product_id(self):
        """Gets the associated product ID of the product translation."""
        return self.product_id

    def set_product_id(self, product_id):
        """Sets the associated product ID of the product translation.

        Args:
            product_id (int): The product ID to be set.

        Raises:
            ValueError: If the product ID is not valid.
        """
        try:
            if not isinstance(product_id, int) or product_id < 0:
                raise ValueError("Product ID must be a non-negative integer.")
            self.product_id = product_id
        except Exception as e:
            raise ValueError(f"Error setting product ID: {e}")

    def update(self, bridge_entity_new):
        """
        Updates the current BridgeProductTranslation instance with values from a new instance.

        Args:
            bridge_entity_new (BridgeProductTranslation): The new BridgeProductTranslation instance with updated values.
        """
        try:
            self.set_language(bridge_entity_new.get_language())
            self.set_name(bridge_entity_new.get_name())
            self.set_description(bridge_entity_new.get_description())
            self.set_edited_at(bridge_entity_new.get_edited_at())
            self.set_product_id(bridge_entity_new.get_product_id())

            # Log the update
            print(f"Updated BridgeProductTranslation: {self.id}")
            return self

        except Exception as e:
            # Handle the error appropriately
            print(f"Error updating BridgeProductTranslation: {e}")
            # Depending on your error handling strategy, you might want to re-raise the exception
            # raise
            return False
