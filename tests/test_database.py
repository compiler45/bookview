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


def test_roles(app):
    with app.test_request_context():
        # one User role, one Administrator role
        users = Role.query.filter_by(name='User').all()
        admins = Role.query.filter_by(name='Administrator').all()

        assert len(users) == 1
        assert len(admins) == 1

        assert users[0].is_default is True and admins[0].is_default is False


def test_password(app):
    with app.test_request_context():
        user = User.query.first()
        with pytest.raises(AttributeError):
            password = user.password

        assert user.check_password('spacenebula') is False
        assert user.check_password('nervousdreamer') is True
