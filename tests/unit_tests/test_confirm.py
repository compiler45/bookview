import pytest
import datetime
import time

from app.models import User


@pytest.fixture(scope='module')
def user_details():
    return {'username': 'nasuka',
            'email': 'peaceful@life.com',
            'password1': 'peace',
            'password2': 'peace'}


@pytest.mark.usefixtures('client_class')
class UserViewUnitTest:

    def test_right_message_on_successful_submission_to_register_endpoint(
        self, user_details
    ):
        # TODO: make a decorator
        response = self.client.post('/register', data=user_details,
                               follow_redirects=True)
        assert response.status_code is 200
        assert "An email has been sent to your supplied address" in response.get_data(as_text=True)


@pytest.mark.usefixtures('client_class')
class UserCreationIntegrationTest:

    def test_user_exists_on_successful_submission_to_register_endpoint(
        self, user_details
    ):
        self.client.post('/register',
                    data=user_details,
                    follow_redirects=True)

        user = User.query.filter_by(username='nasuka').first()
        assert user is not None

    def test_user_is_not_confirmed_on_successful_submission_to_register_endpoint(
        self, user_details
    ):
        self.client.post('/register',
                    data=user_details,
                    follow_redirects=True)
        user = User.query.filter_by(username='nasuka').first()
        assert user.confirmed is False

    def test_verification_fails_after_submission_of_invalid_token_to_register_endpoint(
        self, user_details
    ):
        self.client.post('/register',
                    data=user_details,
                    follow_redirects=True)
        bad_token = 'bad token'
        user = User.query.filter_by(username='nasuka').first()
        verified = user.verify_confirmation_token(bad_token)
        assert verified is False

    def test_verification_succeeds_on_submission_of_valid_token_to_register_endpoint(
        self, user_details
    ):
        self.client.post('/register', data=user_details)

        user = User.query.filter_by(username='nasuka').first()
        token = user.generate_confirmation_token()

        assert user.confirmed is False
        self.client.post('/login', data={
            'username': user_details['username'],
            'password': user_details['password1']
        }, follow_redirects=True)
        self.client.get('/confirm?t={}'.format(token),
                   follow_redirects=True)
        assert user.confirmed is True

    def test_user_verification_fails_on_expired_confirmation(
        self, user_details
    ):
        self.client.post('/register', data=user_details)

        user = User.query.filter_by(username='nasuka').first()
        token = {'user_id': user.id,
                 'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=1)}
        time.sleep(2)
        assert user.verify_confirmation_token(token) is False

