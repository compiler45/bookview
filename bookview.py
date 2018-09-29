import os
import click

from flask import redirect, url_for, request
from flask_migrate import Migrate
from flask_login import current_user

from app import create_app, db
from app.models import Role, User, Tag
from app.permissions import Permission
from app.test_data import generate_articles
from app.decorators import attach_request_hooks

app_config = os.environ.get('BOOKVIEW_CONFIG', 'default')
app = create_app(config=app_config)
attach_request_hooks(app)
migrate = Migrate(app, db)


# provide app objects through shell
@app.shell_context_processor
def make_shell_context():
    return dict(db=db, Tag=Tag, Role=Role, User=User, Permission=Permission)


@app.cli.command(help='Update dev database')
def update_dev_db():
    with app.app_context():
        Role.insert_roles()
        Tag.insert_tags()


@app.cli.command(help='Recreate development database')
@click.option('--drop-all', is_flag=True, help='Drop all tables')
@click.option('--add-admin', is_flag=True, help='Add an admin user to the'
              ' database')
@click.option('--num-articles', type=click.INT, help='Add fake articles to the'
              ' database')
def recreate_dev_db(drop_all, add_admin, num_articles):
    # TODO: refactor
    with app.app_context():
        if drop_all:
            app.logger.info('Dropping tables')
            db.drop_all()

        app.logger.info('Creating tables')
        db.create_all()

        Role.insert_roles()
        Tag.insert_tags()

        if add_admin:
            app.logger.info("Creating new admin user 'tmuxlain'")
            admin_user = User(username='tmuxlain',
                              email=app.config['ADMIN_EMAIL'],
                              password=app.config['ADMIN_PASSWORD'],
                              confirmed=True)
            db.session.add(admin_user)
            db.session.commit()

        if num_articles:
            app.logger.info("Generating {} fake articles".format(num_articles))
            generate_articles(number=num_articles)



@app.cli.command('add_user', help='Add a user to the database')
@click.argument('username')
@click.argument('password')
def add_user(username, password):
    with app.app_context():
        email = '{}@example.com'.format(username)
        user = User(username=username, email=email, password=password,
                    confirmed=True)
        db.session.add(user)
        db.session.commit()
        app.logger.info("New user created: {} with password {}".
                        format(email, password))
