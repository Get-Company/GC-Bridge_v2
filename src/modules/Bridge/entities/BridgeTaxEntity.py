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

    def get_erp_nr(self):
        try:
            return self.erp_nr
        except Exception as e:
            print(f"Error: {e}")

    def set_erp_nr(self, erp_nr):
        try:
            self.erp_nr = erp_nr
        except Exception as e:
            print(f"Error: {e}")

    def get_description(self):
        try:
            return self.description
        except Exception as e:
            print(f"Error: {e}")

    def set_description(self, description):
        try:
            self.description = description
        except Exception as e:
            print(f"Error: {e}")

    def get_key(self):
        try:
            return self.key
        except Exception as e:
            print(f"Error: {e}")

    def set_key(self, key):
        try:
            self.key = key
        except Exception as e:
            print(f"Error: {e}")

    def get_key_to_calculate(self):
        return ((self.key / 100) + 1)

    def get_edited_at(self):
        try:
            return self.edited_at
        except Exception as e:
            print(f"Error: {e}")

    def set_edited_at(self, edited_at):
        try:
            self.edited_at = edited_at
        except Exception as e:
            print(f"Error: {e}")

    def __repr__(self):
        return f'Bridge Tax Entity: {self.description} ID: {self.id}'

    