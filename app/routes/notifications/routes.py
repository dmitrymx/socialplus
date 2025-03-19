from flask import render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from app.routes.notifications import notifications
from app.models.notification import Notification
from app import db

@notifications.route('/')
@login_required
def index():
    """Отображает страницу уведомлений пользователя."""
    notifications_list = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.timestamp.desc()).all()
    return render_template('notifications/index.html', notifications=notifications_list)

@notifications.route('/mark_read/<int:notification_id>')
@login_required
def mark_read(notification_id):
    """Отмечает уведомление как прочитанное."""
    notification = Notification.query.get_or_404(notification_id)
    if notification.user_id != current_user.id:
        flash('У вас нет доступа к этому уведомлению.', 'error')
        return redirect(url_for('notifications.index'))
    
    notification.is_read = True
    db.session.commit()
    flash('Уведомление отмечено как прочитанное.', 'success')
    return redirect(url_for('notifications.index'))

@notifications.route('/mark_all_read')
@login_required
def mark_all_read():
    """Отмечает все уведомления пользователя как прочитанные."""
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    flash('Все уведомления отмечены как прочитанные.', 'success')
    return redirect(url_for('notifications.index'))

@notifications.route('/delete/<int:notification_id>')
@login_required
def delete(notification_id):
    """Удаляет уведомление."""
    notification = Notification.query.get_or_404(notification_id)
    if notification.user_id != current_user.id:
        flash('У вас нет доступа к этому уведомлению.', 'error')
        return redirect(url_for('notifications.index'))
    
    db.session.delete(notification)
    db.session.commit()
    flash('Уведомление удалено.', 'success')
    return redirect(url_for('notifications.index'))

@notifications.route('/delete_all')
@login_required
def delete_all():
    """Удаляет все уведомления пользователя."""
    Notification.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    flash('Все уведомления удалены.', 'success')
    return redirect(url_for('notifications.index')) 