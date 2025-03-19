from datetime import datetime
from app import db
import emoji

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    likes_count = db.Column(db.Integer, default=0)
    image_url = db.Column(db.String(200))
    
    # Отношения
    likes = db.relationship('Like', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Post {self.id}>'
    
    def like_count(self):
        return self.likes.count()
    
    def comment_count(self):
        return self.comments.count()
    
    def is_liked_by(self, user):
        return Like.query.filter_by(user_id=user.id, post_id=self.id).first() is not None
    
    def formatted_content(self):
        """Преобразует текст с эмодзи-кодами в настоящие эмодзи"""
        return emoji.emojize(self.content, language='alias')

class Like(db.Model):
    __tablename__ = 'like'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='unique_user_post_like'),)

    def __repr__(self):
        return f'<Like {self.id}>'

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    
    def __repr__(self):
        return f'<Comment {self.id}>'
    
    def formatted_content(self):
        """Преобразует текст с эмодзи-кодами в настоящие эмодзи"""
        return emoji.emojize(self.content, language='alias')

# Модель для групп
class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    avatar_url = db.Column(db.String(200), default='group_default.jpg')
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Отношения
    members = db.relationship('GroupMember', backref='group', lazy='dynamic', cascade='all, delete-orphan')
    posts = db.relationship('GroupPost', backref='group', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Group {self.name}>'
    
    def member_count(self):
        return self.members.count()
    
    def is_member(self, user):
        return GroupMember.query.filter_by(user_id=user.id, group_id=self.id).first() is not None

class GroupMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    is_admin = db.Column(db.Boolean, default=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'group_id', name='unique_user_group'),)
    
    def __repr__(self):
        return f'<GroupMember {self.id}>'

class GroupPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    image_url = db.Column(db.String(200))
    
    # Отношения
    likes = db.relationship('GroupPostLike', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('GroupPostComment', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<GroupPost {self.id}>'
    
    def like_count(self):
        return self.likes.count()
    
    def comment_count(self):
        return self.comments.count()
    
    def formatted_content(self):
        """Преобразует текст с эмодзи-кодами в настоящие эмодзи"""
        return emoji.emojize(self.content, language='alias')

class GroupPostLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('group_post.id'))
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='unique_user_group_post_like'),)
    
    def __repr__(self):
        return f'<GroupPostLike {self.id}>'

class GroupPostComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('group_post.id'))
    
    def __repr__(self):
        return f'<GroupPostComment {self.id}>'
    
    def formatted_content(self):
        """Преобразует текст с эмодзи-кодами в настоящие эмодзи"""
        return emoji.emojize(self.content, language='alias') 