# DB
from src import db
# Tools
import uuid
from datetime import datetime


class BridgeDatasetIndexEntity(db.Model):
    __tablename__ = 'bridge_dataset_index_entity'
    id = db.Column(db.String(36), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    index_name = db.Column(db.String(128), nullable=False)
    index_description = db.Column(db.String(256))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    #  Relations
    dataset_id = db.Column(db.String(36), db.ForeignKey('bridge_dataset_entity.id'), nullable=False)
    index_fields = db.relationship('BridgeDatasetIndexFieldEntity', backref='index', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<BridgeDatasetIndexEntity(name={self.name})>"