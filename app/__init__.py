from flask import Flask

from config import basedir, ADMINS, MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD
from flask.ext.login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mail import Mail

app = Flask(__name__)
app.config.from_object('config')

if not app.debug:
  import logging
  from logging.handlers import SMTPHandler
  credentials = None
  if MAIL_USERNAME or MAIL_PASSWORD:
    credentials = (MAIL_USERNAME, MAIL_PASSWORD)
  mail_handler = SMTPHandler((MAIL_SERVER, MAIL_PORT), 'no-reply@' + MAIL_SERVER, ADMINS, 'microblog failure', credentials)
  mail_handler.setLevel(logging.ERROR)
  app.logger.addHandler(mail_handler)

mail = Mail(app)

db = SQLAlchemy(app)

# Initialize login capabilities
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

from app import views, models

