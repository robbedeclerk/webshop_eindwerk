from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField,DecimalField,SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo,NumberRange
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
    bus_number = IntegerField('Bus Number', default='0')  

    submit = SubmitField('Register')
    
    def validate_password(self, password):
        if len(password.data) < 8:
            raise ValidationError('Password must be at least 8 characters long.')

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
    email = StringField('Email', validators=[DataRequired()], render_kw={'style': 'width: 400px'})
    country = StringField('Country', validators=[DataRequired()], render_kw={'style': 'width: 400px'})
    street = StringField('Street', validators=[DataRequired()], render_kw={'style': 'width: 400px'})
    postal_number = IntegerField('Postal Number', validators=[DataRequired()], render_kw={'style': 'width: 400px'})
    house_number = IntegerField('House Number', validators=[DataRequired()], render_kw={'style': 'width: 400px'})
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
    image = FileField('Product Image', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Submit')

class AddToCartForm(FlaskForm):
    quantity = IntegerField('Quantity', default=1, validators=[DataRequired(), NumberRange(min=1, message="Quantity must be at least 1")])
    submit = SubmitField('Add to Cart')


class ResetPasswordForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(), EqualTo('new_password', message='Passwords must match')
    ])
    submit = SubmitField('Reset Password')

    def validate_new_password(self, new_password):
        if len(new_password.data) < 8:
            raise ValidationError('New password must be at least 8 characters long.')