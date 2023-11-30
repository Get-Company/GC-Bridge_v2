from src import db
import datetime

BridgeProductsMediaAssoc = db.Table('media_product_association',
                                    db.Column('media_id', db.Integer, db.ForeignKey('bridge_media_entity.id', ondelete="CASCADE")),
                                    db.Column('product_id', db.Integer, db.ForeignKey('bridge_product_entity.id', ondelete="CASCADE"))
                                    )

BridgeCategoryMediaAssoc = db.Table('media_category_association',
                                    db.Column('media_id', db.Integer, db.ForeignKey('bridge_media_entity.id', ondelete="CASCADE")),
                                    db.Column('category_id', db.Integer, db.ForeignKey('bridge_category_entity.id', ondelete="CASCADE"))
                                    )


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
    title = db.Column(db.Text(), nullable=False)
    description = db.Column(db.Text(), nullable=False)
    created_at = db.Column(db.DateTime(), nullable=True, default=datetime.datetime.now())
    edited_at = db.Column(db.DateTime(), nullable=True, default=datetime.datetime.now())

    # Foreign keys for the relationship of Product and Category
    # product_id = db.Column(db.Integer, db.ForeignKey('bridge_product_entity.id'), nullable=True)
    # category_id = db.Column(db.Integer, db.ForeignKey('bridge_category_entity.id'), nullable=True)

    # Relationships
    products = db.relationship("BridgeProductEntity",
                               secondary=BridgeProductsMediaAssoc,
                               backref=db.backref("media", cascade="all, delete"),
                               passive_deletes=True)

    categories = db.relationship("BridgeCategoryEntity",
                                 secondary=BridgeCategoryMediaAssoc,
                                 backref=db.backref("media", cascade="all, delete"),
                                 passive_deletes=True)

    def get_translation_(self, language_code):
            translation = next((t for t in self.translations if t.language == language_code), None)
            return MediaTranslationWrapper(translation)

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
