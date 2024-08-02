from pprint import pprint

from src import db
import datetime


class BridgePriceEntity(db.Model):
    __tablename__ = 'bridge_price_entity'

    id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True)
    price = db.Column(db.Float(), nullable=False)
    rebate_quantity = db.Column(db.Integer(), nullable=True)
    rebate_price = db.Column(db.Float(), nullable=True)
    special_price = db.Column(db.Float(), nullable=True)
    special_start_date = db.Column(db.DateTime(), nullable=True)
    special_end_date = db.Column(db.DateTime(), nullable=True)
    created_at = db.Column(db.DateTime(), nullable=False, default=datetime.datetime.now())
    edited_at = db.Column(db.DateTime(), nullable=False, default=datetime.datetime.now())

    # Removed when using the assocations table: product_marketplace_price
    # Foreign key for BridgeProductEntity
    # product_id = db.Column(db.Integer, db.ForeignKey('bridge_product_entity.id'))
    # product = db.relationship("BridgeProductEntity", back_populates="prices")

    # Getter and Setter for price
    def get_price(self):
        """Gets the price of the object."""
        return self.price

    def set_price(self, price):
        """Sets the price of the object."""
        if price < 0:
            raise ValueError("Price cannot be negative.")
        self.price = price

    # Getter and Setter for rebate_quantity
    def get_rebate_quantity(self):
        """Gets the rebate quantity of the object."""
        return self.rebate_quantity

    def set_rebate_quantity(self, rebate_quantity):
        """Sets the rebate quantity of the object."""
        if rebate_quantity is not None and rebate_quantity < 0:
            raise ValueError("Rebate quantity cannot be negative.")
        self.rebate_quantity = rebate_quantity

    # Getter and Setter for rebate_price
    def get_rebate_price(self):
        """Gets the rebate price of the object."""
        return self.rebate_price

    def set_rebate_price(self, rebate_price):
        """Sets the rebate price of the object."""
        if rebate_price is not None and rebate_price < 0:
            raise ValueError("Rebate price cannot be negative.")
        self.rebate_price = rebate_price

    # Getter and Setter for special_price
    def get_special_price(self):
        """Gets the special price of the object."""
        return self.special_price

    def set_special_price(self, special_price=None, percentage=None):
        """
        Sets the special price for the entity.

        Either a special price or a percentage must be provided. If a percentage is provided,
        the method will calculate the discount based on the original price.

        :param special_price: The special price to be set.
        :param percentage: The discount percentage for the price.
        :raises ValueError: When neither or both price and percentage parameters are provided.
        """
        try:
            # Check both input values are not provided
            if special_price is not None and percentage is not None:
                raise ValueError("Cannot set both special price and percentage. Please choose one.")

            # Check neither of the input values are provided
            if special_price is None and percentage is None:
                raise ValueError("Either special_price or percentage must be provided.")

            # Setting price directly if special_price is not None
            if special_price is not None:
                self.special_price = special_price
            else:  # Calculating and setting price based on discount percentage
                discount = (percentage / 100.0) * self.get_price()
                self.special_price = self.get_price() - discount

        except Exception as e:
            print("Error occurred when calculating the special price:", str(e))
            # Here you may add any additional exception handling or logging of your choice

    # Getter and Setter for special_start_date
    def get_special_start_date(self):
        """Gets the special start date of the object."""
        return self.special_start_date

    def set_special_start_date(self, special_start_date):
        """Sets the special start date of the object."""
        self.special_start_date = special_start_date

    # Getter and Setter for special_end_date
    def get_special_end_date(self):
        """Gets the special end date of the object."""
        return self.special_end_date

    def set_special_end_date(self, special_end_date):
        """Sets the special end date of the object."""
        self.special_end_date = special_end_date

    # Getter and Setter for created_at
    def get_created_at(self):
        """Gets the creation date of the object."""
        return self.created_at

    def set_created_at(self, created_at):
        """Sets the creation date of the object."""
        self.created_at = created_at

    # Getter and Setter for edited_at
    def get_edited_at(self):
        """Gets the last edited date of the object."""
        return self.edited_at

    def set_edited_at(self, edited_at):
        """Sets the last edited date of the object."""
        self.edited_at = edited_at

    """
    Special getter and setter
    """

    def is_special_price_active(self):
        """
        Checks if the special price is currently active.

        The special price is considered active if it's set and the current date & time falls between
        the start and end dates of the special price period.

        Returns:
        bool: True if the special price is set and is active, False otherwise.
        """
        # Check if special price is set
        if not self.get_special_price():
            return False

        active = self.get_special_start_date() <= datetime.datetime.now() <= self.get_special_end_date()

        return active

    def get_current_best_price(self, order_amount=None):
        """
        Returns the current best price for a given order amount.

        If a special price is currently active, it will return this special price.
        If not, it checks if the rebate conditions are met (rebate quantity is greater than
        or equal to order amount and there is a rebate price). If they are, it returns the
        rebate price. If none of these conditions are met, it returns the regular price.

        If order_amount is not supplied, it will either return the special price
        (if it's currently valid) or the regular price.

        Args:
            order_amount (int, optional): The number of items in the order. Defaults to None.

        Returns:
            float: The current best price.
        """
        try:
            if self.get_special_price() and self.is_special_price_active():
                return self.get_special_price()
            elif order_amount is not None and self.get_rebate_quantity() >= order_amount and self.get_rebate_price():
                return self.get_rebate_price()
            else:
                return self.get_price()
        except Exception as e:
            self.logger.error(f"Error getting the best price: {str(e)}")
            return None


    def update(self, bridge_entity_new):
        """
        Updates the current instance with values from a new instance.

        Args:
            bridge_entity_new (YourModel): The new instance with updated values.

        Returns:
            bool: True if update was successful, False otherwise.
        """
        try:
            # Updating fields using the setter methods
            self.set_price(bridge_entity_new.get_price())
            self.set_rebate_quantity(bridge_entity_new.get_rebate_quantity())
            self.set_rebate_price(bridge_entity_new.get_rebate_price())
            self.set_special_price(bridge_entity_new.get_special_price())
            self.set_special_start_date(bridge_entity_new.get_special_start_date())
            self.set_special_end_date(bridge_entity_new.get_special_end_date())
            self.set_edited_at(bridge_entity_new.get_edited_at())

            # Log the update
            return self

        except Exception as e:
            # Handle the error appropriately
            print(f"Error updating YourModel: {e}")
            # Depending on your error handling strategy, you might want to re-raise the exception
            # raise
            return False

    def __repr__(self):
        return f'Price: {self.price}'
