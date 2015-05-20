from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, TextAreaField, DateField, SelectField
from wtforms.validators import DataRequired, Length, Optional
from wtforms.fields.html5 import DateField


class LoginForm(Form):
  loginID = StringField('loginID', validators=[DataRequired()])
  remember_me = BooleanField('remember_me', default=False)

class PostForm(Form):
  post = TextAreaField('post', validators=[DataRequired()])

class BaseForm(Form):
  title = StringField('title', validators=[DataRequired()])
  base = TextAreaField('base', validators=[DataRequired()])
  category = SelectField('category', choices=[('action', 'Action/Adventure'), ('history', 'History'), ('horror', 'Horror'), ('mystery', 'Mystery/Thriller/Suspense'), ('romance', 'Romance'), ('scifi', 'SciFi/Fantasy')], validators=[DataRequired()])

class EditForm(Form):
  about_me = TextAreaField('about_me', validators=[Length(min=0, max=140), Optional()])
  birthday = DateField('birthday', format='%m/%d/%y', validators=[Optional()])
  emails = BooleanField('emails', default=False, validators=[Optional()])