import pytest
import datetime
import time
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidSignatureError
from flask import url_for, current_app
from flask_login import current_user

from app.models import User


@pytest.fixture(scope='module')
def user_details():
    return {'username': 'nasuka',
            'email': 'peaceful@life.com',
            'password1': 'peace',
            'password2': 'peace'}


class UserViewUnitTest:

    def test_right_message_on_successful_submission_to_register_endpoint(
        app, client, user_details
    ):
        # TODO: make a decorator
        response = client.post('/register', data=user_details,
                               follow_redirects=True)
        assert response.status_code is 200
        assert "An email has been sent to your address" in response.get_data(as_text=True)


class UserCreationIntegrationTest:

    def test_user_exists_on_successful_submission_to_register_endpoint(
        app, client, user_details
    ):
        client.post('/register',
                    data=user_details,
                    follow_redirects=True)

        user = User.query.filter_by(username='nasuka').first()
        assert user is not None

    def test_user_is_not_confirmed_on_successful_submission_to_register_endpoint(
        app, client, user_details
    ):
        client.post('/register',
                    data=user_details,
                    follow_redirects=True)
        user = User.query.filter_by(username='nasuka').first()
        assert user.confirmed is False

    def test_verification_fails_after_submission_of_invalid_token_to_register_endpoint(
        app, client, user_details
    ):
        client.post('/register',
                    data=user_details,
                    follow_redirects=True)
        bad_token = 'bad token'
        user = User.query.filter_by(username='nasuka').first()
        verified = user.verify_confirmation_token(bad_token)
        assert verified is False

    def test_verification_succeeds_on_submission_of_valid_token_to_register_endpoint(
        app, client, user_details
    ):
        client.post('/register', data=user_details)

        user = User.query.filter_by(username='nasuka').first()
        token = user.generate_confirmation_token()

        assert user.confirmed is False
        client.post('/login', data={
            'username': user_details['username'],
            'password': user_details['password1']
        }, follow_redirects=True)
        client.get('/confirm?t={}'.format(token),
                   follow_redirects=True)
        assert user.confirmed is True

    def test_user_verification_fails_on_expired_confirmation(
        app, client, user_details
    ):
        client.post('/register', data=user_details)

        user = User.query.filter_by(username='nasuka').first()
        token = {'user_id': user.id,
                 'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=1)}
        time.sleep(2)
        assert user.verify_confirmation_token(token) is False

    # TODO: test user is forced to confirm before visiting non-confirmation pages
    @pytest.mark.skip
    def test_user_must_confirm_before_seeing_index(app, client, user_details):
        client.post('/register', data=user_details,
                                    follow_redirects=True)

        user = User.query.filter_by(username='nasuka').one()
        assert user.confirmed is False

        # login
        login_details = {'username': user_details['username'],
                         'password': user_details['password1']}
        response = client.post('/login', data=login_details, follow_redirects=True)

        # now try to go to index page
        response = client.get('/')
        assert user.confirmed is False
        assert user == current_user

        assert response.status_code == 302  # redirect
        redirect_url = response.headers['location']
        assert redirect_url == url_for('auth.confirm', _external=True)
