from src import db
import datetime


class BridgeOrderEntity(db.Model):
    __tablename__ = "bridge_order_entity"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    api_id = db.Column(db.CHAR(36), nullable=False)
    description = db.Column(db.String(4096), nullable=True)
    total_price = db.Column(db.Float, nullable=False)
    total_tax = db.Column(db.Float, nullable=True)
    shipping_costs = db.Column(db.Float, nullable=True)
    payment_method = db.Column(db.String(255), nullable=True)
    shipping_method = db.Column(db.String(255), nullable=True)
    order_number = db.Column(db.String(255), nullable=True)

    # ERP
    erp_order_id = db.Column(db.String(255), nullable=True)

    # States
    order_state = db.Column(db.String(20), nullable=False)
    shipping_state = db.Column(db.String(20), nullable=False)
    payment_state = db.Column(db.String(20), nullable=False)

    # Datetime
    purchase_date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    edited_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)

    # Relations
    customer = db.relationship('BridgeCustomerEntity',back_populates='orders')
    customer_id = db.Column(db.Integer, db.ForeignKey('bridge_customer_entity.id'))

    marketplace = db.relationship('BridgeMarketplaceEntity', back_populates='orders')
    marketplace_id = db.Column(db.Integer, db.ForeignKey('bridge_marketplace_entity.id'))

    order_details = db.relationship('BridgeOrderDetailsEntity', back_populates='order', cascade="all,delete-orphan")

    def __repr__(self):
        if self.order_number:
            return f"Order No: {self.order_number} with a total of {self.total_price}."
        else:
            return "BridgeOrderEntity instantiated, data not filled yet."

    # id
    def get_id(self):
        try:
            return self.id
        except Exception as e:
            print("Error getting id:", str(e))

    # api_id
    def get_api_id(self):
        try:
            return self.api_id
        except Exception as e:
            print("Error getting api_id:", str(e))

    def set_api_id(self, value):
        try:
            self.api_id = value
        except Exception as e:
            print("Error setting api_id:", str(e))

    # description
    def get_description(self):
        try:
            return self.description
        except Exception as e:
            print("Error getting description:", str(e))

    def set_description(self, value):
        try:
            self.description = value
        except Exception as e:
            print("Error setting description:", str(e))

    # total_price
    def get_total_price(self):
        try:
            return self.total_price
        except Exception as e:
            print("Error getting total_price:", str(e))

    def set_total_price(self, value):
        try:
            self.total_price = value
        except Exception as e:
            print("Error setting total_price:", str(e))

    # total_tax
    def get_total_tax(self):
        try:
            return self.total_tax
        except Exception as e:
            print("Error getting total_tax:", str(e))

    def set_total_tax(self, value):
        try:
            self.total_tax = value
        except Exception as e:
            print("Error setting total_tax:", str(e))

    # shipping_costs
    def get_shipping_costs(self):
        try:
            return self.shipping_costs
        except Exception as e:
            print("Error getting shipping_costs:", str(e))

    def set_shipping_costs(self, value):
        try:
            self.shipping_costs = value
        except Exception as e:
            print("Error setting shipping_costs:", str(e))

    # payment_method
    def get_payment_method(self):
        try:
            return self.payment_method
        except Exception as e:
            print("Error getting payment_method:", str(e))

    def set_payment_method(self, value):
        try:
            self.payment_method = value
        except Exception as e:
            print("Error setting payment_method:", str(e))

    # shipping_method
    def get_shipping_method(self):
        try:
            return self.shipping_method
        except Exception as e:
            print("Error getting shipping_method:", str(e))

    def set_shipping_method(self, value):
        try:
            self.shipping_method = value
        except Exception as e:
            print("Error setting shipping_method:", str(e))

    # order_number
    def get_order_number(self):
        try:
            return self.order_number
        except Exception as e:
            print("Error getting order_number:", str(e))

    def set_order_number(self, value):
        try:
            self.order_number = value
        except Exception as e:
            print("Error setting order_number:", str(e))

    # erp_order_id
    def get_erp_order_id(self):
        try:
            return self.erp_order_id
        except Exception as e:
            print("Error getting erp_order_id:", str(e))

    def set_erp_order_id(self, value):
        try:
            self.erp_order_id = value
        except Exception as e:
            print("Error setting erp_order_id:", str(e))

    # order_state
    def get_order_state(self):
        try:
            return self.order_state
        except Exception as e:
            print("Error getting order_state:", str(e))

    def set_order_state(self, value):
        try:
            self.order_state = value
        except Exception as e:
            print("Error setting order_state:", str(e))

    # shipping_state
    def get_shipping_state(self):
        try:
            return self.shipping_state
        except Exception as e:
            print("Error getting shipping_state:", str(e))

    def set_shipping_state(self, value):
        try:
            self.shipping_state = value
        except Exception as e:
            print("Error setting shipping_state:", str(e))

    # payment_state
    def get_payment_state(self):
        try:
            return self.payment_state
        except Exception as e:
            print("Error getting payment_state:", str(e))

    def set_payment_state(self, value):
        try:
            self.payment_state = value
        except Exception as e:
            print("Error setting payment_state:", str(e))

    # purchase_date
    def get_purchase_date(self):
        try:
            return self.purchase_date
        except Exception as e:
            print("Error getting purchase_date:", str(e))

    def set_purchase_date(self, value):
        try:
            self.purchase_date = value
        except Exception as e:
            print("Error setting purchase_date:", str(e))

    # created_at
    def get_created_at(self):
        try:
            return self.created_at
        except Exception as e:
            print("Error getting created_at:", str(e))

    def set_created_at(self, value):
        try:
            self.created_at = value
        except Exception as e:
            print("Error setting created_at:", str(e))

    # edited_at
    def get_edited_at(self):
        try:
            return self.edited_at
        except Exception as e:
            print("Error getting edited_at:", str(e))

    def set_edited_at(self, value):
        try:
            self.edited_at = value
        except Exception as e:
            print("Error setting edited_at:", str(e))

    # Update method
    def update(self, bridge_entity_new):
        """
        Updates the current instance with values from a new instance.

        Args:
            bridge_entity_new (BridgeOrderEntity): The new instance with updated values.

        Returns:
            BridgeOrderEntity: self, if update was successful, None otherwise.
        """
        try:
            # Updating fields using the setter methods
            self.set_api_id(bridge_entity_new.get_api_id())
            self.set_description(bridge_entity_new.get_description())
            self.set_total_price(bridge_entity_new.get_total_price())
            self.set_total_tax(bridge_entity_new.get_total_tax())
            self.set_shipping_costs(bridge_entity_new.get_shipping_costs())
            self.set_payment_method(bridge_entity_new.get_payment_method())
            self.set_shipping_method(bridge_entity_new.get_shipping_method())
            self.set_order_number(bridge_entity_new.get_order_number())
            self.set_erp_order_id(bridge_entity_new.get_erp_order_id())
            self.set_order_state(bridge_entity_new.get_order_state())
            self.set_shipping_state(bridge_entity_new.get_shipping_state())
            self.set_payment_state(bridge_entity_new.get_payment_state())
            self.set_purchase_date(bridge_entity_new.get_purchase_date())
            self.set_edited_at(datetime.datetime.now())

            return self

        except Exception as e:
            print(f"Error updating BridgeOrderEntity: {e}")
            return None

    def to_dict(self):
        return {
            "id": self.id,
            "total_price": self.get_total_price(),
            "total_tax": self.get_total_tax(),
            "order_details": [order_detail.to_dict() for order_detail in self.order_details],
            "customer": self.customer.to_dict(),
            'marketplace': self.marketplace.to_dict()
        }
