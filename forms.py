from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, FileField, SelectField, \
    IntegerField, RadioField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length, Required
from app.models import User, Category
from app import db


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
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class GoodsCreationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    image = FileField('Image', validators=[DataRequired()])
    category = SelectField('Category', validate_choice=False, choices=[])
    price = StringField('Price', validators=[DataRequired()])
    count = IntegerField('Count')
    description = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Create')

    def set_cat_choices(self):
        self.category.choices = [(c.id, c.category) for c in Category.query.all()]


def categories(columns=None):
    return Category.query


class CategoryCreationForm(FlaskForm):
    name = StringField('Category name', validators=[DataRequired()])
    parents = SelectField('Parents category', validate_choice=False, choices=[])
    description = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Create')

    def set_cat_choices(self):
        self.parents.choices = [(c.id, c.category) for c in Category.query.all()]


class AddToCartForm(FlaskForm):
    count = IntegerField('Count', default='1')
    submit = SubmitField('Add to cart')


class ChangeCategoryForm(FlaskForm):
    name = StringField('Category name', validators=[DataRequired()])
    parents = SelectField('Parents category', validate_choice=False, choices=[])
    description = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Save')

    def set_cat_choices(self):
        self.parents.choices = [(c.id, c.category) for c in Category.query.all()]


class ChangeItmForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    image = FileField('Image')
    category = SelectField('Category', validate_choice=False, choices=[])
    price = StringField('Price', validators=[DataRequired()])
    count = IntegerField('Count')
    description = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Create')

    def set_cat_choices(self):
        self.category.choices = [(c.id, c.category) for c in Category.query.all()]


class CheckoutForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    phone = IntegerField('Phone(without (+38))', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    payment = RadioField('Payment', choices=[('cc', 'Credit card(DONT WORK)'), ('ca', 'Cash, upon receipt')], default='ca')
    submit = SubmitField('Create')


class ConfirmForm(FlaskForm):
    submit = SubmitField('Confirm')