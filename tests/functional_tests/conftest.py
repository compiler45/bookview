import random
import pytest

from selenium import webdriver

from app.models import User
from app.test_data import generate_articles


@pytest.fixture
def browser():
    browser = webdriver.Chrome()

    yield browser
    browser.quit()


@pytest.fixture(autouse=True)
def db_setup(database, admin_user):
    user = User(username='maetel', password='mystery', email='sad@woman.com',
                confirmed=True)
    database.session.add(user)
    database.session.commit()

    # always need an admin user to make new articles!
    num_articles = random.randint(20, 40)
    generate_articles(number=num_articles)
