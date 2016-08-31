
import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    VERSION = '1.0'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to cai haha'
    CELERY_BROKER_URL = 'redis://127.0.0.1:6379/2'
    CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/2'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
    SQLALCHEM_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True

config = {
    'default': DevelopmentConfig,
}