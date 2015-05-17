from app import app, db, lm
from auth import GoogleSignIn, OAuthSignIn
from datetime import datetime
from emails import follower_notification
from flask import render_template, url_for, flash, redirect, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required, LoginManager
from forms import LoginForm, EditForm, PostForm, BaseForm
from models import User, User_Post, Base_Post


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
  user = g.user
  posts = ""
  
  form = PostForm()

  if form.validate_on_submit():
    post = User_Post(body=form.post.data, timestamp=datetime.utcnow(), comment=0, extend=0, discriminator='user_post', author=user)

    db.session.add(post)
    db.session.commit()

    flash('Good post')
    return redirect(url_for('index'))

  if user.is_authenticated():
    posts = user.posts

  return render_template('index.html', title='Home', user=user, posts=posts, form=form)

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

        u = user.follow(user)
        db.session.add(u)
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

@app.route('/profile/<nickname>/<page>')
@login_required
def profile(nickname, page):
  user = User.query.filter_by(nickname=nickname).first()
  posts = user.posts

  if not page:
    page = 'About'

  if user is None:
    flash('User not found')
    return redirect(url_for('index'))

  return render_template("profile.html", page=page, user=user, posts=posts)

@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
  form = EditForm()

  if form.validate_on_submit():
    g.user.about_me = form.about_me.data

    db.session.add(g.user)
    db.session.commit()

    flash('Saved Changes')
    return redirect(url_for('edit'))

  else:
    form.about_me = form.about_me

  return render_template('edit.html', form=form)

@app.route('/follow/<nickname>')
@login_required
def follow(nickname):
  user = User.query.filter_by(nickname=nickname).first()

  if user is None:
    flash('User not found')
    return redirect(url_for('index'))

  if user == g.user:
    flash('You cant follow yourself')
    return redirect(url_for('profile', nickname=nickname))

  u = g.user.follow(user)

  if u is None:
    flash('Unable to follow')
    return redirect(url_for('profile', nickname=nickname))

  db.session.add(u)
  db.session.commit()

  flash('You are following %s' % nickname)
  follower_notification(user, g.user)
  return redirect(url_for('profile', nickname=nickname))


@app.route('/unfollow/<nickname>')
@login_required
def unfollow(nickname):
  user = User.query.filter_by(nickname=nickname).first()

  if user is None:
    flash('User not found')
    return redirect(url_for('index'))

  if user == g.user:
    flash('you have to follow yourself')
    return redirect(url_for('profile', nickname=nickname))

  u = g.user.unfollow(user)

  if u is None:
    flash('Unable to unfollow')
    return redirect(url_for('profile', nickname=nickname))

  db.session.add(u)
  db.session.commit()

  flash('You have unfollowed %s' % nickname)
  return redirect(url_for('profile', nickname=nickname))

@app.route('/base_add', methods=['GET', 'POST'])
@login_required
def base_add():
  form = BaseForm()

  if form.validate_on_submit():
    base = Base_Post(body=form.base.data, timestamp=datetime.utcnow(), discriminator='base_post')

    db.session.add(base)
    db.session.commit()

    flash('You have added a story')
    return redirect(url_for('base'))

  return render_template("storyEdit.html", form=form)

@app.route('/base')
def base():
  user = g.user 
  comments = ""

  bases = Base_Post.query.filter_by(discriminator='base_post')
  comments = User_Post.query.filter_by(discriminator='user_post', extend=0)
  extends = User_Post.query.filter_by(discriminator='user_post', comment=0)

  return render_template("story.html", bases=bases, comments=comments, extends=extends, user=user)

@app.route('/base_extend/<int:base_id>', methods=['GET', 'POST'])
def base_extend(base_id):
  form = PostForm()

  if form.validate_on_submit():
    extended = User_Post(body=form.post.data, timestamp=datetime.utcnow(), comment=0, extend=base_id, discriminator='user_post', author=g.user)

    db.session.add(extended)
    db.session.commit()

    flash('You extended')
    return redirect(url_for('base'))

  return render_template("post_edit.html", form=form)


@app.route('/comment/<int:base_id>', methods=['GET', 'POST'])
@login_required
def comment(base_id):
  user = g.user
  posts = ""
  form = PostForm()

  if form.validate_on_submit():
    comment = User_Post(body=form.post.data, timestamp=datetime.utcnow(), comment=base_id, extend=0, discriminator='user_post', author=g.user)

    db.session.add(comment)
    db.session.commit()

    flash('you commented')
    return redirect(url_for('base'))

  return render_template("index.html", title='Comment', user=user, posts=posts, form=form)