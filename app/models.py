from cached_property import cached_property
import datetime

import bleach
import jwt
from markdown import markdown
from flask import current_app, url_for
from flask_login import UserMixin, AnonymousUserMixin

from . import db, bcrypt, login_manager
from .permissions import Permission


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    permissions = db.Column(db.Integer, default=0)
    is_default = db.Column(db.Boolean)

    users = db.relationship('User', backref='role')

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


articles_tags = db.Table('articles_tags',
                         db.Column('tags_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True),
                         db.Column('articles_id', db.Integer, db.ForeignKey('articles.id'),
                                   primary_key=True))


class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, unique=True, nullable=False)
    author = db.Column(db.String, nullable=False)
    year_published = db.Column(db.String, nullable=True)


class UploadedImage(db.Model):
    __tablename__ = 'uploaded_images'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String, nullable=False, unique=True)
    path = db.Column(db.String, nullable=False, unique=True)

    @property
    def static_path(self):
        return url_for('static',
                       filename='img/uploads/{}'.format(self.filename))


class Article(db.Model):
    __tablename__ = 'articles'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False, unique=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    time_published = db.Column(db.DateTime, nullable=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    image_id = db.Column(db.Integer, db.ForeignKey('uploaded_images.id'),
                         nullable=True)
    body_text = db.Column(db.Text)
    body_html = db.Column(db.Text)
    is_published = db.Column(db.Boolean, default=False, nullable=False)

    book = db.relationship('Book', backref=db.backref('article'),
                           uselist=False)
    image = db.relationship('UploadedImage', lazy='select')
    author = db.relationship('User', backref=db.backref('articles',
                                                        lazy='dynamic'))
    tags = db.relationship('Tag', secondary=articles_tags,
                           backref=db.backref('articles', lazy='dynamic'))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @cached_property
    def hyphenated_title(self):
        lowercase_title = self.title.lower()

        punctuation = ['?', '!', ',', '"', '#', ')', '(', '$', '%', '^', '-',
                       '+', '*', '.']
        for symbol in punctuation:
            lowercase_title = lowercase_title.replace(symbol, '')

        return lowercase_title.replace(' ', '-')

    @cached_property
    def text_preview(self):
        """ Return first 10 words of an article"""
        num_spaces = 0
        preview = ""
        for char in self.body_text:
            if char == " ":
                num_spaces += 1

            if num_spaces == 10:
                break
            else:
                preview += char

        return preview

    @staticmethod
    def on_changed_body(target, value, old_value, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul', 'h1',
                        'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))


class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @staticmethod
    def insert_tags():
        logger = current_app.logger
        tag_names = ['Action', 'Graphic Novel', 'Philosophy', 'Classical '
                     'Literature', 'Modern Literature', 'History', 'Political '
                     'Philosophy', 'Science', 'Existentialism', 'Social '
                     'Commentary', 'Travel', 'Science Fiction', 'Fantasy', 
                     'Japanese Literature']
        for name in tag_names:
            tag = Tag.query.filter_by(name=name).one_or_none()
            if not tag:
                logger.info('Adding new book tag: {}'.format(name))
                tag = Tag(name=name)
                db.session.add(tag)

        db.session.commit()


# database events, such as updating an article's text
db.event.listen(Article.body_text, 'set', Article.on_changed_body)
