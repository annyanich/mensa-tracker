from app import app, db, lm
from app.models import User, SavedSearch, MenuEntry
from app.oauth import OAuthSignIn, FacebookSignIn

from flask import redirect, url_for, flash, render_template, request
from flask.ext.login import current_user, login_user, logout_user

import datetime


@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/mensahistory')
def mensa_history():
    menu_entries = MenuEntry.query.order_by(MenuEntry.date_valid)
    return render_template('mensahistory.html', menu_entries=menu_entries)


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
    assert(isinstance(oauth, FacebookSignIn))

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

