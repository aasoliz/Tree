from flask import url_for, current_app, redirect, request
from rauth import OAuth2Service

import json, urllib2

# Wrapper class for specific logins
class OAuthSignIn(object):
  providers = None

  def __init__(self, provider_name):
    self.provider_name = provider_name
    
    # Get credentials from config
    credentials = current_app.config['CREDENTIALS'][provider_name]
    self.id = credentials['id']
    self.secret = credentials['secret']

  def authorize(self):
    pass

  def callback(self):
    pass

  def get_callback_url(self):
    return url_for('oauth_callback', 
      provider=self.provider_name, 
      _external=True
    )

  @classmethod
  def get_provider(self, provider_name):
    if self.providers is None:
      self.providers={}

      # For each class that derives from 'OAuth'
      for provider_class in self.__subclasses__():
        provider = provider_class()
        self.providers[provider.provider_name] = provider
    
    # Return the 'provider_class' that is associated with the 'provider_name'
    return self.providers[provider_name]

class GoogleSignIn(OAuthSignIn):
  def __init__(self):
    # Create OAuth object iwth provider 'google'
    super(GoogleSignIn, self).__init__('google')
    
    # Load webpage
    googleinfo = urllib2.urlopen('https://accounts.google.com/.well-known/openid-configuration')
    
    # Load json
    google_params = json.load(googleinfo)
    
    # Set service object for object
    self.service_object = OAuth2Service(
      name='google',
      client_id=self.id,
      client_secret=self.secret,
      authorize_url=google_params.get('authorization_endpoint'),
      base_url=google_params.get('userinfo_endpoint'),
      access_token_url=google_params.get('token_endpoint')
    )

  def authorize(self):
    # Requesting email and profile
    # Get a 'code' in response
    return redirect(self.service_object.get_authorize_url(
      scope='email profile',
      response_type='code',
      redirect_uri=self.get_callback_url()
      )
    )

  def callback(self):
    # Check if a 'code' was returned
    if 'code' not in request.args:
      return None, None
    
    # Get the 'code' and 'grant_type'
    oauth_session = self.service_object.get_auth_session(
      data={
        'code': request.args['code'],
        'grant_type': 'authorization_code',
        'redirect_uri': self.get_callback_url()
      },
      decoder = json.loads
    )
    me = oauth_session.get('').json()
    
    # Return the name and email of the logged in
    return (me['name'], me['email'])