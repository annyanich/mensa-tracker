from flask_app import app, db, lm
from flask_app.models import User, SavedSearch, MenuEntry, MAX_SEARCH_LENGTH
from flask_app.oauth import OAuthSignIn, FacebookSignIn

from flask import redirect, url_for, flash, render_template, request, Markup
from flask.ext.login import current_user, login_user, logout_user
from sqlalchemy import exc

import datetime
import re


@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/mensa-history')
def mensa_history():
    menu_entries = MenuEntry.query.order_by(MenuEntry.date_valid)
    return render_template('mensahistory.html', menu_entries=menu_entries)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# @app.route('/authorize/<provider>')
@app.route('/authorize/facebook')
def oauth_authorize():
    """Invoked when the user clicks the "login with..." button."""
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider('facebook')
    # Intentionally left out support for multiple OAuth providers
    # try:
    #     oauth = OAuthSignIn.get_provider(provider)
    # except KeyError:
    #     flash('Invalid oauth provider')
    #     return redirect(url_for('index'))
    assert(isinstance(oauth, FacebookSignIn))

    return oauth.authorize()


@app.route('/rerequest_permissions/facebook')
def oauth_rerequest_permissions():
    """
    Accessible via a link when the user has failed to grant us permission to access their email address.
    Sends them to Facebook's OAuth permissions dialog.
    If they already have given us permission, then this just bounces them back to the main page.
    """
    if current_user.is_anonymous:
        flash('You need to be logged in to do that.')
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider('facebook')
    return oauth.rerequest_permissions()


@app.route('/callback/login/facebook')
def oauth_callback_authorize():
    if not current_user.is_anonymous:
        return redirect(url_for('index'))

    oauth = OAuthSignIn.get_provider('facebook')
    social_id, username, email, is_email_granted = oauth.callback_authorize()
    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('index'))

    user = User.query.filter_by(social_id=social_id).first()
    if not user:
        user = User(social_id=social_id, nickname=username, email=email)
        try:
            db.session.add(user)
            db.session.commit()
        except exc.SQLAlchemyError:
            flash('Something went wrong while adding you as a user.  Sorry!')
            #  TODO log this
            return redirect(url_for('index'))
    else:  # Update email and nickname to those provided by Facebook.
        # This way, email and name changes are reflected in our interface upon login.
        if email and email != user.email:
            try:
                user.email = email
                db.session.commit()
            except exc.SQLAlchemyError:
                flash('Something went wrong while saving your email to our database.')
                #  TODO log this.
                db.session.rollback()
        if username and username != user.nickname:
            try:
                user.nickname = username
                db.session.commit()
            except exc.SQLAlchemyError:
                #  TODO log this
                flash('Something went wrong while saving your name to our database.')
                db.session.rollback()

    login_user(user, True)
    return redirect(url_for('index'))


@app.route('/callback/rerequest_permissions/facebook')
def oauth_callback_rerequest_permissions():
    if current_user.is_anonymous:
        flash('You need to be logged in to do that')
        return redirect(url_for('index'))

    oauth = OAuthSignIn.get_provider('facebook')
    social_id, username, email, is_email_granted = oauth.callback_rerequest_permissions()

    if not is_email_granted:
        flash("It looks like you didn't give us permission to see your email address." \
              "Please send a bug report (ann.yanich@gmail.com) if you actually did grant "
              "us permission, but still see this message.")
        return redirect(url_for('index'))

    if email and email != current_user.email:
        try:
            current_user.email = email
            db.session.commit()
        except exc.SQLAlchemyError:
            #  TODO log this
            flash('Something went wrong while saving your email to our database.')
            db.session.rollback()
    if username and username != current_user.nickname:
        try:
            current_user.nickname = username
            db.session.commit()
        except exc.SQLAlchemyError:
            #  TODO log this
            flash('Something went wrong while saving your name to our database.')
            db.session.rollback()

    flash('Email permissions granted.  Thanks!  :)')
    return redirect(url_for('index'))


@app.route('/add_search', methods=['POST'])
def add_search():
    if current_user.is_anonymous:
        flash('You need to be logged in to do that.')
        return redirect(url_for('index'))

    already_saved_searches = SavedSearch.query.filter_by(owner=current_user).all()
    if len(already_saved_searches) >= 25:
        flash('You can only have up to 25 saved searches.  Please delete some before you make more.')
        return redirect(url_for('index'))

    search_terms = request.form['search_terms']
    if not search_terms:
        flash("You can't save a search with blank search terms.")
        return redirect(url_for('index'))
    if len(search_terms) > MAX_SEARCH_LENGTH:
        flash("The entered search criteria are too long ({0} characters.)  "
              "Please limit your search's length to {1} characters.".format(len(search_terms),
                                                                            MAX_SEARCH_LENGTH))
        return redirect(url_for('index'))

    search = SavedSearch(owner=current_user,
                         search_terms=search_terms,
                         timestamp=datetime.datetime.utcnow())
    try:
        db.session.add(search)
        db.session.commit()
        flash('Search saved.')
    except exc.SQLAlchemyError:
        #  TODO log this
        flash('Something went wrong while saving your search in our database.')
        db.session.rollback()
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

    try:
        db.session.delete(search)
        db.session.commit()
        flash('Deleted search: %r' % search.search_terms)
        return redirect(url_for('index'))
    except exc.SQLAlchemyError:
        #  TODO log this
        flash('Something went wrong while deleting your search from our database.')
        return redirect(url_for('index'))



@app.route('/delete_email_address')
def delete_email_address():

    if current_user.is_anonymous:
        flash('You need to be logged in to do that')
        return redirect(url_for('index'))

    try:
        current_user.email = None
        db.session.commit()
    except exc.SQLAlchemyError:
        #  TODO log this
        flash('Something went wrong while deleting your email from our database.')
        db.session.rollback()

    oauth = OAuthSignIn.get_provider('facebook')
    user_id = re.findall('\d+', current_user.social_id)[0]  # Strip out the 'facebook$' at the start of the id
    permission_revoked = oauth.revoke_email_permission(user_id)

    if not permission_revoked:
        flash('There was a problem giving up the permission to access your email address.  '
              'It may be re-added to your account here the next time you sign in.  '
              'To permanently remove it, please use your privacy settings in Facebook.')

    return redirect(url_for('index'))
