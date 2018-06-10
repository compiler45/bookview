import pytest

from app import create_app
from app.models import db, Role, User


@pytest.fixture
def app():
    app = create_app('testing')
    app_ctx = app.app_context()
    app_ctx.push()

    db.create_all()
    Role.insert_roles()

    # add a user
    username = 'conductor'
    password = 'nervousdreamer'
    email = 'conductor@999.com'

    user = User(username=username, email=email, password=password)
    db.session.add(user)
    db.session.commit()

    yield app

    db.session.remove()
    db.drop_all()
    app_ctx.pop()
