import pytest

from app.models import Role, User


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
