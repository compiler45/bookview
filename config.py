import os
import datetime
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Mail information
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_SUBJECT_PREFIX = '[Book View]'
    ADMIN_EMAIL = os.environ.get('BOOKVIEW_ADMIN_EMAIL')
    MAIL_DEFAULT_SENDER = 'Book View Admin <bvadmin@pageparadise.com>'

    # login settings
    REMEMBER_COOKIE_DURATION = datetime.timedelta(hours=2)

    # database settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # generate a random key?
    SECRET_KEY = os.environ.get('SECRET_KEY')

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URI') or \
            'sqlite:///{}'.format(os.path.join(basedir, 'data-dev.sqlite'))
    ADMIN_PASSWORD = os.environ.get('BOOKVIEW_TEST_ADMIN_PASSWORD')


class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URI') or \
            'sqlite:///{}'.format(os.path.join(basedir, 'data-test.sqlite'))
    ADMIN_PASSWORD = os.environ.get('BOOKVIEW_TEST_ADMIN_PASSWORD')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or \
            'sqlite:///{}'.format(os.path.join(basedir, 'data.sqlite'))


configs = {
    'default': DevelopmentConfig, 
    'development': DevelopmentConfig,
    'testing': TestConfig,
    'production': ProductionConfig,
}
