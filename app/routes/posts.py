from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user, login_required
from app import db
from app.models.post import Post, Comment, Like, Group, GroupPost, GroupPostLike, GroupPostComment
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, FileField
from wtforms.validators import DataRequired, Length
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from flask import current_app

bp = Blueprint('posts', __name__)

class PostForm(FlaskForm):
    content = TextAreaField('Что у вас нового?', validators=[DataRequired(), Length(min=1, max=500)])
    image = FileField('Изображение')
    submit = SubmitField('Опубликовать')

class CommentForm(FlaskForm):
    content = TextAreaField('Комментарий', validators=[DataRequired(), Length(min=1, max=200)])
    submit = SubmitField('Отправить')

@bp.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(content=form.content.data, author=current_user)
        
        # Обработка загрузки изображения
        if form.image.data:
            image_file = form.image.data
            if image_file and image_file.filename:
                filename = secure_filename(image_file.filename)
                # Добавляем временную метку к имени файла, чтобы избежать конфликтов
                filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                image_path = os.path.join(current_app.root_path, 'static/images', filename)
                image_file.save(image_path)
                post.image_url = filename
        
        db.session.add(post)
        db.session.commit()
        flash('Ваш пост опубликован!')
        return redirect(url_for('main.index'))
    return render_template('create_post.html', title='Создать пост', form=form)

@bp.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        if current_user.is_authenticated:
            comment = Comment(content=form.content.data, post=post, user=current_user)
            db.session.add(comment)
            db.session.commit()
            flash('Ваш комментарий добавлен!')
            return redirect(url_for('posts.post', id=post.id))
        else:
            flash('Пожалуйста, войдите, чтобы оставить комментарий.')
            return redirect(url_for('auth.login'))
    comments = post.comments.order_by(Comment.created_at.desc()).all()
    return render_template('post.html', post=post, form=form, comments=comments)

@bp.route('/delete_post/<int:id>')
@login_required
def delete_post(id):
    post = Post.query.get_or_404(id)
    if post.author != current_user:
        flash('Вы не можете удалить этот пост.')
        return redirect(url_for('main.index'))
    
    # Удаляем изображение, если оно есть
    if post.image_url:
        image_path = os.path.join(current_app.root_path, 'static/images', post.image_url)
        if os.path.exists(image_path):
            os.remove(image_path)
    
    db.session.delete(post)
    db.session.commit()
    flash('Пост удален.')
    return redirect(url_for('main.index'))

@bp.route('/like/<int:post_id>', methods=['POST'])
@login_required
def like(post_id):
    post = Post.query.get_or_404(post_id)
    like = Like.query.filter_by(user_id=current_user.id, post_id=post.id).first()
    
    if like:
        db.session.delete(like)
        post.likes_count -= 1
        db.session.commit()
        return jsonify({'status': 'unliked', 'count': post.like_count()})
    else:
        like = Like(user_id=current_user.id, post_id=post.id)
        db.session.add(like)
        post.likes_count += 1
        db.session.commit()
        return jsonify({'status': 'liked', 'count': post.like_count()})

@bp.route('/delete_comment/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_comment(id):
    comment = Comment.query.get_or_404(id)
    if comment.user != current_user:
        flash('Вы не можете удалить этот комментарий.')
        return redirect(url_for('posts.post', id=comment.post_id))
    
    post_id = comment.post_id
    db.session.delete(comment)
    db.session.commit()
    flash('Комментарий удален.')
    return redirect(url_for('posts.post', id=post_id))

# Маршруты для групповых постов
@bp.route('/create_group_post/<int:group_id>', methods=['POST'])
@login_required
def create_group_post(group_id):
    group = Group.query.get_or_404(group_id)
    
    # Проверяем, является ли пользователь участником группы
    member = group.members.filter_by(user_id=current_user.id).first()
    if not member:
        flash('Вы не являетесь участником этой группы.')
        return redirect(url_for('main.group', id=group_id))
    
    content = request.form.get('content')
    if not content:
        flash('Содержание поста не может быть пустым.')
        return redirect(url_for('main.group', id=group_id))
    
    post = GroupPost(content=content, user_id=current_user.id, group_id=group_id)
    
    # Обработка загрузки изображения
    if 'image' in request.files:
        image_file = request.files['image']
        if image_file and image_file.filename:
            filename = secure_filename(image_file.filename)
            # Добавляем временную метку к имени файла, чтобы избежать конфликтов
            filename = f"group_post_{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
            image_path = os.path.join(current_app.root_path, 'static/images', filename)
            image_file.save(image_path)
            post.image_url = filename
    
    db.session.add(post)
    db.session.commit()
    flash('Ваш пост опубликован в группе!')
    return redirect(url_for('main.group', id=group_id))

@bp.route('/like_group_post/<int:post_id>', methods=['POST'])
@login_required
def like_group_post(post_id):
    post = GroupPost.query.get_or_404(post_id)
    like = GroupPostLike.query.filter_by(user_id=current_user.id, post_id=post.id).first()
    
    if like:
        db.session.delete(like)
        db.session.commit()
        return jsonify({'status': 'unliked', 'count': post.like_count()})
    else:
        like = GroupPostLike(user_id=current_user.id, post_id=post.id)
        db.session.add(like)
        db.session.commit()
        return jsonify({'status': 'liked', 'count': post.like_count()})

@bp.route('/delete_group_post/<int:id>')
@login_required
def delete_group_post(id):
    post = GroupPost.query.get_or_404(id)
    group_id = post.group_id
    
    # Проверяем, является ли пользователь автором поста или администратором группы
    is_admin = GroupMember.query.filter_by(user_id=current_user.id, group_id=group_id, is_admin=True).first()
    
    if post.user_id != current_user.id and not is_admin:
        flash('Вы не можете удалить этот пост.')
        return redirect(url_for('main.group', id=group_id))
    
    # Удаляем изображение, если оно есть
    if post.image_url:
        image_path = os.path.join(current_app.root_path, 'static/images', post.image_url)
        if os.path.exists(image_path):
            os.remove(image_path)
    
    db.session.delete(post)
    db.session.commit()
    flash('Пост удален.')
    return redirect(url_for('main.group', id=group_id)) 