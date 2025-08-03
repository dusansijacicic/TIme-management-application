from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models import User, Company

class LoginForm(FlaskForm):
    username = StringField('Korisničko ime', validators=[DataRequired()])
    password = PasswordField('Lozinka', validators=[DataRequired()])
    remember_me = BooleanField('Zapamti me')
    submit = SubmitField('Uloguj se')

class RegistrationForm(FlaskForm):
    username = StringField('Korisničko ime', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('Ime', validators=[DataRequired(), Length(max=64)])
    last_name = StringField('Prezime', validators=[DataRequired(), Length(max=64)])
    password = PasswordField('Lozinka', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Potvrdi lozinku', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Uloga', choices=[
        ('user', 'Korisnik'),
        ('company_admin', 'Admin kompanije')
    ])
    submit = SubmitField('Registruj se')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Ovo korisničko ime je već zauzeto.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Ovaj email je već registrovan.') 