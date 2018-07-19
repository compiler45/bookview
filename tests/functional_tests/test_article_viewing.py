""" FT for a user who visits the site when it has at least twenty articles, clicks
an article on page 1, goes back, and views page 2"""

import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from flask import current_app, url_for

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
    generate_articles(number=25)


@pytest.mark.usefixtures("live_server")
class TestUserBrowsesIndexPage(object):

    def test_user_visits_page_one_and_page_two(self, browser):

        # Maetel is interested in learning about some new books to read
        # on the 999. She hears of Bookview, and decides to visit 
        server_url = url_for('main.index', _external=True)

        browser.get(server_url)

        greeting = browser.find_element_by_class_name('greeting')
        assert 'Welcome to Bookview' in greeting.text

        # She logs in
        username_input = browser.find_element_by_id('username')
        username_input.send_keys('maetel')
        password_input = browser.find_element_by_id('password')
        password_input.send_keys('mystery')
        password_input.submit()

        time.sleep(1)

        assert browser.current_url == server_url

        greeting = browser.find_element_by_class_name('greeting')
        assert greeting.text == 'Welcome, maetel!'

        # Happy, she sees that there are (at least) two pages of articles
        # to view. Pager looks like so: << | 1 | 2 | ... | >>

        pagination_links = browser.find_elements_by_class_name('pagination-link')
        assert len(pagination_links) >= 4

        # She sees a count of the number of articles in the entire site
        article_count = browser.find_element_by_class_name('article-count')
        assert int(article_count.text) >= 20

        # She also notices there is a max of 10 articles on each page
        article_links = browser.find_elements_by_class_name('article-link')
        assert len(article_links) == current_app.config['MAX_ARTICLES_PER_PAGE']

        # She decides to choose the first one and spend some time reading it
        article_links[0].click()
        time.sleep(1)

        # She then goes back and clicks looks at page 2
        # which should have 10 articles on it
        browser.back()
        link_to_page_two = browser.find_elements_by_class_name('pagination-link')[2]
        link_to_page_two.click()

        article_links = browser.find_elements_by_class_name('article-link')
        assert len(article_links) == current_app.config['MAX_ARTICLES_PER_PAGE']

        # After she's done browsing a bit, she sleeps as the stars drift by
        # outside
