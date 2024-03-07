from src import db
import datetime


class BridgeOrderDetailsEntity(db.Model):
    __tablename__ = 'bridge_order_details_entity'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    api_id = db.Column(db.CHAR(36), nullable=False)
    api_order_id = db.Column(db.CHAR(36), nullable=False)
    erp_nr = db.Column(db.String(255), nullable=False)
    unit = db.Column(db.String(255), nullable=True)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    tax = db.Column(db.Float, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    edited_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)

    # Relations

    order = db.relationship('BridgeOrderEntity', back_populates='order_details')
    order_id = db.Column(db.Integer, db.ForeignKey('bridge_order_entity.id', ondelete='CASCADE'))
    product = db.relationship('BridgeProductEntity', back_populates='order_details')
    product_id = db.Column(db.Integer, db.ForeignKey('bridge_product_entity.id'))

    # Repräsentationsmethode
    def __repr__(self):
        return f"<BridgeOrderDetailsEntity id={self.id}, order_id={self.order_id}, product_id={self.product_id}>"

    # Getter und Setter für jedes Feld
    def get_id(self):
        return self.id

    def get_order_id(self):
        return self.order_id

    def set_order_id(self, value):
        self.order_id = value

    def get_product_id(self):
        return self.product_id

    def set_product_id(self, value):
        self.product_id = value

    def get_erp_nr(self):
        return self.erp_nr

    def set_erp_nr(self, value):
        self.erp_nr = value

    def get_api_id(self):
        return self.api_id

    def set_api_id(self, api_id):
        self.api_id = api_id

    def get_api_order_id(self):
        return self.api_order_id

    def set_api_order_id(self, api_order_id):
        self.api_order_id=api_order_id

    def get_unit_price(self):
        return self.unit_price

    def set_unit_price(self, unit_price):
        self.unit_price = unit_price

    def get_unit(self):
        return self.unit

    def set_unit(self, unit):
        self.unit = unit

    def get_total_price(self):
        return self.total_price

    def set_total_price(self, total_price):
        self.total_price = total_price

    def get_quantity(self):
        return self.quantity

    def set_quantity(self, value):
        self.quantity = value

    def get_name(self):
        return self.name

    def set_name(self, value):
        self.name = value

    def get_tax(self):
        return self.tax

    def set_tax(self, value):
        self.tax = value

    def get_created_at(self):
        return self.created_at

    def get_edited_at(self):
        return self.edited_at

    def set_edited_at(self, value):
        self.edited_at = value

    def to_dict(self):
        return {
            'id': self.id,
            'api_id': self.api_id,
            'api_order_id': self.api_order_id,
            'erp_nr': self.erp_nr,
            'price': self.price,
            'quantity': self.quantity,
            'name': self.name,
            'tax': self.tax,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'edited_at': self.edited_at.isoformat() if self.edited_at else None
        }

    # Update-Method
    def update(self, bridge_entity_new):
        try:

            self.set_order_id(bridge_entity_new.get_order_id())
            self.set_product_id(bridge_entity_new.get_product_id())
            self.set_erp_nr(bridge_entity_new.get_erp_nr())
            self.set_api_id(bridge_entity_new.get_api_id())
            self.set_api_order_id(bridge_entity_new.get_api_order_id())
            self.set_unit_price(bridge_entity_new.get_unit_price())
            self.set_total_price(bridge_entity_new.get_total_price())
            self.set_quantity(bridge_entity_new.get_quantity())
            self.set_name(bridge_entity_new.get_name())
            self.set_tax(bridge_entity_new.get_tax())

            self.set_edited_at(datetime.datetime.now())

            return self
        except Exception as e:
            print(f"Error on updating BridgeOrderDetailsEntity: {e}")
            return None
