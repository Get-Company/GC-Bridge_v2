from pprint import pprint

from sqlalchemy import update, Text
from sqlalchemy.orm import aliased

from src import db
import datetime
import json


class BridgeProductsCategoriesAssoc(db.Model):
    __tablename__ = 'bridge_product_categories_assoc'

    product_id = db.Column('product_id', db.Integer, db.ForeignKey('bridge_product_entity.id'), primary_key=True)
    category_id = db.Column('category_id', db.Integer, db.ForeignKey('bridge_category_entity.id'), primary_key=True)
    sort = db.Column('sort', db.Integer, nullable=False, default=0)

    # Relationen zu den verbundenen Tabellen
    product = db.relationship("BridgeProductEntity", back_populates="categories_assoc")
    category = db.relationship("BridgeCategoryEntity", back_populates="products_assoc")

    def get_sort(self):
        if self.sort:
            return self.sort

    def set_sort(self, sort):
        self.sort = sort


class TranslationWrapper:
    def __init__(self, translation):
        self.translation = translation

    def __getattr__(self, name):
        if self.translation:
            return getattr(self.translation, name)
        return None


class BridgeCategoryEntity(db.Model):
    """
    Only use after_category_id and parent_category_id for building the tree and working with paths
    Fields like:
    cat_nr, cat_parent_nr, cat_tree_path, erp_nr, erp_nr_parent, erp_tree_path
    are deprecated
    """
    __tablename__ = 'bridge_category_entity'

    id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True)
    after_category_id = db.Column(db.Integer(), db.ForeignKey('bridge_category_entity.id'), nullable=True)
    parent_category_id = db.Column(db.Integer(), db.ForeignKey('bridge_category_entity.id'), nullable=True)
    path = db.Column(Text, nullable=True)
    erp_nr = db.Column(db.Integer(), nullable=False, unique=True, comment='Deprecated: use another field instead')
    erp_nr_parent = db.Column(db.Integer(), nullable=True, comment='Deprecated: use another field instead')
    erp_tree_path = db.Column(db.JSON, nullable=True, comment='Deprecated: use another field instead')
    cat_nr = db.Column(db.Integer(), nullable=True, unique=True, comment='Deprecated: use another field instead')
    cat_parent_nr = db.Column(db.Integer(), nullable=True, comment='Deprecated: use another field instead')
    cat_tree_path = db.Column(db.JSON, nullable=True, comment='Deprecated: use another field instead')
    sw6_id = db.Column(db.CHAR(36), nullable=False)
    created_at = db.Column(db.DateTime(), nullable=True, default=datetime.datetime.now())
    edited_at = db.Column(db.DateTime(), nullable=True, default=datetime.datetime.now())

    # Relations
    translations = db.relationship(
        'BridgeCategoryTranslation',
        backref='category',
        lazy='subquery',
        cascade='all, delete-orphan')

    products_assoc = db.relationship("BridgeProductsCategoriesAssoc", back_populates="category")

    @property
    def products(self):
        """
        Returns a list of products associated with the category.

        This property navigates through the relationship with the
        "BridgeProductsCategoriesAssoc" entity,
        collecting all the associated "BridgeProductEntity" objects,
        effectively giving us all the products related to this category.

        :return: List of "BridgeProductEntity" objects associated with the category.
        """
        return [assoc.product for assoc in self.products_assoc]

    def get_prod_cat_assoc(self, product):
        assoc = BridgeProductsCategoriesAssoc.query.filter(
            BridgeProductsCategoriesAssoc.category_id == self.get_id(),
            BridgeProductsCategoriesAssoc.product_id == product.get_id()
        ).one_or_none()
        if assoc:
            return assoc

    def get_id(self):
        return self.id

    def get_after_category_id(self):
        if self.after_category_id:
            return self.after_category_id

    def set_after_category_id(self, after_category_id):
        if after_category_id:
            self.after_category_id = after_category_id

    def get_parent_category_id(self):
        if self.parent_category_id:
            return self.parent_category_id

    def set_parent_category_id(self, parent_category_id):
        if parent_category_id:
            self.after_category_id = parent_category_id

    def get_translation(self, language_code="DE_de"):
        # Find the translation with the given language code using list comprehension
        translation = next((t for t in self.translations if t.language == language_code), None)
        return TranslationWrapper(translation)

    # Getter and Setter for erp_nr
    def get_erp_nr(self):
        print("Warning: 'erp_nr' is deprecated.")
        return self.erp_nr

    def set_erp_nr(self, value):
        self.erp_nr = value

    # Getter and Setter for erp_nr_parent
    def get_erp_nr_parent(self):
        print("Warning: 'erp_nr_parent' is deprecated.")
        return self.erp_nr_parent

    def set_erp_nr_parent(self, value):
        self.erp_nr_parent = value

    # Getter and Setter for erp_tree_path
    def get_erp_tree_path(self):
        print("Warning: 'erp_tree_path' is deprecated.")
        return self.erp_tree_path

    def set_erp_tree_path(self, value):
        self.erp_tree_path = value

    # Getter and Setter for cat_nr
    def get_cat_nr(self):
        print("Warning: 'cat_nr' is deprecated.")
        return self.cat_nr

    def set_cat_nr(self, value):
        self.cat_nr = value

    # Getter and Setter for cat_parent_nr
    def get_cat_parent_nr(self):
        print("Warning: 'cat_parent_nr' is deprecated.")
        if self.cat_parent_nr and self.cat_parent_nr > 0:
            return self.cat_parent_nr
        else:
            return None

    def set_cat_parent_nr(self, value):
        self.cat_parent_nr = value

    # Getter and Setter for cat_tree_path
    def get_cat_tree_path(self):
        print("Warning: 'cat_tree_path' is deprecated.")
        return self.cat_tree_path

    def set_cat_tree_path(self, value):
        self.cat_tree_path = value

    def get_sw6_id(self):
        if self.sw6_id:
            return self.sw6_id
        else:
            return None

    def set_sw6_id(self, sw6_id):
        self.sw6_id = sw6_id

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

    def __repr__(self):
        return f'<BridgeCategoryEntity ID: {self.id} {self.get_translation().get_name()}'

    """
    Special Getter and Setter
    """
    def get_main(self):
        tree_path_list = json.loads(self.get_erp_tree_path())
        main_category_id = tree_path_list[0]
        main_category = self.query.filter_by(erp_nr=main_category_id).one_or_none()
        if main_category:
            return main_category
        else:
            return None

    def get_parent(self):
        if self.get_parent_category_id():
            return BridgeCategoryEntity().query.get(self.get_parent_category_id())
        else:
            print("No parent available!")
            return False

    def get_tree_path_names_as_list(self):
        tree_path_list = json.loads(self.get_erp_erp_tree_path())
        if tree_path_list:
            names_list = []
            tree_path_list.pop(0)  # Entfernt das erste Element, falls die Liste nicht leer ist
            for item in tree_path_list:
                names_list.append(self.query.filter_by(erp_nr=item).one_or_none())
            return tree_path_list
        else:
            return None

    def get_current_tree_level(self):
        tree_path_list = json.loads(self.get_erp_tree_path())
        return len(tree_path_list)

    def calculate_path(self, return_json=True):
        path = [self.cat_nr]
        current_category = self
        while current_category.cat_parent_nr != 0:  # assuming 0 indicates no parent
            current_category = BridgeCategoryEntity().query.filter_by(cat_nr=current_category.cat_parent_nr).first()
            path.append(current_category.cat_nr)
        path.reverse()
        if return_json:
            return json.dumps(path)  # Converts list to JSON string
        else:
            return path

    def update_path(self):
        self.cat_tree_path = self.calculate_path()


class BridgeCategoryTranslation(db.Model):
    __tablename__ = 'bridge_category_translation'

    id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True)
    language = db.Column(db.String(5), nullable=False)  # language format: 'DE_de', 'GB_en', etc.
    name = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text(), nullable=True)
    description_short = db.Column(db.Text(), nullable=True)
    sw6_id = db.Column(db.CHAR(36), nullable=False)
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

    def get_sw6_id(self):
        return self.sw6_id

    def set_sw6_id(self, sw6_id):
        self.sw6_id = sw6_id

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
