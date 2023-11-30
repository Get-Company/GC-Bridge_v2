from src import db
import datetime


# Assoziationstabelle für die Many-to-Many Beziehung
BridgeProductsCategoriesAssoc = db.Table('bridge_product_categories_assoc',
                                          db.Column('product_id', db.Integer, db.ForeignKey('bridge_product_entity.id', ondelete='CASCADE'), primary_key=True),
                                          db.Column('category_id', db.Integer, db.ForeignKey('bridge_category_entity.id', ondelete='CASCADE'), primary_key=True)
                                          )

class TranslationWrapper:
    def __init__(self, translation):
        self.translation = translation

    def __getattr__(self, name):
        if self.translation:
            return getattr(self.translation, name)
        return None


class BridgeCategoryEntity(db.Model):
    __tablename__ = 'bridge_category_entity'

    id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True)
    erp_nr = db.Column(db.Integer(), nullable=False, unique=True)
    erp_nr_parent = db.Column(db.Integer(), nullable=True)
    tree_path = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime(), nullable=True, default=datetime.datetime.now())
    edited_at = db.Column(db.DateTime(), nullable=True, default=datetime.datetime.now())

    # Relations
    translations = db.relationship(
        'BridgeCategoryTranslation',
        backref='category',
        lazy='subquery',
        cascade='all, delete-orphan')

    products = db.relationship('BridgeProductEntity', secondary=BridgeProductsCategoriesAssoc, lazy='subquery',
                               backref=db.backref('categories', lazy=False))

    def get_translation(self, language_code):
        # Find the translation with the given language code using list comprehension
        translation = next((t for t in self.translations if t.language == language_code), None)
        return TranslationWrapper(translation)

    def __repr__(self):
        print(f'Bridge Category Entity: {self.get_translation("DE_de").name} ID: {self.id}')


class BridgeCategoryTranslation(db.Model):
    __tablename__ = 'bridge_category_translation'

    id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True)
    language = db.Column(db.String(5), nullable=False)  # language format: 'DE_de', 'GB_en', etc.
    name = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text(), nullable=True)
    description_short = db.Column(db.Text(), nullable=True)
    created_at = db.Column(db.DateTime(), nullable=True, default=datetime.datetime.now())
    edited_at = db.Column(db.DateTime(), nullable=True, default=datetime.datetime.now())

    # Relations
    category_id = db.Column(db.Integer(), db.ForeignKey('bridge_category_entity.id', ondelete='CASCADE'),
                            nullable=False)
