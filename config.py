import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Mail information
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_PORT = 587
    MAIL_SUBJECT_PREFIX = '[Book View]'
    ADMIN_EMAIL = os.environ.get('BOOKVIEW_ADMIN_EMAIL')
    BOOKVIEW_MAIL_SENDER = 'Book View Admin <bvadmin@pageparadise.com>'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URI') or \
            'sqlite:///{}'.format(os.path.join(basedir, 'data-dev.sqlite'))


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URI') or \
            'sqlite:///{}'.format(os.path.join(basedir, 'data-test.sqlite'))


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or \
            'sqlite:///{}'.format(os.path.join(basedir, 'data.sqlite'))


configs = {
    'default': DevelopmentConfig, 
    'testing': TestConfig,
    'production': ProductionConfig,
}
