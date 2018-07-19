import pytest
import random
from lxml import html
from flask import current_app

from app.models import Article, User
from app.test_data import generate_articles




def test_correct_number_of_pagination_links_shown_on_index_page(app, client,
                                                                database,
                                                                admin_user):
    # add some fake articles
    num_fake_articles = random.choice(range(1, 20))
    generate_articles(number=num_fake_articles)
    print(num_fake_articles)
    num_published_articles = Article.query.filter_by(is_published=True).count()
    assert num_published_articles == num_fake_articles

    # login with a confirmed user
    user = User.query.filter_by(username='conductor').one()
    user.confirmed = True
    database.session.commit()
    index_page = client.post('/login', data={'username': 'conductor',
                                             'password': 'nervousdreamer',
                                             'email': 'conductor@999.com'},
                             follow_redirects=True)

    index_page_text = index_page.get_data(as_text=True)
    html_tree = html.document_fromstring(index_page_text)
    pagination_links = html_tree.find_class('pagination-link')

    max_articles_per_page = current_app.config['MAX_ARTICLES_PER_PAGE']
    quotient, remainder = divmod(num_published_articles, max_articles_per_page)
    correct_num_of_links = quotient + 2 + (1 if remainder else 0)
    assert len(pagination_links) == correct_num_of_links
