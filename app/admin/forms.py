from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, SelectField, SubmitField, DecimalField, PasswordField, SelectMultipleField
from wtforms.validators import DataRequired, Length, Optional, EqualTo, Email
from app.models import Company, User, Project

class CompanyForm(FlaskForm):
    name = StringField('Naziv kompanije', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[Optional(), Email()])
    phone = StringField('Telefon', validators=[Optional()])
    website = StringField('Website', validators=[Optional()])
    address = TextAreaField('Adresa', validators=[Optional()])
    description = TextAreaField('Opis')
    submit = SubmitField('Sačuvaj')

class ProjectForm(FlaskForm):
    name = StringField('Naziv projekta', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Opis')
    company_id = SelectField('Kompanija', coerce=int, validators=[DataRequired()])
    start_date = DateField('Datum početka', validators=[DataRequired()])
    end_date = DateField('Datum završetka', validators=[Optional()])
    budget = DecimalField('Budžet', validators=[Optional()])
    status = SelectField('Status', choices=[
        ('active', 'Aktivan'),
        ('completed', 'Završen'),
        ('on_hold', 'Na čekanju')
    ])
    submit = SubmitField('Sačuvaj')

class UserForm(FlaskForm):
    username = StringField('Korisničko ime', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('Ime', validators=[DataRequired(), Length(max=64)])
    last_name = StringField('Prezime', validators=[DataRequired(), Length(max=64)])
    role = SelectField('Uloga', choices=[
        ('user', 'Korisnik'),
        ('company_admin', 'Admin kompanije'),
        ('super_admin', 'Super Admin')
    ])
    hourly_rate = DecimalField('Satnica', validators=[Optional()])
    projects = SelectMultipleField('Projekti', coerce=int, validators=[Optional()], default=[])
    password = PasswordField('Lozinka', validators=[Optional()])
    confirm_password = PasswordField('Potvrdi lozinku', validators=[Optional(), EqualTo('password', message='Lozinke se ne poklapaju')])
    submit = SubmitField('Sačuvaj')

class ProjectUserForm(FlaskForm):
    user_id = SelectField('Korisnik', coerce=int, validators=[DataRequired()])
    role = SelectField('Uloga na projektu', choices=[
        ('user', 'Korisnik'),
        ('project_admin', 'Admin projekta')
    ])
    submit = SubmitField('Dodeli korisnika') 