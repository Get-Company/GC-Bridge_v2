from src import db
import datetime


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
    erp_nr = db.Column(db.Integer(), nullable=False)
    erp_nr_parent = db.Column(db.Integer(), nullable=True)
    tree_path = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime(), nullable=True, default=datetime.datetime.now())
    edited_at = db.Column(db.DateTime(), nullable=True, default=datetime.datetime.now())

    # Relations
    translations = db.relationship(
        'BridgeCategoryTranslation',
        backref='category',
        lazy='dynamic',
        cascade='all, delete-orphan')

    def get_(self, language_code):
        # Usage example:
        # category = BridgeCategoryEntity.query.first()
        # german_title = category.get_('DE_de').title
        # english_description = category.get_('GB_en').description
        translation = self.translations.filter_by(language=language_code).first()
        return TranslationWrapper(translation)

    def __repr__(self):
        print(f'"Bridge Category Entity: {self.get_("DE_de").title}" ID: {self.id}')


class BridgeCategoryTranslation(db.Model):
    __tablename__ = 'bridge_category_translation'

    id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True)
    language = db.Column(db.String(5), nullable=False)  # language format: 'DE_de', 'GB_en', etc.
    name = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text(), nullable=True)
    description_short = db.Column(db.Text(), nullable=True)

    # Relations
    category_id = db.Column(db.Integer(), db.ForeignKey('bridge_category_entity.id', ondelete='CASCADE'),
                            nullable=False)
