import os

basedir = os.path.abspath(os.path.dirname(__file__))

CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

GOOGLE_LOGIN_CLIENT_ID = '30238383517-uc6knv2iici0lbf0vi08mqsn8tpnmbso.apps.googleusercontent.com'
GOOGLE_LOGIN_CLIENT_SECRET = 'Qnvsj4o-bt642TBHeLCkT6h7'

CREDENTIALS = {
  'google': 
    {
      'id': GOOGLE_LOGIN_CLIENT_ID,
      'secret': GOOGLE_LOGIN_CLIENT_SECRET
    }
}

# Mail Server Settings
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = 'bry.sharp12@gmail.com'
MAIL_PASSWORD = 'recursion0'
MAIL_DEBUG = True
MAIL_SUPPRESS_SEND = False

# Administrator List
ADMINS = ['bry.sharp12@gmail.com']
