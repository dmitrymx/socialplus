from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.message import Message, Conversation
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length
from datetime import datetime

bp = Blueprint('messages', __name__)

class MessageForm(FlaskForm):
    content = TextAreaField('Сообщение', validators=[DataRequired(), Length(min=1, max=500)])
    submit = SubmitField('Отправить')

@bp.route('/inbox')
@login_required
def inbox():
    conversations = Conversation.query.filter(
        (Conversation.user1_id == current_user.id) | 
        (Conversation.user2_id == current_user.id)
    ).all()
    
    # Получаем последние сообщения для каждого разговора
    conversation_data = []
    for conv in conversations:
        other_user = conv.user2 if conv.user1_id == current_user.id else conv.user1
        last_message = Message.query.filter_by(conversation_id=conv.id).order_by(Message.timestamp.desc()).first()
        unread_count = Message.query.filter_by(
            conversation_id=conv.id, 
            recipient_id=current_user.id,
            is_read=False
        ).count()
        
        conversation_data.append({
            'conversation': conv,
            'other_user': other_user,
            'last_message': last_message,
            'unread_count': unread_count
        })
    
    # Сортируем по времени последнего сообщения (новые сверху)
    conversation_data.sort(
        key=lambda x: x['last_message'].timestamp if x['last_message'] else datetime.min, 
        reverse=True
    )
    
    return render_template('messages/inbox.html', title='Сообщения', conversations=conversation_data)

@bp.route('/conversation/<int:user_id>', methods=['GET', 'POST'])
@login_required
def conversation(user_id):
    other_user = User.query.get_or_404(user_id)
    
    # Проверяем, существует ли уже разговор между пользователями
    conversation = Conversation.query.filter(
        ((Conversation.user1_id == current_user.id) & (Conversation.user2_id == user_id)) |
        ((Conversation.user1_id == user_id) & (Conversation.user2_id == current_user.id))
    ).first()
    
    # Если разговора нет, создаем новый
    if not conversation:
        conversation = Conversation(user1_id=current_user.id, user2_id=user_id)
        db.session.add(conversation)
        db.session.commit()
    
    # Помечаем все непрочитанные сообщения как прочитанные
    unread_messages = Message.query.filter_by(
        conversation_id=conversation.id,
        recipient_id=current_user.id,
        is_read=False
    ).all()
    
    for message in unread_messages:
        message.is_read = True
    
    db.session.commit()
    
    # Получаем все сообщения в разговоре
    messages = Message.query.filter_by(conversation_id=conversation.id).order_by(Message.timestamp).all()
    
    # Форма для отправки нового сообщения
    form = MessageForm()
    if form.validate_on_submit():
        message = Message(
            sender_id=current_user.id,
            recipient_id=user_id,
            conversation_id=conversation.id,
            content=form.content.data
        )
        db.session.add(message)
        db.session.commit()
        return redirect(url_for('messages.conversation', user_id=user_id))
    
    return render_template('messages/conversation.html', 
                          title=f'Чат с {other_user.username}',
                          other_user=other_user,
                          messages=messages,
                          form=form)

@bp.route('/new_message/<int:user_id>')
@login_required
def new_message(user_id):
    other_user = User.query.get_or_404(user_id)
    form = MessageForm()
    return render_template('messages/new_message.html', 
                          title=f'Новое сообщение для {other_user.username}',
                          other_user=other_user,
                          form=form)

@bp.route('/send_message/<int:user_id>', methods=['POST'])
@login_required
def send_message(user_id):
    other_user = User.query.get_or_404(user_id)
    form = MessageForm()
    
    if form.validate_on_submit():
        # Проверяем, существует ли уже разговор между пользователями
        conversation = Conversation.query.filter(
            ((Conversation.user1_id == current_user.id) & (Conversation.user2_id == user_id)) |
            ((Conversation.user1_id == user_id) & (Conversation.user2_id == current_user.id))
        ).first()
        
        # Если разговора нет, создаем новый
        if not conversation:
            conversation = Conversation(user1_id=current_user.id, user2_id=user_id)
            db.session.add(conversation)
            db.session.commit()
        
        # Создаем новое сообщение
        message = Message(
            sender_id=current_user.id,
            recipient_id=user_id,
            conversation_id=conversation.id,
            content=form.content.data
        )
        db.session.add(message)
        db.session.commit()
        
        flash('Сообщение отправлено!')
        return redirect(url_for('messages.conversation', user_id=user_id))
    
    return render_template('messages/new_message.html', 
                          title=f'Новое сообщение для {other_user.username}',
                          other_user=other_user,
                          form=form)

@bp.route('/api/send_message/<int:user_id>', methods=['POST'])
@login_required
def api_send_message(user_id):
    data = request.json
    if not data or 'content' not in data:
        return jsonify({'error': 'Отсутствует содержание сообщения'}), 400
    
    other_user = User.query.get_or_404(user_id)
    
    # Проверяем, существует ли уже разговор между пользователями
    conversation = Conversation.query.filter(
        ((Conversation.user1_id == current_user.id) & (Conversation.user2_id == user_id)) |
        ((Conversation.user1_id == user_id) & (Conversation.user2_id == current_user.id))
    ).first()
    
    # Если разговора нет, создаем новый
    if not conversation:
        conversation = Conversation(user1_id=current_user.id, user2_id=user_id)
        db.session.add(conversation)
        db.session.commit()
    
    # Создаем новое сообщение
    message = Message(
        sender_id=current_user.id,
        recipient_id=user_id,
        conversation_id=conversation.id,
        content=data['content']
    )
    db.session.add(message)
    db.session.commit()
    
    return jsonify({
        'id': message.id,
        'content': message.content,
        'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'sender_id': message.sender_id,
        'recipient_id': message.recipient_id
    }) 