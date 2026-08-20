import os
from models import db, User

def init_db(app):
    db.init_app(app)
    with app.app_context():
        # Ensure directories exist
        os.makedirs(app.config['MODEL_DIR'], exist_ok=True)
        os.makedirs(app.config['DATASET_DIR'], exist_ok=True)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        db.create_all()
        seed_default_admin()

def seed_default_admin():
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        default_admin = User(
            username='admin',
            email='admin@fakenewsdetector.com',
            is_admin=True
        )
        default_admin.set_password('Admin@123456')
        db.session.add(default_admin)
        db.session.commit()
        print("[Database] Default admin user initialized ('admin' / 'Admin@123456').")
