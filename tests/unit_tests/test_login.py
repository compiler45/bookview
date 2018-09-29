import pytest

from app.models import db, User


@pytest.fixture
def confirmed_user(app, database):
    user = User.query.filter_by(username='conductor').one()
    user.confirmed = True
    database.session.commit()

    return user


def attempt_login(client, username, password):
    # TODO make a decorator
    return client.post('/login', data={'username': username,
                                       'password': password},
                       follow_redirects=True)


class LoginPageViewIntegrationTest:

    def test_login_page_gives_correct_status_code(app, client):
        response = client.get('/', follow_redirects=True)
        assert response.status_code == 200

    def test_login_page_shows_right_message(app, client):
        response = client.get('/', follow_redirects=True)
        assert 'Welcome to Bookview' in response.get_data(as_text=True)

    def test_login_with_incorrect_details(app, client):
        response = attempt_login(client, 'tetsuro', '999')
        assert 'Invalid account details' in response.get_data(as_text=True)

    def test_correct_message_on_successful_login(
        app, client, confirmed_user
    ):
        response = attempt_login(client, 'conductor', 'nervousdreamer')

        assert 'Welcome, conductor' in response.get_data(as_text=True)

    def test_correct_message_on_logout(
        app, client, confirmed_user
    ):
        response = attempt_login(client, 'conductor', 'nervousdreamer')

        response = client.get('/logout')
        assert response.status_code == 200
        assert 'You have been logged out' in response.get_data(as_text=True)


