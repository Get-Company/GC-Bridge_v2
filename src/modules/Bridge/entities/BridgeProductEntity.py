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

    # One-to-One relationship
    prices = db.relationship("BridgePriceEntity", uselist=False, back_populates="product", cascade="all, delete-orphan")

    # Categories ist set in the BridgeCategoryEntity

    def get_translation(self, language_code):
        # Find the translation with the given language code using list comprehension
        translation = next((t for t in self.translations if t.language == language_code), None)
        return TranslationWrapper(translation)

    def __repr__(self):
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

    # Foreign key for BridgeProductEntity
    product_id = db.Column(db.Integer, db.ForeignKey('bridge_product_entity.id'))
    product = db.relationship("BridgeProductEntity", back_populates="prices")
