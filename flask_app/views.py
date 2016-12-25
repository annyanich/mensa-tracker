from flask_app import app, db, lm
from flask_app.models import User, SavedSearch, MenuEntry, MAX_SEARCH_LENGTH
from flask_app.oauth import OAuthSignIn, FacebookSignIn

from flask import redirect, url_for, flash, render_template, request, jsonify
from flask.ext.login import current_user, login_user, logout_user
from sqlalchemy import exc

from flask_app.models import MenuEntry

import datetime
import re


@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    # When an anonymous user tries to subscribe to a search, we pass their
    # search terms through Facebook as URL parameters in our redirect URL.
    search_terms = request.args.get('search_terms_to_save', '')
    # Allow only letters and spaces!! Prevent XSS attacks!
    safe_search_terms = re.sub(r'[^a-zA-ZäëöüßÄËÖÜ\s]*', '', search_terms)
    return render_template('index.html', search_terms_url_param=safe_search_terms)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/mensa-history')
def mensa_history():
    menu_entries = MenuEntry.query.order_by(MenuEntry.date_valid)
    return render_template('mensahistory.html', menu_entries=menu_entries)


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
    # TODO allow logging in through Twitter, or another service other than FB
    oauth = OAuthSignIn.get_provider('facebook')
    assert(isinstance(oauth, FacebookSignIn))

    return oauth.authorize()


@app.route('/rerequest_permissions/facebook')
def oauth_rerequest_permissions():
    """
    Lets the user grant us permission to access their email address, should they
    have denied us permission the first time around.
    Sends them to Facebook's OAuth permissions dialog.
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
    search_terms = request.args.get('search_terms_to_save', '')
    social_id, username, email, is_email_granted = oauth.callback_authorize(search_terms)
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
    else:
        # Update email and nickname upon login to those provided by Facebook.
        if email and email != user.email:
            update_email_address(email)
        if username and username != user.nickname:
            update_nickname(username)

    login_user(user, True)

    return redirect(url_for('index', search_terms_to_save=search_terms))


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
        update_email_address(email)
    if username and username != current_user.nickname:
        update_nickname(username)

    flash('Email permissions granted.  Thanks!  :)')
    return redirect(url_for('index'))


@app.route('/test_search', methods=['POST'])
def test_search():
    """
    :param 'search_terms' (HTTP form parameter)
    :return: The most recent 25 menu entries matching the given search terms.
    """
    matches = [menu_entry for menu_entry in MenuEntry.query.all()
               if menu_entry.does_search_match(request.form['search_terms'])
               if menu_entry.mensa in ['Uhlhornsweg Culinarium',
                                       'Uhlhornsweg Pasta & Veggie/Vegan',
                                       'Uhlhornsweg Classic']]
    matches.sort(key=lambda entry: entry.date_valid, reverse=True)

    result_dict = {'result %s' % entry.id:
                    {'date_valid': entry.date_valid.strftime("%d.%m.%Y"),
                     'mensa': entry.mensa,
                     'description': entry.description,
                     'category': entry.category} for entry in matches[:25]}

    return jsonify(result_dict)


@app.route('/add_search', methods=['POST'])
def add_search():
    if current_user.is_anonymous:
        return json_failed("You need to be logged in to save a search.")

    already_saved_searches = SavedSearch.query.filter_by(owner=current_user).all()
    if len(already_saved_searches) >= 25:
        return json_failed('You can only have up to 25 saved searches.  '
                           'Please delete some before you make more.')

    search_terms = request.form['search_terms']
    if not search_terms:
        return json_failed("You can't save a search with blank search terms.")

    if len(search_terms) > MAX_SEARCH_LENGTH:
        return json_failed("The entered search criteria are too long "
                           "({0} characters.)  Please limit your search's "
                           "length to {1} characters.".format(len(search_terms),
                                                              MAX_SEARCH_LENGTH))

    search = SavedSearch(owner=current_user,
                         search_terms=search_terms,
                         timestamp=datetime.datetime.utcnow())
    try:
        db.session.add(search)
        db.session.commit()
        return jsonify({
            "status": "success",
            "search_id": search.id
        })
    except exc.SQLAlchemyError:
        #  TODO log this
        db.session.rollback()
        return json_failed('Something went wrong while saving your search in'
                           ' our database.')


@app.route('/savedsearches/<int:search_id>/delete', methods=['POST'])
def delete_search(search_id):
    if current_user.is_anonymous:
        return json_failed("You need to be logged in to delete a search.")

    search = SavedSearch.query.filter_by(id=search_id).first()
    if (not search) or (search.owner != current_user):
        return json_failed('Invalid search id.  Either the given search id does'
                           ' not exist, or it does not belong to you.')

    try:
        db.session.delete(search)
        db.session.commit()
        return jsonify({
            'status': 'success',
            'search_id': search.id,
            'search_terms': search.search_terms
        })
    except exc.SQLAlchemyError:
        #  TODO log this
        return json_failed('Something went wrong while deleting your search '
                           'from our database.')


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
    # Strip out the 'facebook$' at the start of the id
    user_id = re.findall('\d+', current_user.social_id)[0]
    permission_revoked = oauth.revoke_email_permission(user_id)

    if not permission_revoked:
        flash('There was a problem giving up the permission to access your email address.  '
              'It may be re-added to your account here the next time you sign in.  '
              'To permanently remove it, please use your privacy settings in Facebook.')

    return redirect(url_for('index'))


def json_failed(reason):
    return jsonify({
        "status": "failed",
        "reason": reason
    })


def update_email_address(email):
    try:
        current_user.email = email
        db.session.commit()
    except exc.SQLAlchemyError:
        #  TODO log this
        flash('Something went wrong while saving your email to our database.')
        db.session.rollback()


def update_nickname(nickname):
    try:
        current_user.nickname = nickname
        db.session.commit()
    except exc.SQLAlchemyError:
        #  TODO log this
        flash('Something went wrong while saving your name to our database.')
        db.session.rollback()

