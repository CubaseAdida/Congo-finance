from flask import Flask, render_template, redirect, url_for, flash, request, abort, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from models import db, User, Notification
from forms_fixed import RegisterForm, LoginForm, DepositForm, WithdrawForm, MessageForm
from dotenv import load_dotenv
import os
import string
import random
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from functools import wraps
import pathlib

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-change-me')
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'users.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['WTF_CSRF_ENABLED'] = True

# Extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
csrf = CSRFProtect(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        if not current_user.is_admin:
            flash('Accès administrateur requis.', 'danger')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def transfer_referral_bonus(user, action=None):
    \"\"\"Transfer 500 FCFA referral bonus from pending to balance when unblocking.\"\"\"
    if user.referrer_promo_code:
        referrer = User.query.filter_by(promo_code=user.referrer_promo_code).first()
        if referrer and referrer.pending_promo_bonus >= 500:
            referrer.balance += 500
            referrer.pending_promo_bonus -= 500
            db.session.add(referrer)
            msg = f'Bonus promo 500 FCFA transféré au referrer !'
            if action:
                flash(f'Compte {action}. {msg}', 'success')
            else:
                flash(f'Utilisateur mis à jour. {msg}', 'success')
        else:
            msg = f'Utilisateur mis à jour.' if not action else f'Compte {action}.'
            flash(msg, 'success')
    else:
        msg = f'Utilisateur mis à jour.' if not action else f'Compte {action}.'
        flash(msg, 'success')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    return render_template('services.html')
