from flask import render_template, url_for, flash, redirect, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required, LoginManager
from app import app, db, lm
from .forms import LoginForm
from .models import User
from auth import GoogleSignIn, OAuthSignIn


@app.route('/')
@app.route('/index')
def index():
  user = g.user
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

@app.before_request
def before_request():
    g.user = current_user

@app.route('/login', methods=['GET', 'POST'])
def login():
  form = LoginForm()
  if form.validate_on_submit():
      flash('Login requested for userID="%s", remember_me=%s' %
            (form.loginID.data, str(form.remember_me.data)))
      return redirect(url_for('index'))
  return render_template('login.html', title='Sign In', form=form)

@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    # Flask-Login function
    if not current_user.is_anonymous():
      return redirect(url_for('index'))
    print provider
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()

@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous():
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    username, email = oauth.callback()
    if email is None:
        # I need a valid email address for my user identification
        flash('Authentication failed.')
        return redirect(url_for('index'))
    # Look if the user already exists
    user=User.query.filter_by(email=email).first()
    if not user:
        # Create the user. Try and use their name returned by Google,
        # but if it is not set, split the email address at the @.
        nickname = username
        if nickname is None or nickname == "":
            nickname = email.split('@')[0]

        # We can do more work here to ensure a unique nickname, if you 
        # require that.
        user=User(nickname=nickname, email=email)
        db.session.add(user)
        db.session.commit()
    # Log in the user, by default remembering them for their next visit
    # unless they log out.
    login_user(user, remember=True)
    return redirect(url_for('index'))

@lm.user_loader
def load_user(id):
  return User.query.get(int(id))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))