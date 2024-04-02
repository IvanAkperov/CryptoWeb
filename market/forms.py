from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, ValidationError, IntegerField
from wtforms.validators import Length, EqualTo, Email, DataRequired
from market.models import User


class RegisterForm(FlaskForm):

    def validate_username(self, name):
        user = User.query.filter_by(username=name.data).first()
        if user:
            raise ValidationError(f"Username {user.username} exists. Try different one!")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError(f"Email {user.email} exists. Try different one!")

    username = StringField(label="username", validators=[Length(min=4, max=30), DataRequired()])
    email = StringField(label="email", validators=[Email(), DataRequired()])
    password = PasswordField(label="password", validators=[Length(min=6), DataRequired()])
    password_repeat = PasswordField(label="password-repeat", validators=[EqualTo("password"), DataRequired()])
    submit = SubmitField(label="submit")


class LoginForm(FlaskForm):
    username = StringField(label="username", validators=[Length(min=4, max=30), DataRequired()])
    password = PasswordField(label="password", validators=[Length(min=6), DataRequired()])
    submit = SubmitField(label="sign in")


class PurchaseItemForm(FlaskForm):
    currency_id = IntegerField('Currency ID', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    submit = SubmitField(label="Purchase")


class SellItemForm(FlaskForm):
    currency_id = IntegerField('Currency ID', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    submit = SubmitField(label='sell')
