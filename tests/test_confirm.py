import pytest
import datetime
import time
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidSignatureError

from app.models import User


@pytest.fixture(scope='module')
def user_details():
    return {'username': 'nasuka',
             'email': 'peaceful@life.com',
             'password1': 'peace',
             'password2': 'peace'}


def test_incorrect_confirmation_token(app, user_details):
    test_client = app.test_client(use_cookies=True)
    response = test_client.post('/register', data=user_details,
                                follow_redirects=True)
    assert response.status_code is 200
    assert "An email has been sent to your address" in response.get_data(as_text=True)

    user = User.query.filter_by(username='nasuka').first()
    assert user is not None
    assert user.confirmed is False

    bad_token  = 'bad token'
    verified = user.verify_confirmation_token(bad_token)
    assert verified is False

    # login, then confirm
    test_client.post('/login', data={'username': 'nasuka', 'password': 'peace'})
    response = test_client.get('/confirm?t={}'.format(bad_token),
                               follow_redirects=True)
    assert 'Token is invalid or expired' in response.get_data(as_text=True)
    assert user.confirmed is False


def test_correct_confirmation_token(app, user_details):
    test_client = app.test_client(use_cookies=True)
    response = test_client.post('/register', data=user_details)

    user = User.query.filter_by(username='nasuka').first()

    token = user.generate_confirmation_token()
    verified = user.verify_confirmation_token(token)
    assert verified is True

    test_client.post('/login', data={'username': 'nasuka', 'password': 'peace'})
    assert user.is_authenticated
    response = test_client.get('/confirm?t={}'.format(token),
                               follow_redirects=True)
    assert user.confirmed is True

def test_expired_confirmation(app, user_details):
    test_client = app.test_client(use_cookies=True)
    response = test_client.post('/register', data=user_details)

    user = User.query.filter_by(username='nasuka').first()
    token = {'user_id': user.id,
             'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=1)}
    time.sleep(2)
    assert user.verify_confirmation_token(token) is False


#TODO: test user is forced to confirm before visiting non-confirmation pages
