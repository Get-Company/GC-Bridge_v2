from sqlalchemy import JSON

from src import db
import datetime
import json


class BridgeRuleEntity(db.Model):
    __tablename__ = 'bridge_rule_entity'

    id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True)
    name = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text(), nullable=True)
    json = db.Column(JSON, nullable=True)

    def __repr__(self):
        return f'Bridge Rule: {self.name}'
