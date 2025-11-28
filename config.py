import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    # Default to the pre-seeded dev database; override with env DATABASE if needed.
    DATABASE = os.environ.get('DATABASE') or 'sqlite:///' + os.path.join(basedir, 'db_dev.sqlite3')

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}









