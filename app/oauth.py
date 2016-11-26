from rauth import OAuth1Service, OAuth2Service
from flask import current_app, url_for, request, redirect, session
import requests
import json


class OAuthSignIn(object):
    """A dictionary, built via introspection in the get_provider() method,
    which holds references to all the subclasses of this class."""
    providers = None

    def __init__(self, provider_name):
        self.provider_name = provider_name
        credentials = current_app.config['OAUTH_CREDENTIALS'][provider_name]
        self.consumer_id = credentials['id']
        self.consumer_secret = credentials['secret']

    def authorize(self):
        """Redirects to the provider's website to let the user
        authenticate there"""
        pass

    def reauthorize(self):
        """Redirects to the provider's website to let the user grant us permissions,
        like giving us access to their email address."""
        pass

    def callback(self):
        """Handles the callback when the provider redirects back to our app
        post-authentication.
        :return A three-tuple: Social ID, Nickname, Email address"""
        pass

    def revoke_email_permission(self, user_id):
        """Tells the OAuth provider that we no longer want access to the users's
        email address.
        :return True if successful, False otherwise"""
        pass

    def get_callback_url(self):
        return url_for('oauth_callback', provider=self.provider_name,
                       _external=True)

    @classmethod
    def get_provider(cls, provider_name):
        """Look up the correct OAuthSignIn instance given a provider name.

        When first called, use introspection to build a dictionary,
        stored in OAuthSignIn.providers, containing an instance of every
        subclass of OAuthSignIn.

        :param provider_name: The name of the provider to look up.  Each
        provider's name is defined in the corresponding OAuthSignIn subclass.
        """
        if cls.providers is None:
            cls.providers = {}
            for provider_class in cls.__subclasses__():
                provider = provider_class()
                cls.providers[provider.provider_name] = provider
        return cls.providers[provider_name]


class FacebookSignIn(OAuthSignIn):
    def __init__(self):
        super().__init__('facebook')
        self.service = OAuth2Service(
            name='facebook',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            # authorize_url='https://graph.facebook.com/oauth/authorize',
            authorize_url='https://www.facebook.com/dialog/oauth',
            access_token_url='https://graph.facebook.com/oauth/access_token',
            base_url='https://graph.facebook.com'

            )

    def authorize(self):
        return redirect(self.service.get_authorize_url(
            scope='email',  # Ask Facebook for user's email address
            response_type='code',  # Indicates we are a web app
            redirect_uri=self.get_callback_url()
        ))

    def reauthorize(self):
        return redirect(self.service.get_authorize_url(
            scope='email',
            response_type='code',
            redirect_uri=self.get_callback_url(),
            auth_type='rerequest'
        ))

    def callback(self):
        if 'code' not in request.args:
            return None, None, None
        oauth_session = self.service.get_auth_session(
            data={'code': request.args['code'],
                  'grant_type': 'authorization_code',
                  'redirect_uri': self.get_callback_url()}
        )

        me = oauth_session.get('me', params={'fields': 'email,name'}).json()
        email = me.get('email')
        return (
            'facebook$' + me['id'],  # Social ID
            me['name'],  # Nickname = user's real name
            email  # Email address
        )

    def revoke_email_permission(self, user_id):
        permission_url = 'https://graph.facebook.com/v2.8/{user_id}/permissions/email'.format(
            user_id=user_id
        )
        outcome = requests.delete(permission_url,
                     params={'access_token': '{0}|{1}'.format(self.consumer_id, self.consumer_secret)})
        outcome_json = json.loads(outcome.text)

        answer = outcome_json.get('success') is True
        return answer



# class TwitterSignIn(OAuthSignIn):
#     def __init__(self):
#         super(TwitterSignIn, self).__init__('twitter')
#         self.service = OAuth1Service(
#             name='twitter',
#             consumer_key=self.consumer_id,
#             consumer_secret=self.consumer_secret,
#             request_token_url='https://api.twitter.com/oauth/request_token',
#             authorize_url='https://api.twitter.com/oauth/authorize',
#             access_token_url='https://api.twitter.com/oauth/access_token',
#             base_url='https://api.twitter.com/1.1/'
#         )