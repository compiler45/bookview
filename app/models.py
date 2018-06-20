import datetime

import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidSignatureError, DecodeError
from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin

from . import db, bcrypt, login_manager
from .permissions import Permission


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    permissions = db.Column(db.Integer, default=0)
    is_default = db.Column(db.Boolean)

    users = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, name, **kwargs):
        super().__init__(**kwargs)
        self.name = name

    def has_permission(self, permission):
        return self.permissions & permission == permission

    def reset_permissions(self):
        self.permissions = 0

    def remove_permission(self, permission):
        if self.has_permission(permission):
            self.permissions -= permission

    def add_permission(self, permission):
        if not self.has_permission(permission):
            self.permissions += permission

    @staticmethod
    def insert_roles():
        roles_permissions = {'User': [Permission.VIEW_ARTICLE,
                                      Permission.SUBMIT_SUGGESTIONS],
                             'Administrator': [Permission.VIEW_ARTICLE,
                                               Permission.WRITE_ARTICLE,
                                               Permission.SUBMIT_SUGGESTIONS,
                                               Permission.ADMIN]}

        for role_name, permissions in roles_permissions.items():
            role = Role.query.filter_by(name=role_name).first()
            if not role:
                new_role = Role(name=role_name,
                                is_default=(role_name == 'User'))
                new_role.reset_permissions()
                for permission in permissions:
                    new_role.add_permission(permission)
                db.session.add(new_role)

        db.session.commit()

    def __repr__(self):
        return '<Role {}>'.format(self.name)


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True, index=True)
    email = db.Column(db.String, nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String, nullable=False)
    time_created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __init__(self, username, email, **kwargs):
        super().__init__(**kwargs)
        self.username = username
        self.email = email

        if email == current_app.config['ADMIN_EMAIL']:
            self.role = Role.query.filter_by(name='Administrator').first()
        else:
            self.role = Role.query.filter_by(is_default=True).first()

    @property
    def password(self):
        raise AttributeError("Passwords cannot be retrieved.")

    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, given_password):
        return bcrypt.check_password_hash(self.password_hash, given_password)

    def generate_confirmation_token(self, seconds=60 * 60 * 24):
        # generate token with a validity time of 1 day by default
        payload = {'user_id': self.id,
                   'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=seconds)
                  }

        return jwt.encode(payload, current_app.config['SECRET_KEY'],
                          algorithm='HS256').decode('utf-8')

    def verify_confirmation_token(self, token):
        try:
            payload = jwt.decode(token, current_app.config['SECRET_KEY'],
                                 algorithm='HS256')
            if payload.get('user_id') != self.id:
                return False
        except Exception:
            return False

        return True

    def __repr__(self):
        return 'User {}'.format(self.username)


# TODO: use session token instead
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
