# DB
from src import db
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
# Tools
import uuid
from datetime import datetime


class BridgeDatasetEntity(db.Model):
    __tablename__ = 'bridge_dataset_entity'
    id = db.Column(db.String(36), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    # One-to-many relationship with indices
    # When a dataset is deleted, its indices should also be deleted
    indices = db.relationship('BridgeDatasetIndexEntity', backref='dataset', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<BridgeDatasetEntity(name={self.name}, description={self.description})>"
