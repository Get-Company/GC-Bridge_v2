from src import db
import datetime


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
    unit = db.Column(db.String(255), nullable=True)
    min_purchase = db.Column(db.Integer(), nullable=True)
    purchase_unit = db.Column(db.Integer(), nullable=True)
    shipping_cost_per_bundle = db.Column(db.Float(), nullable=True)
    shipping_bundle_size = db.Column(db.Integer(), nullable=True)
    active = db.Column(db.Integer(), nullable=True)
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

    def get_active(self):
        """Gets the active status of the product."""
        return self.active

    def set_active(self, active):
        """
        Shoud not be set in the Bridge

        Sets the active status of the product.
        """
        try:
            if active is not None and not isinstance(active, int):
                raise ValueError("Active status must be an integer.")
            self.active = active
        except Exception as e:
            raise ValueError(f"Error setting active status: {e}")

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

        # Update unit
        self.set_unit(bridge_entity_new.get_unit())

        # Update minimum purchase
        self.set_min_purchase(bridge_entity_new.get_min_purchase())

        # Update purchase unit
        self.set_purchase_unit(bridge_entity_new.get_purchase_unit())

        # Update shipping cost per bundle
        self.set_shipping_cost_per_bundle(bridge_entity_new.get_shipping_cost_per_bundle())

        # Update active
        self.set_active(bridge_entity_new.get_active())

        # Update shipping bundle size
        self.set_shipping_bundle_size(bridge_entity_new.get_shipping_bundle_size())

        # Update edited_at
        self.set_edited_at(bridge_entity_new.get_edited_at())

        self.translations = bridge_entity_new.translations

        return self

    def get_translation(self, language_code="DE_de"):
        # Find the translation with the given language code using list comprehension
        translation = next((t for t in self.translations if t.language == language_code), None)
        return TranslationWrapper(translation)

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


