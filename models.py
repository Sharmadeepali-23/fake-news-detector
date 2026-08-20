from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

def get_utc_now():
    return datetime.now(timezone.utc)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=get_utc_now)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class PredictionHistory(db.Model):
    __tablename__ = 'prediction_history'
    
    id = db.Column(db.Integer, primary_key=True)
    news_title = db.Column(db.String(255), nullable=True, default='Untitled Article')
    news_content = db.Column(db.Text, nullable=False)
    prediction = db.Column(db.String(20), nullable=False)  # 'REAL NEWS' or 'FAKE NEWS'
    confidence = db.Column(db.Float, nullable=False)       # Percentage e.g. 97.8
    model_used = db.Column(db.String(64), default='Best ML Model')
    word_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=get_utc_now, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'news_title': self.news_title,
            'news_content': self.news_content[:150] + ('...' if len(self.news_content) > 150 else ''),
            'prediction': self.prediction,
            'confidence': self.confidence,
            'model_used': self.model_used,
            'word_count': self.word_count,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

    def __repr__(self):
        return f'<PredictionHistory {self.id} - {self.prediction} ({self.confidence}%)>'
