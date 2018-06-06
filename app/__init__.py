# module where application factory is 
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail

from config import configs

db = SQLAlchemy()
bcrypt = Bcrypt()


def create_app(config='development'):
    app = Flask(__name__)

    # config
    app_config = configs[config]
    app.config.from_object(app_config)
    app_config.init_app(app)

    # attach flask extensions
    bootstrap = Bootstrap(app)
    mail = Mail(app)
    db.init_app(app)

    bcrypt.init_app(app)

    # register blueprints

    return app
