from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, SelectField, TextAreaField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mot de passe', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmer mot de passe', validators=[DataRequired(), EqualTo('password')])
    country = SelectField('Pays', choices=[
        ('AO', 'Angola'),
        ('BI', 'Burundi'),
        ('CM', 'Cameroun'), 
        ('CF', 'République Centrafricaine'),
        ('TD', 'Tchad'),
        ('CG', 'Congo'),
        ('CD', 'RDC'),
        ('GQ', 'Guinée équatoriale'),
        ('GA', 'Gabon'),
        ('RW', 'Rwanda'),
        ('ST', 'Sao Tomé-et-Principe')
    ], validators=[DataRequired()])
    currency = SelectField('Monnaie', choices=[('CDF', 'Franc Congolais (CDF)'), ('USD', 'Dollar US (USD)'), ('XAF', 'Franc CFA (XAF)'), ('EUR', 'Euro (EUR)')], validators=[DataRequired()])
    promo_code = StringField('Code promo (optionnel)')
    submit = SubmitField("S'inscrire")

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    submit = SubmitField('Se connecter')

class DepositForm(FlaskForm):
    amount = FloatField('Montant à déposer (FCFA)', validators=[DataRequired()])
    payment_method = SelectField('Moyen de paiement', choices=[
        ('visa', 'Visa'),
        ('mastercard', 'Mastercard'),
        ('momo', 'MTN MoMo'),
        ('airtel', 'Airtel Money')
    ], validators=[DataRequired()])
    submit = SubmitField('Confirmer le paiement')

class WithdrawForm(FlaskForm):
    amount = FloatField('Montant à retirer (FCFA)', validators=[DataRequired()])
    submit = SubmitField('Retirer')

class MessageForm(FlaskForm):
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=5, max=1000)])
    target_user_id = IntegerField('ID Utilisateur (optionnel pour individuel)', validators=[Optional()])
    send_all = BooleanField('Envoyer à tous les utilisateurs')
    submit = SubmitField('Envoyer le message')
