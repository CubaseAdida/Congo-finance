from app import app, db
from models import User

with app.app_context():
    admin = User.query.filter_by(email='admin@congofinance.com').first()
    if admin:
        admin.is_admin = True
        db.session.commit()
        print('Admin set pour admin@congofinance.com')
    else:
        print('Admin non trouvé')
    
    print('Admins:', User.query.filter_by(is_admin=True).count())

