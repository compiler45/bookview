import os
import click

from flask import redirect, url_for, request
from flask_migrate import Migrate
from flask_login import current_user

from app import create_app, db
from app.models import Role, User, Tag
from app.permissions import Permission

app_config = os.environ.get('BOOKVIEW_CONFIG', 'default')
app = create_app(config=app_config)
migrate = Migrate(app, db)


@app.before_request
def is_confirmed():
    if current_user.is_authenticated:
        if not current_user.confirmed and request.endpoint not in \
          ['auth.confirm', 'auth.resend_confirmation_email', 'auth.logout']:
            return redirect(url_for('auth.confirm'))


# provide app objects through shell
@app.shell_context_processor
def make_shell_context():
    return dict(db=db, Role=Role, User=User)


@app.cli.command()
def update_db():
    Role.insert_roles()
