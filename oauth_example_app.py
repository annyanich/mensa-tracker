# Based on this tutorial
# http://blog.miguelgrinberg.com/post/oauth-authentication-with-flask
#
from flask import Flask, redirect, url_for, flash, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, UserMixin, current_user, \
    login_user, logout_user
from oauth_example_oauth import OAuthSignIn, FacebookSignIn

app = Flask(__name__)
app.config['SECRET_KEY'] = 'V\x8cjc\xff\xb8\x02\x9f@JV\r\xd9K\xe9\xd5\xe0\xa1m\x9e\xd0 \x99*'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:\\temp\\mensa-scraper-oauth-test-db.sqlite'
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

db = SQLAlchemy(app)
lm = LoginManager(app)
lm.login_view = 'index'


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    social_id = db.Column(db.String(64), nullable=False, unique=True)
    nickname = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=True)

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


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)