import uuid

from config import GCBridgeConfig
from src import db
import datetime


class BridgeProductsMediaAssoc(db.Model):
    __tablename__ = 'media_product_association'
    media_id = db.Column(db.Integer, db.ForeignKey('bridge_media_entity.id', ondelete="CASCADE"), primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('bridge_product_entity.id', ondelete="CASCADE"), primary_key=True)
    sort = db.Column(db.Integer)
    product = db.relationship("BridgeProductEntity", backref=db.backref("media_assocs", cascade="all, delete"))


class BridgeCategoryMediaAssoc(db.Model):
    __tablename__ = 'media_category_association'
    media_id = db.Column(db.Integer, db.ForeignKey('bridge_media_entity.id', ondelete="CASCADE"), primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('bridge_category_entity.id', ondelete="CASCADE"),
                            primary_key=True)
    sort = db.Column(db.Integer)
    category = db.relationship("BridgeCategoryEntity", backref=db.backref("media_assocs", cascade="all, delete"))


class MediaTranslationWrapper:
    def __init__(self, translation):
        self.translation = translation

    def __getattr__(self, name):
        if self.translation:
            return getattr(self.translation, name)
        return None


class BridgeMediaEntity(db.Model):
    __tablename__ = 'bridge_media_entity'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    file_name = db.Column(db.String(255), nullable=False, unique=True)
    file_type = db.Column(db.String(50), nullable=False)
    file_size = db.Column(db.Integer, nullable=True)  # Can be null, when the file was not found and calculating the size was not possible
    title = db.Column(db.Text(), nullable=True)
    description = db.Column(db.Text(), nullable=True)
    sw6_id = db.Column(db.CHAR(36), default=uuid.uuid4().hex, nullable=False)
    created_at = db.Column(db.DateTime(), nullable=True, default=datetime.datetime.now())
    edited_at = db.Column(db.DateTime(), nullable=True, default=datetime.datetime.now())

    # New relationships
    product_assocs = db.relationship("BridgeProductsMediaAssoc", backref=db.backref("media"), cascade="all, delete",
                                     passive_deletes=True)
    category_assocs = db.relationship("BridgeCategoryMediaAssoc", backref=db.backref("media"), cascade="all, delete",
                                      passive_deletes=True)

    def get_id(self):
        if self.id:
            return self.id

    def get_translation_(self, language_code):
        translation = next((t for t in self.translations if t.language == language_code), None)
        return MediaTranslationWrapper(translation)

    # Getter und Setter für file_name
    def get_file_name(self):
        return self.file_name

    def set_file_name(self, value):
        self.file_name = value

    # Getter und Setter für file_type
    def get_file_type(self):
        return self.file_type

    def set_file_type(self, value):
        self.file_type = value

    # Getter und Setter für file_size
    def get_file_size(self):
        return self.file_size

    def set_file_size(self, value):
        self.file_size = value

    # Getter und Setter für title
    def get_title(self):
        return self.title

    def set_title(self, value):
        self.title = value

    # Getter und Setter für description
    def get_description(self):
        return self.description

    def set_description(self, value):
        self.description = value

    # Getter und Setter für created_at
    def get_created_at(self):
        return self.created_at

    def set_created_at(self, value):
        self.created_at = value

    def get_sw6_id(self):
        if self.sw6_id:
            return self.sw6_id
        else:
            return None

    def set_sw6_id(self, sw6_id):
        self.sw6_id = sw6_id

    # Getter und Setter für edited_at
    def get_edited_at(self):
        return self.edited_at

    def set_edited_at(self, value):
        self.edited_at = value

    def update(self, bridge_media_entity_new):
        """
        Aktualisiert die aktuelle BridgeMediaEntity-Instanz mit Werten aus einer neuen Instanz.

        Args:
            bridge_media_entity_new (BridgeMediaEntity): Die neue BridgeMediaEntity-Instanz mit aktualisierten Werten.
        """
        self.set_file_name(bridge_media_entity_new.get_file_name())
        self.set_file_type(bridge_media_entity_new.get_file_type())
        self.set_file_size(bridge_media_entity_new.get_file_size())
        self.set_title(bridge_media_entity_new.get_title())
        self.set_description(bridge_media_entity_new.get_description())
        self.set_created_at(bridge_media_entity_new.get_created_at())
        self.set_edited_at(bridge_media_entity_new.get_edited_at())

        return self

    def get_media_url(self):
        return f"{GCBridgeConfig.ASSETS_PATH}{GCBridgeConfig.IMG_PATH}/{self.get_file_name()}.{self.get_file_type()}"

    def __repr__(self):
        return f"<BridgeMediaEntity(id={self.id}, file_name={self.file_name}, file_type={self.file_type})>"


class BridgeMediaTranslation(db.Model):
    __tablename__ = 'bridge_media_translation'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    language = db.Column(db.String(5), nullable=False)
    title = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text(), nullable=True)
    created_at = db.Column(db.DateTime, nullable=True, default=datetime.datetime.now())
    edited_at = db.Column(db.DateTime, nullable=True, default=datetime.datetime.now())

    # Relations
    media_id = db.Column(db.Integer, db.ForeignKey('bridge_media_entity.id', ondelete='CASCADE'), nullable=False)

    # Getter und Setter für language
    def get_language(self):
        return self.language

    def set_language(self, value):
        self.language = value

    # Getter und Setter für title
    def get_title(self):
        return self.title

    def set_title(self, value):
        self.title = value

    # Getter und Setter für description
    def get_description(self):
        return self.description

    def set_description(self, value):
        self.description = value

    # Getter und Setter für created_at
    def get_created_at(self):
        return self.created_at

    def set_created_at(self, value):
        self.created_at = value

    # Getter und Setter für edited_at
    def get_edited_at(self):
        return self.edited_at

    def set_edited_at(self, value):
        self.edited_at = value

    # Getter und Setter für media_id
    def get_media_id(self):
        return self.media_id

    def set_media_id(self, value):
        self.media_id = value

    def update(self, bridge_media_translation_new):
        """
        Aktualisiert die aktuelle BridgeMediaTranslation-Instanz mit Werten aus einer neuen Instanz.

        Args:
            bridge_media_translation_new (BridgeMediaTranslation): Die neue BridgeMediaTranslation-Instanz mit aktualisierten Werten.
        """
        self.set_language(bridge_media_translation_new.get_language())
        self.set_title(bridge_media_translation_new.get_title())
        self.set_description(bridge_media_translation_new.get_description())
        self.set_created_at(bridge_media_translation_new.get_created_at())
        self.set_edited_at(bridge_media_translation_new.get_edited_at())
        self.set_media_id(bridge_media_translation_new.get_media_id())

        return self