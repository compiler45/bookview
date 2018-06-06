import os

from flask_migrate import Migrate

from app import create_app, db
from app.models import Role, User

app_config = os.environ.get('BOOKVIEW_CONFIG', 'default')
app = create_app(config=app_config)
migrate = Migrate(app, db)


# provide app objects through shell
@app.shell_context_processor
def make_shell_context():
    return dict(db=db, Role=Role, User=User)


@app.cli.command()
def update_db():
    Role.insert_roles()
