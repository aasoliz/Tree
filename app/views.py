from app import app, db, lm
from auth import GoogleSignIn, OAuthSignIn
from datetime import datetime, date
from emails import follower_notification
from flask import render_template, url_for, flash, redirect, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required, LoginManager
from forms import LoginForm, EditForm, PostForm, BaseForm
from models import User, User_Post, Base_Post
from dateutil.parser import *


@app.route('/')
@app.route('/index')
def index():
  user = g.user

  return render_template('index.html', title='Home', user=user)

@app.before_request
def before_request():
    g.user = current_user

@app.route('/login', methods=['GET', 'POST'])
def login():
  return render_template('login.html', title='Sign In')

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

    user.last_seen = datetime.now()
    db.session.add(user)
    db.session.commit()

    return redirect(url_for('index'))

@lm.user_loader
def load_user(id):
  return User.query.get(int(id))

@app.route('/logout')
def logout():
  logout_user()
  return redirect(url_for('index'))

@app.route('/profile/<nickname>')
@app.route('/profile/<nickname>/<page>')
@login_required
def profile(nickname, page='About'):
  user = User.query.filter_by(nickname=nickname).first()
  posts = user.posts.paginate(1, 3, False)
  rep = user.reputation()

  if user is None:
    flash('User not found')
    return redirect(url_for('index'))

  # if page == 'Favorites':
  #   posts = user.favorites(True)

  return render_template("profile.html", page=page, user=user, posts=posts, rep=rep)

@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
  form = EditForm()

  if form.validate_on_submit():
    g.user.about_me = form.about_me.data
    g.user.birthday = form.birthday.data
    g.user.emails = form.emails.data

    db.session.add(g.user)
    db.session.commit()

    flash('Saved Changes')
    return redirect(url_for('profile', nickname=g.user.nickname))

  else:
    form.about_me = form.about_me
    form.birthday = form.birthday
    form.emails = form.emails

  print type(form.birthday)
  #print form.birthday.date().strftime('on %m/%d/%y')

  # print 'form %s' % (form.about_me.data)
  # print form.emails
  
  # print str(form.birthday.data)
  # t = parse(form.birthday.data)

  # print t.date().strftime('%d/%m/%y')

  flash('hey')
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
    body_len = len(form.base.data)

    if body_len > 140:
      base = Base_Post(title=form.title.data, body=form.base.data, description=form.base.data[0:140] + '...', timestamp=datetime.utcnow(), category=form.category.data, discriminator='base_post')
    else:
      base = Base_Post(title=form.title.data, body=form.base.data, description=form.base.data, timestamp=datetime.utcnow(), category=form.category.data, discriminator='base_post')

    db.session.add(base)
    db.session.commit()

    flash('You have added a story')

    # Change so that it goes to the page where the user can see the story
    # For now go to story category
    return redirect(url_for('base', category=form.category.data))

  return render_template("storyEdit.html", form=form)

@app.route('/base/<category>')
@app.route('/base/<category>/<int:page>')
def base(category, page=1):
  user = g.user

  bases = Base_Post.query.filter_by(discriminator='base_post', category=category).paginate(page, 10, False)

  proper = bases.items[0].proper(category)

  return render_template("story.html", bases=bases, category=proper, unproper=category)

@app.route('/base_extend/<int:base_id>', methods=['GET', 'POST'])
def base_extend(base_id):
  form = PostForm()

  if form.validate_on_submit():
    base = Base_Post.query.filter_by(id=base_id).first()

    category = base.category
    title = base.title

    body_len = len(form.post.data)

    if body_len > 140:
      extended = User_Post(body=form.post.data, title=title, description=form.post.data[0:140] + '...', timestamp=datetime.utcnow(), category=category, comment=0, extend=base_id, discriminator='user_post', author=g.user)
    else:
      extended = User_Post(body=form.post.data, title=title, description=form.post.data, timestamp=datetime.utcnow(), category=category, comment=0, extend=base_id, discriminator='user_post', author=g.user)

    db.session.add(extended)
    db.session.commit()

    flash('You extended')
    return redirect(url_for('base', category=category))

  return render_template("post_edit.html", form=form)


@app.route('/comment/<int:base_id>', methods=['GET', 'POST'])
@login_required
def comment(base_id):
  user = g.user
  posts = ""
  form = PostForm()

  if form.validate_on_submit():
    category = Base_Post.query.filter_by(id=base_id).first().category
    
    comment = User_Post(body=form.post.data, description=form.post.data, timestamp=datetime.utcnow(), category=category, comment=base_id, extend=0, discriminator='user_post', author=g.user)

    db.session.add(comment)
    db.session.commit()

    flash('you commented')
    return redirect(url_for('base', category=category))

  return render_template("post_edit.html", form=form)

@app.route('/story/<int:base_id>')
@app.route('/story/<int:base_id>/<int:page>')
def story(base_id, page=1):
  base = Base_Post.query.filter_by(id=base_id).first()

  comments = User_Post.query.filter_by(discriminator='user_post', comment=base_id, extend=0).paginate(page, 5, False)
  extends = User_Post.query.filter_by(discriminator='user_post', extend=base_id, comment=0).paginate(page, 3, False)

  return render_template('specific.html', base=base, comments=comments, extends=extends)

@app.route('/fav/<int:base_id>')
def fav(base_id):
  user = g.user
  print user

  base = Base_Post.query.filter_by(id=base_id).first()

  u = user.add_fav(base)

  db.session.add(u)
  db.session.commit()

  flash('successful')

  return redirect(url_for('story', base_id=base_id))