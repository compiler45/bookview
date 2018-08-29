import os
import datetime

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from flask import redirect, url_for, render_template, flash, current_app, \
        abort, request
from flask_login import login_required, current_user

from . import main
from .forms import WriteArticleForm
from app.models import Article, Tag, Book, UploadedImage, User
from app.permissions import Permission
from app.decorators import has_permission
from app import db


@main.route('/')
@login_required
def index():
    page = request.args.get('page', '1')
    try:
        page = int(page)
    except ValueError:
        page = 1

    max_articles_per_page = current_app.config['MAX_ARTICLES_PER_PAGE']
    article_pager = Article.query.filter_by(is_published=True).order_by(Article.time_published.desc()).paginate(
        per_page=max_articles_per_page,
        page=page)

    return render_template('index.html', pager=article_pager)


@main.route('/profile/<username>')
@login_required
def user_profile(username):
    user = User.query.filter_by(username=username).one_or_none()
    if not user:
        abort(404)

    return render_template('main/view_profile', user=user)


@main.route('/article/<hyphenated_title>')
@login_required
def view_article(hyphenated_title):
    words = hyphenated_title.split('-')
    format_string = '{}%' * len(words)
    try:
        article = Article.query.filter(
            Article.title.ilike(format_string.format(*words))).one()
    except (NoResultFound, MultipleResultsFound) as exc:
        # return custom error page
        current_app.logger.debug(exc)
        return render_template('error_page.html')

    return render_template('main/view_article.html', article=article)


@main.route('/write-article', methods=['GET', 'POST'])
@login_required
def write_article():
    form = WriteArticleForm()
    if form.validate_on_submit():
        title = form.title.data.strip()
        author = form.author.data.strip()
        year_published = form.year_published.data
        book = Book(title=title, author=author, year_published=year_published)
        db.session.add(book)

        user = current_user._get_current_object()
        article = Article(title=title, book=book, author=user,
                          body_text=form.markdown_field.data)

        db.session.add(article)

        given_tags = form.tags.data
        tags = Tag.query.filter(Tag.name.in_(given_tags)).all()
        article.tags = tags

        hyphenated_title = article.hyphenated_title
        image = form.book_image.data
        if image:
            extension = image.split('.')[-1]
            filename = '{}.{}'.format(hyphenated_title, extension)
            image_path = os.path.join(current_app.instance_path,
                                      'app/static/img/uploads', filename)
            image.save(image_path)
            uploaded_image = UploadedImage(filename=filename, path=image_path)
            db.session.add(uploaded_image)
            article.image = uploaded_image

        published = form.publish.data
        if published:
            article.time_published = datetime.datetime.utcnow()
            article.is_published = True
            flash('Your article has been successfully published.', 'success')
            db.session.commit()
            return redirect(url_for('main.view_article',
                                    hyphenated_title=hyphenated_title))
        else:
            flash('Article saved.')

    return render_template('main/write_article.html', form=form)
