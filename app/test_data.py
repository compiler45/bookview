import os
import factory
from factory.alchemy import SQLAlchemyModelFactory
from flask import current_app

from .constants import TAG_NAMES
from .models import Book, Article, Tag, User, db


def generate_articles(number):
    class BookFactory(SQLAlchemyModelFactory):
        class Meta:
            model = Book
            sqlalchemy_session = db.session
            sqlalchemy_session_persistence = 'commit'

        title = factory.Faker('sentence')
        author = factory.Faker('name')
        year_published = factory.Faker('year')

    class ArticleFactory(SQLAlchemyModelFactory):
        class Meta:
            model = Article
            sqlalchemy_session = db.session
            sqlalchemy_session_persistence = 'commit'

        title = factory.SelfAttribute('book.title')
        time_published = factory.Faker('date_time_this_decade',
                                       before_now=True)
        book = factory.SubFactory(BookFactory)
        author = factory.Iterator(User.query.filter_by(
            email=current_app.config['ADMIN_EMAIL']).all())

        body_text = factory.Faker('text', max_nb_chars=1500)
        is_published = True

    ArticleFactory.create_batch(size=number)
    current_app.logger.debug("{} fake articles created.".format(number))
