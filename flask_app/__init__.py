# Based on this tutorial
# http://blog.miguelgrinberg.com/post/oauth-authentication-with-flask
#
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
import logging
import sys

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

lm = LoginManager(app)
lm.login_view = 'index'

from flask_app import views, models

# Expose datetime-formatting and money-formatting functions to all templates
from flask_app.momentjs import Momentjs
from locale import currency
app.jinja_env.globals['Momentjs'] = Momentjs
app.jinja_env.globals['currency'] = currency

app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)