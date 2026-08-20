import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'fake-news-detector-super-secret-key-2026'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f"sqlite:///{os.path.join(BASE_DIR, 'fake_news.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Paths
    MODEL_DIR = os.path.join(BASE_DIR, 'model')
    DATASET_DIR = os.path.join(BASE_DIR, 'dataset')
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    
    MODEL_PATH = os.path.join(MODEL_DIR, 'model.pkl')
    VECTORIZER_PATH = os.path.join(MODEL_DIR, 'vectorizer.pkl')
    
    # Security & Form config
    WTF_CSRF_ENABLED = True
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
