from app import db


class User(db.Model):
  # Rows in the database for table 'User'
  id = db.Column(db.Integer, primary_key=True)
  nickname = db.Column(db.String(64), index=True, unique=True)
  email = db.Column(db.String(120), index=True, unique=True)
  posts = db.relationship('Post', backref='author', lazy='dynamic')

  # The user is logged in
  def is_authenticated(self):
      return True

  # The user is active
  def is_active(self):
    return True

  # The user is non anonymous
  def is_anonymous(self):
    return False

  # Unique id for the user
  def get_id(self):
    try:
      return unicode(self.id)  # python 2
    except NameError:
      return str(self.id)  # python 3

  def __repr__(self):
    return '<User %r>' % (self.nickname)


class Post(db.Model):
  # Rows in the database for the table 'Post'
  id = db.Column(db.Integer, primary_key=True)
  body = db.Column(db.String(140))
  timestamp = db.Column(db.DateTime)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

  # How posts are represented
  def __repr__(self):
    return '<Post %r>' % (self.body)
