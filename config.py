import os
basedir = os.path.abspath(os.path.dirname(__file__))
#test_pwd


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'some-key'
    POSTGRES = {
        'user': os.getenv('POSTGRES_USER'),
        'pw': os.getenv('POSTGRES_PASSWORD'),
        'db': os.getenv('POSTGRES_DB'),
        'host': os.getenv('HOST'),
        'port': os.getenv('PORT'),
    }
    SQLALCHEMY_DATABASE_URI = 'postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
    print(SQLALCHEMY_DATABASE_URI)


class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True