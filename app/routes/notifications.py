from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.notification import Notification
from datetime import datetime

bp = Blueprint('notifications', __name__)

@bp.route('/')
@login_required
def index():
    # Получаем все уведомления пользователя, сортируем по времени (новые сверху)
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.timestamp.desc()).all()
    
    # Помечаем непрочитанные уведомления как прочитанные
    unread_notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False).all()
    for notification in unread_notifications:
        notification.is_read = True
    
    db.session.commit()
    
    return render_template('notifications/index.html', title='Уведомления', notifications=notifications)

@bp.route('/mark_read/<int:notification_id>')
@login_required
def mark_read(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    
    # Проверяем, принадлежит ли уведомление текущему пользователю
    if notification.user_id != current_user.id:
        flash('У вас нет доступа к этому уведомлению.')
        return redirect(url_for('notifications.index'))
    
    notification.is_read = True
    db.session.commit()
    
    return redirect(url_for('notifications.index'))

@bp.route('/mark_all_read')
@login_required
def mark_all_read():
    # Помечаем все уведомления пользователя как прочитанные
    unread_notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False).all()
    for notification in unread_notifications:
        notification.is_read = True
    
    db.session.commit()
    flash('Все уведомления помечены как прочитанные.')
    
    return redirect(url_for('notifications.index'))

@bp.route('/delete/<int:notification_id>')
@login_required
def delete(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    
    # Проверяем, принадлежит ли уведомление текущему пользователю
    if notification.user_id != current_user.id:
        flash('У вас нет доступа к этому уведомлению.')
        return redirect(url_for('notifications.index'))
    
    db.session.delete(notification)
    db.session.commit()
    flash('Уведомление удалено.')
    
    return redirect(url_for('notifications.index'))

@bp.route('/delete_all')
@login_required
def delete_all():
    # Удаляем все уведомления пользователя
    notifications = Notification.query.filter_by(user_id=current_user.id).all()
    for notification in notifications:
        db.session.delete(notification)
    
    db.session.commit()
    flash('Все уведомления удалены.')
    
    return redirect(url_for('notifications.index'))

@bp.route('/api/count')
@login_required
def api_count():
    # Возвращаем количество непрочитанных уведомлений
    count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return jsonify({'count': count}) 