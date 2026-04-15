"""
Run once to promote a user to admin.
Usage: python make_admin.py your@email.com
"""
import sys
from app import create_app
from extensions import db
from models import User

app = create_app()

with app.app_context():
    email = sys.argv[1] if len(sys.argv) > 1 else None
    if not email:
        # Default: promote the first user
        user = User.query.order_by(User.id).first()
    else:
        user = User.query.filter_by(email=email).first()

    if not user:
        print('User not found.')
    else:
        user.is_admin = True
        db.session.commit()
        print(f'✓ {user.name} ({user.email}) is now an admin.')
