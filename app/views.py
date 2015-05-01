from flask import render_template, url_for, flash, redirect
from app import app
from .forms import LoginForm


@app.route('/')
@app.route('/index')
def index():
  user = {'nickname': 'Andrea'}
  posts = [
      {
          'author': {'nickname': 'Andrea'},
          'body': 'Hello, everybody!'
      },
      {
          'author': {'nickname': 'Kaylene'},
          'body': 'Hey, Andrea!'
      }
  ]
  return render_template('index.html', title='Home', user=user, posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
  form = LoginForm()
  if form.validate_on_submit():
      flash('Login requested for userID="%s", remember_me=%s' %
            (form.loginID.data, str(form.remember_me.data)))
      return redirect(url_for('index'))
  return render_template('login.html', title='Sign In', form=form)
