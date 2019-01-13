# From Miguel Grinberg's Flask tutorial
# Activates cross-site request forgery prevention for the Flask-WTF extension
# WTF_CSRF_ENABLED = True

import os
import locale

basedir = os.path.abspath(os.path.dirname(__file__))

locale.setlocale(locale.LC_MONETARY, 'de_DE.utf8')

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

if os.environ.get('CLOUDAMQP_URL') is None:
    print("The environment variable 'CLOUDAMQP_URL' is missing.  "
          "Without it, we can't queue up emails in RabbitMQ.  "
          "This is normally provided by the RabbitMQ Bigwig addon in Heroku.")
else:
    CLOUDAMQP_URL = os.environ['CLOUDAMQP_URL']

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

    # "file:///vagrant/test%20menu%20pages/uhlhornsweg-culinarium-20161222.html":
    #     "Uhlhornsweg Culinarium",
    "file:///vagrant/test%20menu%20pages/uhlhornsweg-culinarium-20170106.html":
        "Uhlhornsweg Culinarium",
    # "file:///vagrant/test%20menu%20pages/uhlhornsweg-pastaveggievegan-20161222.html":
    #     "Uhlhornsweg Pasta & Veggie/Vegan",
    "file:///vagrant/test%20menu%20pages/uhlhornsweg-pastaveggievegan-20170106.html":
        "Uhlhornsweg Pasta & Veggie/Vegan",
    # "file:///vagrant/test%20menu%20pages/uhlhornsweg-classic-20161222.html":
    #     "Uhlhornsweg Classic",
    "file:///vagrant/test%20menu%20pages/uhlhornsweg-classic-20170106.html":
        "Uhlhornsweg Classic",
    # "file:///vagrant/test%20menu%20pages/wechloy-20161222.html": "Wechloy",
    "file:///vagrant/test%20menu%20pages/wechloy-20170106.html": "Wechloy",
    # "file:///vagrant/test%20menu%20pages/ofener-strasse-20161223.html": "Ofener Straße",
    "file:///vagrant/test%20menu%20pages/ofener-strasse-20170106.html": "Ofener Straße",
    # "file:///vagrant/test%20menu%20pages/emden-20161223.html": "Emden",
    # "file:///vagrant/test%20menu%20pages/wilhelmshaven-20161223.html": "Wilhelmshaven",
    # "file:///vagrant/test%20menu%20pages/elsfleth-20161223.html": "Elsfleth"
}


def we_are_scraping_a_real_website():
    for url in menu_urls_and_names.keys():
        if not url.startswith('file:///'):
            return True
    return False

SCRAPY_USER_AGENT = 'Anns Mensa Tracker (mensa-tracker.herokuapp.com) (ann.yanich@gmail.com)'

# Scrapy waits this many seconds in between requests to the same website.
# Please don't change '60' to a lower value.
# If we send too many requests too fast, the Studentenwerk may get upset.
SCRAPY_DOWNLOAD_DELAY = 60 if we_are_scraping_a_real_website() else 1
