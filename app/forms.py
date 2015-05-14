from flask.ext.wtf import Form
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired, Length


class LoginForm(Form):
  loginID = StringField('loginID', validators=[DataRequired()])
  remember_me = BooleanField('remember_me', default=False)

class PostForm(Form):
  post = StringField('post', validators=[DataRequired()])

class BaseForm(Form):
  # TODO: Add other fields, category, tag, ...
  base = StringField('base', validators=[DataRequired()])

class EditForm(Form):
  about_me = StringField('about_me', validators=[Length(min=0, max=140)])