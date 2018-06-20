# module where application factory is 
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_login import LoginManager

from config import configs

db = SQLAlchemy()
bcrypt = Bcrypt()
mail = Mail()

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.session_protection = 'strong'
login_manager.login_message = ''


def create_app(config='development'):
    app = Flask(__name__)

    # config
    app_config = configs[config]
    app.config.from_object(app_config)
    app_config.init_app(app)

    # attach flask extensions
    bootstrap = Bootstrap(app)
    mail.init_app(app)
    db.init_app(app)

    bcrypt.init_app(app)
    login_manager.init_app(app)

    # register blueprints
    from app.main import main
    from app.auth import auth

    app.register_blueprint(main)
    app.register_blueprint(auth)

    return app
