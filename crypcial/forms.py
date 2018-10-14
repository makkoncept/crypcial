from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, IntegerField, FloatField, TextAreaField
from wtforms.fields.html5 import IntegerRangeField
# from wtforms.widgets import
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from crypcial.models import User
from flask_login import current_user


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    about = StringField('Tell Something about Yourself', validators=[DataRequired(),Length(min=5, max=150)])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')


class InvestForm(FlaskForm):
    wallet_money = StringField('Wallet')
    cryptocurrency = SelectField('Select the cryptocurrency', choices=[('btc', 'Bitcoin'), ('eth', 'Ethereum'), ('eos', 'EOS')]
                                 , validators=[DataRequired()])
    amount_to_invest = IntegerField('Amount to Invest', validators=[DataRequired()])
    submit = SubmitField('Update')

    def validate_amount_to_invest(self, amount_to_invest):
        if amount_to_invest.data > current_user.wallet_money:
            raise ValidationError("You don't have enough money in your wallet")


class RedeemForm(FlaskForm):
    wallet_money = StringField('Wallet')
    bitcoin = StringField('Bitcoin in wallet')
    ethereum = StringField('Ethereum in wallet')
    eos = StringField('EOS in wallet')
    cryptocurrency = SelectField('Select the cryptocurrency', choices=[('btc', 'Bitcoin'), ('eth', 'Ethereum'), ('eos', 'EOS')]
                                 , validators=[DataRequired()])
    coins_to_redeem = FloatField('Coins to Redeem', validators=[DataRequired()])
    submit = SubmitField('Update')

    def validate_coins_to_redeem(self, coins_to_redeem):
        if self.cryptocurrency.data == 'btc':
            if coins_to_redeem.data > current_user.btc:
                raise ValidationError("You don't have enough Bitcoins in your wallet")
        if self.cryptocurrency.data == 'eth':
            if coins_to_redeem.data > current_user.eth:
                raise ValidationError("You don't have enough Ethereum in your wallet")
        if self.cryptocurrency.data == 'eos':
            if coins_to_redeem.data > current_user.eos:
                raise ValidationError("You don't have enough EOS in your wallet")


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=5, max=100)])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')


class DiscussForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=5, max=100)])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')


class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Post')
