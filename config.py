# From Miguel Grinberg's Flask tutorial
# Activates cross-site request forgery prevention for the Flask-WTF extension
# WTF_CSRF_ENABLED = True

import os

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db.sqlite')

# Explicitly disable Flask-SQLAlchemy's event notification system.  It defaults to False,
# but Flask will throw a warning unless we explicitly set it to False ourselves.
SQLALCHEMY_TRACK_MODIFICATIONS = False

DEBUG = None

# SECRET_KEY is a cryptographic secret used by Flask.
# You should generate a new one before deploying this app, or attackers will
# find this key on Github and do bad stuff to you.
SECRET_KEY = 'V\x8cjc\xff\xb8\x02\x9f@JV\r\xd9K\xe9\xd5\xe0\xa1m\x9e\xd0 \x99*'

# More deployment-specific app IDs/secrets.
# Login via Twitter is not yet implemented.
OAUTH_CREDENTIALS = {
    'facebook': {
        'id': '215569478828174',
        'secret': '4ed42c146ac79988bb7073dd77514a45'
    },
    # 'twitter': {
    #     'id': '3RzWQclolxWZIMq5LJqzRZPTl',
    #     'secret': 'm9TEd58DSEtRrZHpz2EjrV9AhsBRxKMo8m3kuIZj3zLwzwIimt'
    # }
}