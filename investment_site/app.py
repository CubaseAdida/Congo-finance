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
    """Transfer 500 FCFA referral bonus from pending to balance when unblocking."""
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

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email déjà utilisé', 'danger')
            return render_template('register.html', form=form)
        
        promo_code = None
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            existing = User.query.filter_by(promo_code=code).first()
            if not existing:
                promo_code = code
                break
        
        user = User(email=form.email.data)
        user.country = form.country.data
        user.currency = form.currency.data
        user.promo_code = promo_code
        user.set_password(form.password.data)
        user.is_blocked = True
        db.session.add(user)
        
        referrer = None
        if form.promo_code.data:
            referrer_promo = form.promo_code.data.upper()
            referrer = User.query.filter_by(promo_code=referrer_promo).first()
            if referrer:
                referrer.pending_promo_bonus += 500.0
                db.session.add(referrer)
            user.referrer_promo_code = referrer_promo if referrer else None
        
        db.session.commit()
        flash(f'Compte créé ! Votre code promo : {user.promo_code}. Connectez-vous.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin'))
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            if user.is_blocked:
                flash('Votre compte a été bloqué par l\'administrateur.', 'danger')
                return render_template('login.html', form=form)
            login_user(user)
            calculate_interest(user)
            if user.is_admin:
                return redirect(url_for('admin'))
            return redirect(url_for('dashboard'))
        flash('Email ou mot de passe incorrect', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Déconnecté avec succès', 'success')
    return redirect(url_for('home'))

def calculate_interest(user):
    # Interest calculation disabled
    return 0

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = WithdrawForm()
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    # calculate_interest(current_user)  # Disabled
    days_elapsed = (datetime.utcnow() - current_user.created_at).days
    remaining_days = max(0, 15 - days_elapsed)
    daily_gain = current_user.balance * current_user.custom_rate
    projected_next = current_user.balance + daily_gain
    
    if form.validate_on_submit():
        amount = form.amount.data
        if amount > current_user.balance:
            flash('Solde insuffisant.', 'danger')
        else:
            method = 'retrait'  # Default, since no payment method for withdrawal
            message = f"je veux retirer {amount:.0f} FCFA - Email: {current_user.email}"
            whatsapp_url = f"https://wa.me/242050542421?text={message.replace(' ', '%20')}"
            flash(f'✅ Confirmez votre retrait de {amount:.0f} FCFA sur WhatsApp: <a href=\"{whatsapp_url}\" target=\"_blank\" class=\"alert-link\">Cliquez ici</a>', 'success')
            return redirect(url_for('dashboard'))
    
    return render_template('dashboard.html', user=current_user, promo_code=current_user.promo_code, promo_bonus_balance=current_user.promo_bonus_balance, promo_uses=current_user.promo_uses, form=form, days_elapsed=days_elapsed, remaining_days=remaining_days, projected_next=projected_next, daily_gain=daily_gain, notifications=notifications, unread_count=unread_count)

@app.route('/deposit', methods=['GET', 'POST'])
@login_required
def deposit():
    form = DepositForm()
    if form.validate_on_submit():
        if current_user.budget_limit and current_user.balance + form.amount.data > current_user.budget_limit:
            flash('Dépôt dépasserait votre limite budgétaire.', 'danger')
            return render_template('deposit.html', form=form)
        method = form.payment_method.data
        amount = form.amount.data
        message = f"je veux deposer {amount:.0f} FCFA via {method.upper()} - Email: {current_user.email}"
        whatsapp_url = f"https://wa.me/242050542421?text={message.replace(' ', '%20')}"
        flash(f'✅ Confirmez votre dépôt de {amount:.0f} FCFA via {method.upper()} sur WhatsApp: <a href=\"{whatsapp_url}\" target=\"_blank\" class=\"alert-link\">Cliquez ici</a>', 'success')
        return redirect(url_for('dashboard'))
    return render_template('deposit.html', form=form)

# Admin Routes
@app.route('/admin', methods=['GET', 'POST'])
@login_required
@admin_required
def admin():
    form = MessageForm()
    users = User.query.all()
    total_users = len(users)
    from datetime import datetime
    users_with_days = []
    for user in users:
        days_elapsed = (datetime.utcnow() - user.created_at).days
        remaining_days = max(0, 15 - days_elapsed)
        users_with_days.append((remaining_days, user))
    users_with_days.sort(key=lambda x: x[0])  # Sort by remaining days
    if form.validate_on_submit():
        if form.send_all.data:
            # Send to all users
            for user in users:
                notif = Notification(user_id=user.id, message=form.message.data)
                db.session.add(notif)
            db.session.commit()
            flash(f'Message envoyé à {total_users} utilisateurs !', 'success')
        elif form.target_user_id.data:
            target_user = User.query.get(form.target_user_id.data)
            if target_user:
                notif = Notification(user_id=target_user.id, message=form.message.data)
                db.session.add(notif)
                db.session.commit()
                flash(f'Message envoyé à {target_user.email} !', 'success')
            else:
                flash('Utilisateur non trouvé.', 'danger')
        else:
            flash('Sélectionnez "Tous" ou un ID utilisateur.', 'danger')
        return redirect(url_for('admin'))
    return render_template('admin.html', users_with_days=users_with_days, users=users, total_users=total_users, message_form=form)

@app.route('/admin/users/<int:user_id>/update', methods=['POST'])
@admin_required
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.form.get('balance'):
        user.balance = float(request.form['balance'])
    if 'blocked' in request.form:
        was_blocked = user.is_blocked
        user.is_blocked = True if request.form['blocked'] == 'on' else False
        if was_blocked and not user.is_blocked:
            transfer_referral_bonus(user)
    if request.form.get('rate'):
        user.custom_rate = float(request.form['rate'])
    budget_str = request.form.get('budget_limit', '')
    user.budget_limit = float(budget_str) if budget_str else None
    db.session.commit()
    flash('Utilisateur mis à jour.', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/users/<int:user_id>/block', methods=['POST'])
@admin_required
def block_user(user_id):
    user = User.query.get_or_404(user_id)
    was_blocked = user.is_blocked
    user.is_blocked = not user.is_blocked
    action = 'bloqué' if user.is_blocked else 'débloqué'
    
    if was_blocked and not user.is_blocked:
        transfer_referral_bonus(user, action)
    db.session.commit()
    return redirect(url_for('admin'))

@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    email = user.email
    db.session.delete(user)
    db.session.commit()
    flash(f'{email} supprimé.', 'success')
    return redirect(url_for('admin'))

# Create first admin and migrate tables
with app.app_context():
    db.create_all()
    if not User.query.filter_by(is_admin=True).first():
        admin_user = User(email='admin@congofinance.com')
        admin_user.promo_code = 'ADMIN001'
        admin_user.set_password('admin2024')
        admin_user.is_admin = True
        db.session.add(admin_user)
        db.session.commit()
        print("Admin créé: admin@congofinance.com / admin2024")

@app.route('/notifications/<int:notif_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notif_id):
    notif = Notification.query.get_or_404(notif_id)
    if notif.user_id == current_user.id:
        notif.is_read = True
        db.session.commit()
        flash('Notification marquée comme lue.', 'success')
    return redirect(url_for('dashboard'))

print("App ready - DB:", db_path)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
