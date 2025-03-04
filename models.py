from app import db
from datetime import datetime

class AITool(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    developer = db.Column(db.String(100))
    description = db.Column(db.Text)
    category = db.Column(db.String(50), nullable=False)
    features = db.Column(db.Text)
    pricing = db.Column(db.Text)
    api_access = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    tags = db.Column(db.String(200))  # Comma-separated tags
    notes = db.Column(db.Text)
    rating = db.Column(db.Float, default=0.0)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'developer': self.developer,
            'description': self.description,
            'category': self.category,
            'features': self.features,
            'pricing': self.pricing,
            'api_access': self.api_access,
            'tags': self.tags.split(',') if self.tags else [],
            'notes': self.notes,
            'rating': self.rating
        }
