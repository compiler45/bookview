import pytest

from app.models import Role, User


class RolesUnitTest:

    def test_user_does_have_a_default_role(app, database):
        # one User role, one Administrator role
        users = Role.query.filter_by(name='User').all()
        assert users[0].is_default is True

    def test_admin_does_not_have_a_default_role(app, database):
        admins = Role.query.filter_by(name='Administrator').all()
        assert admins[0].is_default is False


class ModelsUnitTest:

    def test_password_attribute_cannot_be_accessed_from_user_model_directly(
        app, database
    ):
        user = User.query.filter_by(username='conductor').one()
        with pytest.raises(AttributeError):
            user.password

    def test_check_password_method_gives_true_for_correct_user_password(app):
        user = User.query.filter_by(username='conductor').one()
        assert user.check_password('spacenebula') is False
        assert user.check_password('nervousdreamer') is True
