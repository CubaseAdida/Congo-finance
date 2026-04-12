from app import app, db
from models import User

with app.app_context():
    print(f"Total users: {User.query.count()}")
    for u in User.query.all():
        print(f"ID: {u.id}, Email: {u.email}, Admin: {u.is_admin}, Blocked: {u.is_blocked}, Balance: {u.balance}, Promo: {u.promo_code}")

