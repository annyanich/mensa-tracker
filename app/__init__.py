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

from app import views, models

# Expose datetime-formatting functions to all templates
from app.momentjs import Momentjs
app.jinja_env.globals['Momentjs'] = Momentjs

app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)