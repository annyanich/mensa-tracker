# From Miguel Grinberg's Flask tutorial
# Activates cross-site request forgery prevention for the Flask-WTF extension
# WTF_CSRF_ENABLED = True

import os

basedir = os.path.abspath(os.path.dirname(__file__))

# ('DATABASE_URL' is the environment variable used by Heroku for the main SQL
# attached to an app.  In this case, we only have one database, so that is the one we
# want.)
if os.environ.get('DATABASE_URL') is None:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db.sqlite')
else:
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

# Explicitly disable Flask-SQLAlchemy's event notification system.  It defaults to False,
# but Flask will throw a warning unless we explicitly set it to False ourselves.
SQLALCHEMY_TRACK_MODIFICATIONS = False

DEBUG = None

# SECRET_KEY is a cryptographic secret used by Flask.
# You should generate a new one before deploying this app, or attackers will
# find this key on Github and do bad stuff to you.
if os.environ.get('SECRET_KEY') is None:
    SECRET_KEY = 'V\x8cjc\xff\xb8\x02\x9f@JV\r\xd9K\xe9\xd5\xe0\xa1m\x9e\xd0 \x99*'
else:
    SECRET_KEY = os.environ['SECRET_KEY']
