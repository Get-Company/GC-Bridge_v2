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
    erp_nr = db.Column(db.String(255), nullable=True, unique=True)
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
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    tax_id = db.Column(db.Integer(), db.ForeignKey('bridge_tax_entity.id'), nullable=True)

    # Categories ist set in the BridgeCategoryEntity

    def get_translation_(self, language_code):
        # Usage example:
        # product = BridgeProductEntity.query.first()
        # german_name = product.get_translation_('DE_de').name
        # english_description = product.get_translation_('GB_en').description
        translation = self.translations.filter_by(language=language_code).first()
        return TranslationWrapper(translation)

    def __repr__(self):
        return f'Bridge Product Entity: {self.get_("DE_de").name} ID: {self.id}'


class BridgeProductTranslation(db.Model):
    __tablename__ = 'bridge_product_translation'

    id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True)
    language = db.Column(db.String(5), nullable=False)  # language format: 'DE_de', 'GB_en', etc.
    name = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text(4294967295), nullable=True)

    # Relations
    product_id = db.Column(db.Integer(), db.ForeignKey('bridge_product_entity.id', ondelete='CASCADE'), nullable=False)