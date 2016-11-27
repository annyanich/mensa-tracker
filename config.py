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

OAUTH_CREDENTIALS = {'facebook': {}}

if os.environ.get('FACEBOOK_APP_ID') is None:
    raise ValueError('The environment variable "FACEBOOK_APP_ID" is missing.'
                     'Please specify it to allow users to login with Facebook.'
                     'You can get this from developers.facebook.com after creating an app there.')
else:
    OAUTH_CREDENTIALS['facebook']['id'] = os.environ['FACEBOOK_APP_ID']

if os.environ.get('FACEBOOK_APP_SECRET') is None:
    raise ValueError('The environment variable "FACEBOOK_APP_SECRET" is missing.'
                     'Please specify it to allow users to login with Facebook.'
                     'You can get this from developers.facebook.com after creating an app there.')
else:
    OAUTH_CREDENTIALS['facebook']['secret'] = os.environ['FACEBOOK_APP_SECRET']

if os.environ.get('RABBITMQ_BIGWIG_URL') is None:
    raise ValueError("The environment variable 'RABBITMQ_BIGWIG_URL' is missing.  "
                     "Please specify it to allow email alerts to be queued up in RabbitMQ.  "
                     "This is normally provided by the RabbitMQ Bigwig addon in Heroku.")
else:
    RABBITMQ_BIGWIG_URL = os.environ['RABBITMQ_BIGWIG_URL']

if os.environ.get('GMAIL_USERNAME') is None:
    raise ValueError("The environment variable 'GMAIL_USERNAME' is missing.  "
                     "Please provide it so email alerts can be sent out with yagmail.")
else:
    GMAIL_USERNAME = os.environ['GMAIL_USERNAME']

if os.environ.get('GMAIL_PASSWORD') is None:
    raise ValueError("The environment variable 'GMAIL_PASSWORD' is missing.  "
                     "Please provide it so email alerts can be sent out with "
                     "yagmail.")
else:
    GMAIL_PASSWORD = os.environ['GMAIL_PASSWORD']