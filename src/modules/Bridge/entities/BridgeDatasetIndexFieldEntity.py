# DB
from src import db
# Tools
import uuid
from datetime import datetime


class BridgeDatasetIndexFieldEntity(db.Model):
    __tablename__ = 'bridge_dataset_index_field_entity'
    id = db.Column(db.String(36), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    index_field_name = db.Column(db.String(128), nullable=False)
    index_field_description = db.Column(db.String(256))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    index_id = db.Column(db.String(36), db.ForeignKey('bridge_dataset_index_entity.id'), nullable=False)

    def __repr__(self):
        return f"<BridgeDatasetIndexFieldEntity(name={self.name})>"
