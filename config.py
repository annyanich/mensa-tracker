# From Miguel Grinberg's Flask tutorial
# Activates cross-site request forgery prevention for the Flask-WTF extension
# WTF_CSRF_ENABLED = True

import os

basedir = os.path.abspath(os.path.dirname(__file__))

# Heroku gives us the url of the app's Postgres database via the environment
# variable 'DATABASE_URL'.
if os.environ.get('DATABASE_URL') is None:
    raise ValueError('The environment variable "DATABASE_URL" is not specified.  '
                     'Please specify a database url for SQLAlchemy to connect to.')
else:
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

# Explicitly disable Flask-SQLAlchemy's event notification system.  It defaults to False,
# but Flask will throw a warning unless we explicitly set it to False ourselves.
SQLALCHEMY_TRACK_MODIFICATIONS = False

DEBUG = None

# SECRET_KEY is a cryptographic secret used by Flask.
if os.environ.get('SECRET_KEY') is None:
    raise ValueError('The environment variable "SECRET_KEY" is missing.  '
                     'Please specify a SECRET_KEY for Flask to use as a cryptographic secret.'
                     'See http://flask.pocoo.org/docs/0.11/quickstart/ for an example of how to generate one.')
else:
    SECRET_KEY = os.environ['SECRET_KEY']
