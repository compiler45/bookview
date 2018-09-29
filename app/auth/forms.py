from flask_wtf import FlaskForm
from wtforms.fields import StringField, BooleanField, SubmitField, \
    PasswordField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp, \
    ValidationError


from ..models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(),
                                                   Length(1, 30)])
    # TODO: implement password checking
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me?')
    submit = SubmitField('Login')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(),
                                                   Regexp('^[a-zA-Z][a-zA-Z0-9_]*',
                                                          0,
'''Please ensure that
                                                          your username begins
                                                          with a letter,
                                                          followed by letters,
                                                          numbers and
                                                          underscores.'''),
                                                   Length(1, 30)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password1 = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Confirm your password',
                              validators=[DataRequired(), EqualTo('password1', 
                                                                  message='''Please
                                                                  ensure both
                                                                  passwords
                                                                  match.''')])
    submit = SubmitField('Submit')
    # receive updates?

    def validate_username(self, field):
        username = field.data
        user = User.query.filter_by(username=username).first()
        if user:
            raise ValidationError('Sorry, this username is already taken.')

    def validate_email(self, field):
        email = field.data
        user = User.query.filter_by(email=email).first()
        if user:
            raise ValidationError('There is already an account with this email')


