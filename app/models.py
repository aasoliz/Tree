from app import db
from flask import flash

# Table for the many to many self-referential relationship of User
follow_table = db.Table('follow_table',
  db.Column('follower', db.Integer, db.ForeignKey('user.id'), primary_key=True),
  db.Column('followee', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

class User(db.Model):
  # Name of the table
  __tablename__ = 'user'

  # Rows in the database for table 'User'
  id = db.Column(db.Integer, primary_key=True)
  nickname = db.Column(db.String(64), index=True, unique=True)
  age = db.Column(db.Integer)
  email = db.Column(db.String(120), index=True, unique=True)
  last_seen = db.Column(db.DateTime)
  about_me = db.Column(db.String(140))
  reputation = db.Column(db.Integer)
  posts = db.relationship('User_Post', backref='author', lazy='dynamic')

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

  # Called when the user follows someone
  # Adds current user to the table of followers for the followee
  def follow(self, user):
    if not self.is_following(user):
      self.followed.append(user)
      return self

  # Called when the user unfollows someone
  # Removes the current user from the table of followers
  def unfollow(self, user):
    if self.is_following(user):
      self.followed.remove(user)
      return self

  # Is the current user following the "user"
  def is_following(self, user):
    return self.followed.filter(follow_table.c.followee == user.id).count() > 0

  # How posts are represented
  def __repr__(self):
    return '<User %r>' % (self.nickname)

# Table for the many to many self-referential relationship of Base_Post
# post_table = db.Table('post_table',
#   db.Column('extend', db.Integer, db.ForeignKey('user_post.id'), primary_key=True),
#   db.Column('base', db.Integer, db.ForeignKey('base_post.id'), primary_key=True)
# )

class Base_Post(db.Model):
  __tablename__ = 'base_post'

  # Rows in the database for the table 'Post'
  id = db.Column(db.Integer, primary_key=True)
  body = db.Column(db.String(140))
  timestamp = db.Column(db.DateTime)
  #user_post_id = db.Column(db.Integer, db.ForeignKey('user_post.id'))
  
  # extending = db.relationship('User_Post',
  #   secondary='post_table',
  #   backref=db.backref('post_table', lazy='dynamic'), lazy='dynamic')

  # extending = db.relationship('Base_Post',
  #   secondary=post_table,
  #   primaryjoin=(post_table.c.base == id),
  #   secondaryjoin=(post_table.c.extend == id),
  #   backref=db.backref('post_table', lazy='dynamic'), lazy='dynamic'
  # )

  # Type of Base_Post
  discriminator = db.Column('type', db.String(50))
  __mapper_args__ = {'polymorphic_identity': 'base_post',
    'polymorphic_on': discriminator}

  # def is_BasePost(self):
  #   return True

  # def extend_base(self, base):
  #   pass
    # if self.is_BasePost():
    #   flash('should not happen')

    # if:
    # base = Base_Post.query.with_polymorphic(Base_Post).filter(id == base_id).first()
    # print base

    # if base is None:
    #   flash('Not found')
    #   return None

    # self.extending.append(base)

    # return self

  def __repr__(self):
    return '<Post %r>' % (self.body)

# Inherits from Base_Post adds columns "views" and a relationship with "User"
class User_Post(Base_Post):

  #__tablename__ = 'user_post'
  # Name the inheritor of "Base_Post"
  __mapper_args__ = {'polymorphic_identity': 'user_post'}

  views = db.Column(db.Integer)
  comment = db.Column(db.Integer, default=0)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

  # def extend_base(self, base):
  #   self.extending.append(base)
  #   return self

    #super(User_Post, self).extend_base(base)

  # Get the post body from the parent class
  def __repr__(self):
    return '<Post %r>' % (super(User_Post, self).body)
