from datetime import datetime
from app import db

class Notification(db.Model):
    """Модель для уведомлений пользователей."""
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(20), default='info')  # info, success, warning, error
    is_read = db.Column(db.Boolean, default=False)
    link = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Связь с пользователем определена в модели User
    
    def __repr__(self):
        return f'<Notification {self.id}: {self.message[:20]}...>'
    
    @staticmethod
    def create_notification(user_id, message, category='info', link=None):
        """Создает новое уведомление для пользователя."""
        notification = Notification(
            user_id=user_id,
            message=message,
            category=category,
            link=link
        )
        db.session.add(notification)
        db.session.commit()
        return notification 