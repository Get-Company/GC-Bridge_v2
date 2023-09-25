import datetime

from src import db
from ..entities.BridgeCategoryEntity import bridge_category_marketplace_association


class BridgeMarketplaceEntity(db.Model):
    __tablename__ = 'bridge_marketplace_entity'
    id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True)
    name = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text(), nullable=True)
    created_at = db.Column(db.DateTime(), nullable=True, default=datetime.datetime.now())
    edited_at = db.Column(db.DateTime(), nullable=True, default=datetime.datetime.now())

    categories = db.relationship(
        'BridgeCategoryEntity',
        secondary=bridge_category_marketplace_association,
        back_populates='marketplaces'
    )