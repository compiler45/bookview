def attempt_login(client, username, password):
    return client.post('/login', data={'username': username,
                                       'password': password},
                       follow_redirects=True)


def test_incorrect_login(app):
    test_client = app.test_client(use_cookies=True)

    response = test_client.get('/', follow_redirects=True)
    # should redirect to login page

    assert response.status_code == 200
    assert 'Welcome to Bookview' in response.get_data(as_text=True)
    response = attempt_login(test_client, 'tetsuro', '999')

    assert 'Invalid account details' in response.get_data(as_text=True)


def test_correct_login_and_logout(app):
    test_client = app.test_client(use_cookies=True)

    response = attempt_login(test_client, 'conductor', 'nervousdreamer')
    assert 'Welcome, conductor' in response.get_data(as_text=True)

    response = test_client.get('/logout')
    assert response.status_code == 200
    assert 'You have been logged out' in response.get_data(as_text=True)


