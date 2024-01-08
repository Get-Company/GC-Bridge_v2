from src import db
import datetime


class BridgeTaxEntity(db.Model):
    __tablename__ = 'bridge_tax_entity'

    id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True)
    erp_nr = db.Column(db.Integer(), nullable=False, unique=True)
    description = db.Column(db.Text(), nullable=True)
    key = db.Column(db.Float(), nullable=False)
    created_at = db.Column(db.DateTime(), nullable=True, default=datetime.datetime.now())
    edited_at = db.Column(db.DateTime(), nullable=True, default=datetime.datetime.now())

    # Relations
    products = db.relationship('BridgeProductEntity', backref='tax', lazy=True)

    def __repr__(self):
        return f'Bridge Tax Entity: {self.description} ID: {self.id}'

    