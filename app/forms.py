from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField,DecimalField,SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from wtforms.fields import DecimalField
import sqlalchemy as sa
from app import db
from app.models import User
from flask_login import current_user

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    country = StringField('Country', validators=[DataRequired()])
    street = StringField('Street', validators=[DataRequired()])
    postal_number = IntegerField('Postal Number', validators=[DataRequired()])
    house_number = IntegerField('House Number', validators=[DataRequired()])
    bus_number = IntegerField('Bus Number')  # No validation required for bus number

    submit = SubmitField('Register')

    def validate_username(self, username):
        user = db.session.scalar(sa.select(User).where(
            User.username == username.data))
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(
            User.email == email.data))
        if user is not None:
            raise ValidationError('Please use a different email address.')

class EditProfileForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired()], render_kw={'style': 'width: 400px'})
    country = StringField('Country',validators=[DataRequired()], render_kw={'style': 'width: 400px'})
    street = StringField('Street',validators=[DataRequired()], render_kw={'style': 'width: 400px'})
    postal_number = IntegerField('Postal Number',validators=[DataRequired()], render_kw={'style': 'width: 400px'})
    house_number = IntegerField('House Number',validators=[DataRequired()], render_kw={'style': 'width: 400px'})
    bus_number = IntegerField('Bus Number', render_kw={'style': 'width: 400px'})
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)


    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None and user != current_user:
            raise ValidationError('Please use a different email address.')

class AddCategoryForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Submit')

class AddProductForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    price = DecimalField('Price', validators=[DataRequired()])
    category = SelectField('Category', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Submit')