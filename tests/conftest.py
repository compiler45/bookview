import os
import pytest

from app import create_app
from app.models import db, Role, User, Tag
from app.decorators import attach_request_hooks


@pytest.fixture
def app():
    app = create_app('testing')
    attach_request_hooks(app)
    with app.app_context():
        yield app


@pytest.fixture
def database():
    return db

@pytest.fixture(autouse=True)
def handle_database(request, app, database):
    database.create_all()
    Role.insert_roles()
    Tag.insert_tags()

    yield

    database.session.remove()
    database.drop_all()


@pytest.fixture(autouse=True)
def user(database):
    user = User(username='conductor', password='nervousdreamer',
                email='conductor@999.com')
    database.session.add(user)
    database.session.commit()


@pytest.fixture
def admin_user(database, app):
    email = app.config['ADMIN_EMAIL']
    password = app.config['ADMIN_PASSWORD']
    user = User(username='admin', password=password,
                email=email, confirmed=True)
    database.session.add(user)
    database.session.commit()
