from app import db
from flask import flash

import re

# Table for the many to many self-referential relationship of User
follow_table = db.Table('follow_table',
  db.Column('follower', db.Integer, db.ForeignKey('user.id'), primary_key=True),
  db.Column('followee', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

# Table for many to many between user and posts
fav_table = db.Table('fav_table',
  db.Column('person', db.Integer, db.ForeignKey('user.id'), primary_key=True),
  db.Column('fav', db.Integer, db.ForeignKey('base_post.id'), primary_key=True)
)

class User(db.Model):
  # Name of the table
  __tablename__ = 'user'

  # Rows in the database for table 'User'
  id = db.Column(db.Integer, primary_key=True)
  nickname = db.Column(db.String(64), index=True, unique=True)
  age = db.Column(db.Integer)
  email = db.Column(db.String(120), index=True, unique=True)
  birthday = db.Column(db.Date)
  last_seen = db.Column(db.DateTime)
  about_me = db.Column(db.String(140))
  reputation = db.Column(db.Integer, default=0)
  emails = db.Column(db.Boolean, default=True)
  posts = db.relationship('User_Post', backref='author', lazy='dynamic')
  
  # Many to many relationship
  favs = db.relationship('Base_Post',
    secondary=fav_table,
    backref=db.backref('fav_table', lazy='dynamic'), lazy='dynamic'
  )

  # Describes how to get the data
  followed = db.relationship('User',
    secondary=follow_table,
    primaryjoin=(follow_table.c.follower == id),
    secondaryjoin=(follow_table.c.followee == id),
    backref=db.backref('follow_table', lazy='dynamic'), lazy='dynamic'
  )

  # The user is logged in
  def is_authenticated(self):
      return True

  # The user is active
  def is_active(self):
    return True

  # The user is not anonymous
  def is_anonymous(self):
    return False

  # Unique id for the user
  def get_id(self):
    try:
      return unicode(self.id)  # python 2
    except NameError:
      return str(self.id)  # python 3

  # Adds current user to the table of followers for the followee
  def follow(self, user):
    if not self.is_following(user):
      self.followed.append(user)
      return self

  # Removes the current user from the table of followers
  def unfollow(self, user):
    if self.is_following(user):
      self.followed.remove(user)
      return self

  # Is the current user following the "user"
  def is_following(self, user):
    return self.followed.filter(follow_table.c.followee == user.id).count() > 0

  # Formatted string with date and time
  def seen_last(self):
    return self.last_seen.strftime('on %m/%d/%y at %I:%M')

  # Calculates the reputation of the user (# of posts * (# of favorited posts / 2))
  def reputation(self):
    posts = self.posts.filter_by(comment=0).count()
    faves = self.posts.filter(Base_Post.favorite != 0).count()

    if faves is 0:
      return posts / 2

    return posts * (faves / 2)


  # Inserts into fav_table and adds/removes from base favorite number
  def add_fav(self, base):
    if self.is_faved(base):
      self.favs.remove(base)
      base.favorite = (base.favorite - 1)

      return self
    else:
      self.favs.append(base)
      base.favorite = (base.favorite + 1)
      
      return self

  # Has the user already favorited this post
  def is_faved(self, base):
    return self.favs.filter(fav_table.c.person == self.id, fav_table.c.fav == base.id).count() > 0

  # List of favorites either 'base' or 'extend' depending on 'disc'
  def favorites(self, disc):
    lst = []
    posts =  self.favs.filter(fav_table.c.person == self.id)

    for post in posts:
      if(disc):
        if post.discriminator == 'base_post':
          lst.append(post)
      else:
        if post.discriminator == 'user_post':
          if post.comment == 0:
            lst.append(post)

    return lst

  # How posts are represented
  def __repr__(self):
    return '<User %r>' % (self.nickname)

class Base_Post(db.Model):
  __tablename__ = 'base_post'

  # Rows in the database for the table 'Post'
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(50))
  body = db.Column(db.String(500))
  description = db.Column(db.String(140))
  timestamp = db.Column(db.DateTime)
  category = db.Column(db.String)
  favorite = db.Column(db.Integer, default=0)

  # Type of Base_Post
  discriminator = db.Column('type', db.String(50))
  __mapper_args__ = { 'polymorphic_identity': 'base_post',
    'polymorphic_on': discriminator
  }

  # Proper name of categories
  def proper(self, category):
    if category == 'action':
      return 'Action/Adventure'
    elif category == 'history':
      return 'History'
    elif category == 'horror':
      return 'Horror'
    elif category == 'romance':
      return 'Romance'
    elif category == 'scifi':
      return 'SciFi/Fantasy'

    return 'Mystery/Thriller/Suspense'

  def __repr__(self):
    return '<Post %r>' % (self.body)

# Inherits from Base_Post adds columns "views" and a relationship with "User"
class User_Post(Base_Post):

  # Name the inheritor of "Base_Post"
  __mapper_args__ = { 'polymorphic_identity': 'user_post' }

  views = db.Column(db.Integer, default=0)
  extend = db.Column(db.Integer, default=0)
  comment = db.Column(db.Integer, default=0)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

  # Get the post body from the parent class
  def __repr__(self):
    return '<Post %r>' % (super(User_Post, self).body)
