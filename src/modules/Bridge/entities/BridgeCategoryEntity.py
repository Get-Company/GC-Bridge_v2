from src import db
import datetime
import json

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
                               backref=db.backref('categories', lazy=True))

    def get_translation(self, language_code="DE_de"):
        # Find the translation with the given language code using list comprehension
        translation = next((t for t in self.translations if t.language == language_code), None)
        return TranslationWrapper(translation)

    # Getter and Setter for erp_nr
    def get_erp_nr(self):
        return self.erp_nr

    def set_erp_nr(self, value):
        self.erp_nr = value

    # Getter and Setter for erp_nr_parent
    def get_erp_nr_parent(self):
        return self.erp_nr_parent

    def set_erp_nr_parent(self, value):
        self.erp_nr_parent = value

    # Getter and Setter for tree_path
    def get_tree_path(self):
        return self.tree_path

    def set_tree_path(self, value):
        self.tree_path = value

    # Getter and Setter for created_at
    def get_created_at(self):
        return self.created_at

    def set_created_at(self, value):
        self.created_at = value

    # Getter and Setter for edited_at
    def get_edited_at(self):
        return self.edited_at

    def set_edited_at(self, value):
        self.edited_at = value

    def update(self, bridge_entity_new):
        """
        Updates the current BridgeCategoryEntity instance with values from a new instance.

        Args:
            bridge_entity_new (BridgeCategoryEntity): The new BridgeCategoryEntity instance with updated values.
        """
        self.set_erp_nr(bridge_entity_new.get_erp_nr())
        self.set_erp_nr_parent(bridge_entity_new.get_erp_nr_parent())
        self.set_tree_path(bridge_entity_new.get_tree_path())
        self.set_created_at(bridge_entity_new.get_created_at())
        self.set_edited_at(bridge_entity_new.get_edited_at())

        return self

    """
    Special Getter and Setter
    """
    def get_main(self):
        tree_path_list = json.loads(self.get_tree_path())
        main_category_id = tree_path_list[0]
        main_category = self.query.filter_by(erp_nr=main_category_id).one_or_none()
        if main_category:
            return main_category
        else:
            return None

    def get_tree_path_names_as_list(self):
        tree_path_list = json.loads(self.get_tree_path())
        if tree_path_list:
            names_list = []
            tree_path_list.pop(0)  # Entfernt das erste Element, falls die Liste nicht leer ist
            for item in tree_path_list:
                names_list.add = self.query.filter_by(erp_nr=item).one_or_none()
            return tree_path_list
        else:
            return None

    def __repr__(self):
        return f'Bridge Category Entity ID: {self.erp_nr}'


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

    # Getter and Setter for language
    def get_language(self):
        return self.language

    def set_language(self, value):
        self.language = value

    # Getter and Setter for name
    def get_name(self):
        return self.name

    def set_name(self, value):
        self.name = value

    # Getter and Setter for description
    def get_description(self):
        return self.description

    def set_description(self, value):
        self.description = value

    # Getter and Setter for description_short
    def get_description_short(self):
        return self.description_short

    def set_description_short(self, value):
        self.description_short = value

    # Getter and Setter for created_at
    def get_created_at(self):
        return self.created_at

    def set_created_at(self, value):
        self.created_at = value

    # Getter and Setter for edited_at
    def get_edited_at(self):
        return self.edited_at

    def set_edited_at(self, value):
        self.edited_at = value

    def update(self, bridge_category_translation_new):
        """
        Aktualisiert die aktuelle BridgeCategoryTranslation-Instanz mit Werten aus einer neuen Instanz.

        Args:
            bridge_category_translation_new (BridgeCategoryTranslation): Die neue BridgeCategoryTranslation-Instanz mit aktualisierten Werten.
        """
        self.set_language(bridge_category_translation_new.get_language())
        self.set_name(bridge_category_translation_new.get_name())
        self.set_description(bridge_category_translation_new.get_description())
        self.set_description_short(bridge_category_translation_new.get_description_short())
        self.set_created_at(bridge_category_translation_new.get_created_at())
        self.set_edited_at(bridge_category_translation_new.get_edited_at())

        return self

    def __repr__(self):
        return f'Bridge Category Translation ID: {self.name}'
