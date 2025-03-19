from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db

# Таблица подписок (followers)
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    avatar_url = db.Column(db.String(120), default='default.jpg')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    bio = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Социальные сети
    facebook_url = db.Column(db.String(200))
    twitter_url = db.Column(db.String(200))
    instagram_url = db.Column(db.String(200))
    linkedin_url = db.Column(db.String(200))
    github_url = db.Column(db.String(200))
    
    # Отношения
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', foreign_keys='Comment.user_id', backref='user', lazy='dynamic')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic')
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
    
    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
    
    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0
    
    def followed_posts(self):
        from app.models.post import Post
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())
    
    def __repr__(self):
        return f'<User {self.username}>' 