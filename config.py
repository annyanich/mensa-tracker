# From Miguel Grinberg's Flask tutorial
# Activates cross-site request forgery prevention for the Flask-WTF extension
# WTF_CSRF_ENABLED = True

import os
import locale

basedir = os.path.abspath(os.path.dirname(__file__))

# Heroku gives us the url of the app's Postgres database via the environment
# variable 'DATABASE_URL'.
if os.environ.get('DATABASE_URL') is None:
    raise ValueError('The environment variable "DATABASE_URL" is missing.  '
                     'It should point to your SQL database.  '
                     'If you see this error while deployed to Heroku, you '
                     'probably need to add the heroku-postgresql addon to '
                     'your app.')
else:
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

# Explicitly disable Flask-SQLAlchemy's event notification system.  It
# defaults to False, but Flask will throw a warning unless we explicitly set
# it to False ourselves.
SQLALCHEMY_TRACK_MODIFICATIONS = False

if os.environ.get('DEBUG') is None:
    print('The environment variable "DEBUG" is not set.  '
          'It is used to determine whether debugging is enabled for Flask.  '
          'Defaulting to DEBUG=False.')
    DEBUG = False
else:
    val = os.environ['DEBUG']
    if val == 'True' or val == 'False':
        DEBUG = val
    else:
        print('The environment variable "DEBUG" (used by Flask) has an '
              'inappropriate value: {0}. Only "True" or "False" are accepted. '
              ' Defaulting to DEBUG=False.'.format(val))
        DEBUG = False


# SECRET_KEY is a cryptographic secret used by Flask.
if os.environ.get('SECRET_KEY') is None:
    print('The environment variable "SECRET_KEY" is missing.  '
          "Without it, Flask won't work.  "
          'See http://flask.pocoo.org/docs/0.11/quickstart/ for an example '
          'of how to generate one.')
else:
    SECRET_KEY = os.environ['SECRET_KEY']

OAUTH_CREDENTIALS = {'facebook': {}}


if os.environ.get('FACEBOOK_APP_ID') is None:
    print('The environment variable "FACEBOOK_APP_ID" is missing.  '
          "Without it, users won't be able to log in to our website.  "
          "You can get it from your app's control panel in "
          'developers.facebook.com.')
else:
    OAUTH_CREDENTIALS['facebook']['id'] = os.environ['FACEBOOK_APP_ID']

if os.environ.get('FACEBOOK_APP_SECRET') is None:
    print('The environment variable "FACEBOOK_APP_SECRET" is missing.  '
          "Without it, users won't be able to log in to our website.  "
          "You can get it from your app's control panel in "
          'developers.facebook.com.')
else:
    OAUTH_CREDENTIALS['facebook']['secret'] = os.environ['FACEBOOK_APP_SECRET']

if os.environ.get('RABBITMQ_BIGWIG_URL') is None:
    print("The environment variable 'RABBITMQ_BIGWIG_URL' is missing.  "
          "Without it, we can't queue up emails in RabbitMQ.  "
          "This is normally provided by the RabbitMQ Bigwig addon in Heroku.")
else:
    RABBITMQ_BIGWIG_URL = os.environ['RABBITMQ_BIGWIG_URL']

if os.environ.get('GMAIL_USERNAME') is None:
    print("The environment variable 'GMAIL_USERNAME' is missing.  "
          "Without it, we can't send out email alerts.")
else:
    GMAIL_USERNAME = os.environ['GMAIL_USERNAME']

if os.environ.get('GMAIL_PASSWORD') is None:
    print("The environment variable 'GMAIL_PASSWORD' is missing.  "
          "Without it, we can't send out email alerts.")
else:
    GMAIL_PASSWORD = os.environ['GMAIL_PASSWORD']


menu_urls_and_names = {
    # "https://www.studentenwerk-oldenburg.de/de/gastronomie/speiseplaene"
    # "/uhlhornsweg-ausgabe-b.html": "Uhlhornsweg Classic",
    # "https://www.studentenwerk-oldenburg.de/de/gastronomie/speiseplaene"
    # "/uhlhornsweg-culinarium.html": "Uhlhornsweg Culinarium",
    # "https://www.studentenwerk-oldenburg.de/de/gastronomie/speiseplaene"
    # "/uhlhornsweg-ausgabe-a.html": "Uhlhornsweg Pasta & Veggie/Vegan"
    "file:///vagrant/test%20menu%20pages/uhlhornsweg-culinarium-20161222.html": "Uhlhornsweg Culinarium",
    "file:///vagrant/test%20menu%20pages/uhlhornsweg-pastaveggievegan-20161222.html": "Uhlhornsweg Pasta & Veggie/Vegan",
    "file:///vagrant/test%20menu%20pages/wechloy-20161222.html": "Wechloy",
    "file:///vagrant/test%20menu%20pages/uhlhornsweg-classic-20161222.html": "Uhlhornsweg Classic"
}

locale.setlocale(locale.LC_MONETARY, 'de_DE.utf8')
