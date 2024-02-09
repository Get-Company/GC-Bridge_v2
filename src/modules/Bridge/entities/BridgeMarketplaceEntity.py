from src import db
import datetime
from .BridgePriceEntity import BridgePriceEntity
from .BridgeProductEntity import BridgeProductEntity
"""
# CH 01.03.21: 1.4 -> 1.35
# CH 01.03.22: 1.35 -> 1.3
factor_ch = 1.3
# It 06.12.23: 1.26 -> 1.0413
factor_it = 1.0413
"""


class BridgeProductMarketplacePriceAssoc(db.Model):
    __tablename__ = 'bridge_product_marketplace_price_association'
    product_id = db.Column(db.Integer, db.ForeignKey('bridge_product_entity.id'), primary_key=True)
    marketplace_id = db.Column(db.Integer, db.ForeignKey('bridge_marketplace_entity.id'), primary_key=True)
    price_id = db.Column(db.Integer, db.ForeignKey('bridge_price_entity.id'))

    product = db.relationship('BridgeProductEntity', back_populates='marketplace_prices_assoc')
    marketplace = db.relationship('BridgeMarketplaceEntity', back_populates='product_prices_assoc')
    price = db.relationship('BridgePriceEntity', backref=db.backref('marketplace_products', uselist=False))
    use_fixed_price = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f'BridgeProductMarketplace Assoc. {self.product_id}-{self.marketplace_id}-{self.price_id}'


class BridgeCustomerMarketplaceAssoc(db.Model):
    __tablename__ = 'bridge_customer_marketplace_assoc'
    customer_id = db.Column(db.Integer, db.ForeignKey('bridge_customer_entity.id', ondelete="CASCADE"), primary_key=True)
    marketplace_id = db.Column(db.Integer, db.ForeignKey('bridge_marketplace_entity.id', ondelete="CASCADE"), primary_key=True)

    customer_marketplace_id = db.Column(db.String(255), nullable=True, unique=True)

    customer = db.relationship(
        'BridgeCustomerEntity',
        back_populates='marketplace_assoc',

    )
    marketplace = db.relationship(
        'BridgeMarketplaceEntity',
        back_populates='customer_assoc'
    )

    def __repr__(self):
        return f'BridgeCustomerMarketplace Assoc. {self.customer_id}-{self.marketplace_id} | {self.customer_marketplace_id}'


class BridgeOrderMarketplaceAssoc(db.Model):
    __tablename__ = 'bridge_order_marketplace_assoc'
    order_id = db.Column(db.Integer, db.ForeignKey('bridge_order_entity.id', ondelete="CASCADE"), primary_key=True)
    marketplace_id = db.Column(db.Integer, db.ForeignKey('bridge_order_entity.id', ondelete="CASCADE"), primary_key=True)

    def __repr__(self):
        return f'BridgeOrderMarketplace Assoc. {self.order_id}-{self.marketplace_id}'


class BridgeMarketplaceEntity(db.Model):
    __tablename__ = 'bridge_marketplace_entity'

    id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    description = db.Column(db.Text(), nullable=True)
    url = db.Column(db.String(255), nullable=True)
    api_key = db.Column(db.String(255), nullable=True)  # If needed for API-Integration
    api_id = db.Column(db.String(255), nullable=True)
    config = db.Column(db.JSON(), nullable=True)  # JSON-Feld for some dynamic config
    factor = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime(), nullable=True, default=datetime.datetime.now())
    edited_at = db.Column(db.DateTime(), nullable=True, default=datetime.datetime.now())

    # Relations
    product_prices_assoc = db.relationship(
        'BridgeProductMarketplacePriceAssoc',
        back_populates='marketplace')

    customers = db.relationship(
        'BridgeCustomerEntity',
        secondary='bridge_customer_marketplace_assoc',
        back_populates='marketplaces',
        overlaps="marketplace, customer"
    )

    customer_assoc = db.relationship(
        'BridgeCustomerMarketplaceAssoc',
        back_populates='marketplace',
        overlaps="customers"
    )

    orders = db.relationship('BridgeOrderEntity', back_populates='marketplace')

    # Getter and Setter Methods
    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_description(self):
        return self.description

    def set_description(self, description):
        self.description = description

    def get_url(self):
        return self.url

    def set_url(self, url):
        self.url = url

    def get_api_key(self):
        return self.api_key

    def set_api_key(self, api_key):
        self.api_key = api_key

    def get_api_id(self):
        return self.api_id

    def set_api_id(self, api_id):
        self.api_id = api_id

    def get_config(self):
        return self.config

    def set_config(self, config):
        self.config = config

    def get_created_at(self):
        return self.created_at

    def get_edited_at(self):
        return self.edited_at

    def set_edited_at(self, edited_at):
        self.edited_at = edited_at

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'url': self.url,
            'api_key': self.api_key,
            'api_id': self.api_id,
            'config': self.config,
            'factor': self.factor,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'edited_at': self.edited_at.isoformat() if self.edited_at else None
        }

    # Update Method
    def update(self, bridge_entity_new):
        """
        Updates the current BridgeMarketplaceEntity instance with values from a new instance.

        Args:
            bridge_entity_new (BridgeMarketplaceEntity): The new BridgeMarketplaceEntity instance with updated values.
        """
        self.set_name(bridge_entity_new.get_name())
        self.set_description(bridge_entity_new.get_description())
        self.set_url(bridge_entity_new.get_url())
        self.set_api_key(bridge_entity_new.get_api_key())
        self.set_api_id(bridge_entity_new.get_api_id())
        # config is set manually
        # factor is set manually
        self.set_edited_at(datetime.datetime.now())

        return self

    def __repr__(self):
        return f" Marketplace {self.name} id:{self.id}"

""" 
Example Queries from AI

###
Welche Produkte sind in einem bestimmten Marktplatz verfügbar?
###
marketplace_id = 1  # Beispiel-Marktplatz-ID
products_in_marketplace = BridgeProductEntity.query.join(
    ProductMarketplacePriceAssociation
).filter(
    ProductMarketplacePriceAssociation.marketplace_id == marketplace_id
).all()

for product in products_in_marketplace:
    print(product.erp_nr)


###
Welche Marktplätze bieten ein bestimmtes Produkt an?
###
product_id = 1  # Beispiel-Produkt-ID
marketplaces_for_product = BridgeMarketplaceEntity.query.join(
    ProductMarketplacePriceAssociation
).filter(
    ProductMarketplacePriceAssociation.product_id == product_id
).all()

for marketplace in marketplaces_for_product:
    print(marketplace.name)


###
Abrufen des Preises eines Produkts auf einem bestimmten Marktplatz
###
product_id = 1  # Beispiel-Produkt-ID
marketplace_id = 1  # Beispiel-Marktplatz-ID

association = ProductMarketplacePriceAssociation.query.filter_by(
    product_id=product_id, 
    marketplace_id=marketplace_id
).first()

if association and association.price:
    print(f"Preis: {association.price.amount}")


###
Auflisten aller Produkte mit ihren Preisen auf einem bestimmten Marktplatz
###
marketplace_id = 1  # Beispiel-Marktplatz-ID
associations = ProductMarketplacePriceAssociation.query.filter_by(
    marketplace_id=marketplace_id
).all()

for assoc in associations:
    print(f"Produkt {assoc.product.erp_nr} hat den Preis {assoc.price.amount}")


###
Abrufen aller Preise für ein bestimmtes Produkt über verschiedene Marktplätze hinweg
###
product_id = 1  # Beispiel-Produkt-ID
associations = ProductMarketplacePriceAssociation.query.filter_by(
    product_id=product_id
).all()

for assoc in associations:
    print(f"Marktplatz {assoc.marketplace.name} hat den Preis {assoc.price.amount}")

"""
