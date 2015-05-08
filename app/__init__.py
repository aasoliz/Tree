from flask import Flask

from flask.ext.login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)

# Initialize login capabilities
lm = LoginManager()
lm.init_app(app)

from app import views, models

