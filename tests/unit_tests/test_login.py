import pytest

from app.models import db, User


@pytest.fixture
def confirmed_user(app, database):
    user = User.query.filter_by(username='conductor').one()
    user.confirmed = True
    database.session.commit()

    return user


@pytest.mark.usefixtures('client_class')
class LoginPageViewIntegrationTest:

    def attempt_login(self, username, password):
        # TODO make a decorator
        return self.client.post('/login', data={'username': username,
                                           'password': password},
                           follow_redirects=True)

    def test_login_page_gives_correct_status_code(self, app):
        response = self.client.get('/', follow_redirects=True)
        assert response.status_code == 200

    def test_login_page_shows_right_message(self, app):
        response = self.client.get('/', follow_redirects=True)
        assert 'Welcome to Bookview' in response.get_data(as_text=True)

    def test_login_with_incorrect_details(self, app):
        response = self.attempt_login('tetsuro', '999')
        assert 'Invalid account details' in response.get_data(as_text=True)

    def test_correct_message_on_successful_login(
        self, app, confirmed_user
    ):
        response = self.attempt_login('conductor', 'nervousdreamer')

        assert 'Welcome, conductor' in response.get_data(as_text=True)

    def test_correct_message_on_logout(
        self, app, confirmed_user
    ):
        response = self.attempt_login('conductor', 'nervousdreamer')

        response = self.client.get('/logout')
        assert response.status_code == 200
        assert 'You have been logged out' in response.get_data(as_text=True)


