from app import db
from datetime import datetime

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user2_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    
    user1 = db.relationship('User', foreign_keys=[user1_id], backref='conversations_started')
    user2 = db.relationship('User', foreign_keys=[user2_id], backref='conversations_received')
    messages = db.relationship('Message', backref='conversation', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Conversation {self.id}>'

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'))
    content = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    
    sender = db.relationship('User', foreign_keys=[sender_id], backref='messages_sent')
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref='messages_received')
    
    def __repr__(self):
        return f'<Message {self.id}>' 