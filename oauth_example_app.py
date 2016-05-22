# Based on this tutorial
# http://blog.miguelgrinberg.com/post/oauth-authentication-with-flask
#
from flask import Flask, redirect, url_for, flash, render_template, request
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, UserMixin, current_user, \
    login_user, logout_user

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

import datetime

import os

from oauth_example_oauth import OAuthSignIn, FacebookSignIn

app = Flask(__name__)

app.config['DEBUG'] = None
# SECRET_KEY is just some random secret key that you need to make.  IDK why
app.config['SECRET_KEY'] = 'V\x8cjc\xff\xb8\x02\x9f@JV\r\xd9K\xe9\xd5\xe0\xa1m\x9e\xd0 \x99*'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'mensa-scraper-oauth-test-db.sqlite'
)
app.config['OAUTH_CREDENTIALS'] = {
    'facebook': {
        'id': '215569478828174',
        'secret': '4ed42c146ac79988bb7073dd77514a45'
    },
    # 'twitter': {
    #     'id': '3RzWQclolxWZIMq5LJqzRZPTl',
    #     'secret': 'm9TEd58DSEtRrZHpz2EjrV9AhsBRxKMo8m3kuIZj3zLwzwIimt'
    # }
}

# Expose datetime-formatting functions to all templates
from momentjs import Momentjs
app.jinja_env.globals['Momentjs'] = Momentjs

db = SQLAlchemy(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

lm = LoginManager(app)
lm.login_view = 'index'


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    social_id = db.Column(db.String(64), nullable=False, unique=True)
    nickname = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=True)
    searches = db.relationship("SavedSearch", backref="owner", lazy='dynamic')

    def __repr__(self):
        return '<User %r>' % self.nickname


class SavedSearch(db.Model):
    __tablename__ = 'searches'
    id = db.Column(db.Integer, primary_key=True)
    search_terms = db.Column(db.String(64), nullable=False)
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return '<SavedSearch %r>' % self.search_terms

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    """Invoked when the user clicks the "login with..." button.
    :param provider: The name of the provider, e.g. 'facebook' or 'twitter'"""
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    assert(isinstance(oauth,FacebookSignIn))
    
    return oauth.authorize()

@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    social_id, username, email = oauth.callback()
    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('index'))
    user = User.query.filter_by(social_id=social_id).first()
    if not user:
        user = User(social_id=social_id, nickname=username, email=email)
        db.session.add(user)
        db.session.commit()
    login_user(user, True)
    return redirect(url_for('index'))

@app.route('/email_entry', methods=['POST'])
def add_user_email():
    if current_user.is_anonymous:
        flash('You need to be logged in to do that.')
        return redirect(url_for('index'))
    email = request.form['email']
    current_user.email = email
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/add_search', methods=['POST'])
def add_search():
    if current_user.is_anonymous:
        flash('You need to be logged in to do that.')
        return redirect(url_for('index'))

    search_terms = request.form['search_terms']
    if not search_terms:
        flash("You can't save a search with blank search terms.")
        return redirect(url_for('index'))

    search = SavedSearch(owner=current_user,
                         search_terms=search_terms,
                         timestamp=datetime.datetime.utcnow())
    db.session.add(search)
    db.session.commit()
    flash('Search saved.')
    return redirect(url_for('index'))


@app.route('/savedsearches/<int:search_id>/delete', methods=['POST'])
def delete_search(search_id):
    if current_user.is_anonymous:
        flash('You need to be logged in to do that.')
        return redirect(url_for('index'))

    search = SavedSearch.query.filter_by(id=search_id).first()
    if (not search) or (search.owner != current_user):
        flash('Invalid search id.  Either the given search id does not exist, '
              'or it does not belong to you.')
        return redirect(url_for('index'))

    db.session.delete(search)
    db.session.commit()
    flash('Deleted search: %r' % search.search_terms)
    return redirect(url_for('index'))


if __name__ == '__main__':
    # db.create_all()
    manager.run()
    # app.run(debug=True)