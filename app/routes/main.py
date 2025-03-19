from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import current_user, login_required
from app import db
from app.models.user import User
from app.models.post import Post, Group, GroupMember, GroupPost
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, URLField, FileField
from wtforms.validators import DataRequired, Length, ValidationError, Optional, URL, Email
from werkzeug.utils import secure_filename
import os

bp = Blueprint('main', __name__)

class EditProfileForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    bio = TextAreaField('О себе', validators=[Length(max=140)])
    avatar = FileField('Изображение профиля')
    facebook_url = StringField('Facebook', validators=[Length(max=200)])
    twitter_url = StringField('Twitter', validators=[Length(max=200)])
    instagram_url = StringField('Instagram', validators=[Length(max=200)])
    linkedin_url = StringField('LinkedIn', validators=[Length(max=200)])
    github_url = StringField('GitHub', validators=[Length(max=200)])
    submit = SubmitField('Сохранить')
    
    def __init__(self, original_username, original_email, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email
    
    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError('Это имя пользователя уже занято. Пожалуйста, выберите другое.')
    
    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user is not None:
                raise ValidationError('Этот email уже зарегистрирован. Пожалуйста, используйте другой.')

class CreateGroupForm(FlaskForm):
    name = StringField('Название группы', validators=[DataRequired(), Length(min=3, max=100)])
    description = TextAreaField('Описание', validators=[Length(max=500)])
    avatar = FileField('Изображение группы')
    submit = SubmitField('Создать группу')
    
    def validate_name(self, name):
        group = Group.query.filter_by(name=name.data).first()
        if group is not None:
            raise ValidationError('Группа с таким названием уже существует. Пожалуйста, выберите другое название.')

@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@bp.route('/')
@bp.route('/index')
def index():
    if current_user.is_authenticated:
        posts = current_user.followed_posts().all()
        if not posts:
            posts = Post.query.order_by(Post.timestamp.desc()).all()
    else:
        posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html', title='Главная', posts=posts)

@bp.route('/explore')
def explore():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    users = User.query.all()
    return render_template('explore.html', title='Исследовать', posts=posts, users=users)

@bp.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user.html', user=user, posts=posts)

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username, current_user.email)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.bio = form.bio.data
        current_user.facebook_url = form.facebook_url.data
        current_user.twitter_url = form.twitter_url.data
        current_user.instagram_url = form.instagram_url.data
        current_user.linkedin_url = form.linkedin_url.data
        current_user.github_url = form.github_url.data
        
        # Обработка загрузки аватара
        if form.avatar.data:
            avatar_file = form.avatar.data
            if avatar_file and avatar_file.filename:
                filename = secure_filename(avatar_file.filename)
                # Добавляем временную метку к имени файла, чтобы избежать конфликтов
                filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                avatar_path = os.path.join(current_app.root_path, 'static/images', filename)
                avatar_file.save(avatar_path)
                current_user.avatar_url = filename
        
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        flash('Ваш профиль обновлен!')
        return redirect(url_for('main.user', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.bio.data = current_user.bio
        form.facebook_url.data = current_user.facebook_url
        form.twitter_url.data = current_user.twitter_url
        form.instagram_url.data = current_user.instagram_url
        form.linkedin_url.data = current_user.linkedin_url
        form.github_url.data = current_user.github_url
    return render_template('edit_profile.html', title='Редактировать профиль', form=form)

@bp.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(f'Пользователь {username} не найден.')
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('Вы не можете подписаться на себя!')
        return redirect(url_for('main.user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(f'Вы подписались на {username}!')
    return redirect(url_for('main.user', username=username))

@bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(f'Пользователь {username} не найден.')
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('Вы не можете отписаться от себя!')
        return redirect(url_for('main.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(f'Вы отписались от {username}.')
    return redirect(url_for('main.user', username=username))

@bp.route('/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return render_template('search.html', title='Поиск', users=[], posts=[], query='')
    
    users = User.query.filter(User.username.ilike(f'%{query}%')).all()
    posts = Post.query.filter(Post.content.ilike(f'%{query}%')).order_by(Post.timestamp.desc()).all()
    
    return render_template('search.html', title='Поиск', users=users, posts=posts, query=query)

# Страницы футера
@bp.route('/about')
def about():
    return render_template('about.html', title='О нас')

@bp.route('/contact')
def contact():
    return render_template('contact.html', title='Контакты')

@bp.route('/privacy')
def privacy():
    return render_template('privacy.html', title='Политика конфиденциальности')

@bp.route('/terms')
def terms():
    return render_template('terms.html', title='Условия использования')

@bp.route('/help')
def help():
    return render_template('help.html', title='Помощь')

@bp.route('/careers')
def careers():
    return render_template('careers.html', title='Карьера')

@bp.route('/developers')
def developers():
    return render_template('developers.html', title='Разработчикам')

# Маршруты для групп
@bp.route('/groups')
def groups():
    groups = Group.query.order_by(Group.created_at.desc()).all()
    return render_template('groups.html', title='Группы', groups=groups)

@bp.route('/create_group', methods=['GET', 'POST'])
@login_required
def create_group():
    form = CreateGroupForm()
    if form.validate_on_submit():
        group = Group(name=form.name.data, description=form.description.data, creator_id=current_user.id)
        
        # Обработка загрузки аватара группы
        if form.avatar.data:
            avatar_file = form.avatar.data
            if avatar_file and avatar_file.filename:
                filename = secure_filename(avatar_file.filename)
                # Добавляем временную метку к имени файла, чтобы избежать конфликтов
                filename = f"group_{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                avatar_path = os.path.join(current_app.root_path, 'static/images', filename)
                avatar_file.save(avatar_path)
                group.avatar_url = filename
        
        db.session.add(group)
        db.session.commit()
        
        # Создатель группы автоматически становится её администратором
        member = GroupMember(user_id=current_user.id, group_id=group.id, is_admin=True)
        db.session.add(member)
        db.session.commit()
        
        flash('Группа успешно создана!')
        return redirect(url_for('main.group', id=group.id))
    
    return render_template('create_group.html', title='Создать группу', form=form)

@bp.route('/group/<int:id>')
def group(id):
    group = Group.query.get_or_404(id)
    posts = GroupPost.query.filter_by(group_id=group.id).order_by(GroupPost.timestamp.desc()).all()
    is_member = False
    is_admin = False
    
    if current_user.is_authenticated:
        member = GroupMember.query.filter_by(user_id=current_user.id, group_id=group.id).first()
        if member:
            is_member = True
            is_admin = member.is_admin
    
    return render_template('group.html', title=group.name, group=group, posts=posts, 
                           is_member=is_member, is_admin=is_admin)

@bp.route('/join_group/<int:id>')
@login_required
def join_group(id):
    group = Group.query.get_or_404(id)
    
    # Проверяем, не является ли пользователь уже участником группы
    member = GroupMember.query.filter_by(user_id=current_user.id, group_id=group.id).first()
    if member:
        flash('Вы уже являетесь участником этой группы.')
        return redirect(url_for('main.group', id=group.id))
    
    # Добавляем пользователя в группу
    member = GroupMember(user_id=current_user.id, group_id=group.id)
    db.session.add(member)
    db.session.commit()
    
    flash(f'Вы присоединились к группе {group.name}!')
    return redirect(url_for('main.group', id=group.id))

@bp.route('/leave_group/<int:id>')
@login_required
def leave_group(id):
    group = Group.query.get_or_404(id)
    
    # Проверяем, является ли пользователь участником группы
    member = GroupMember.query.filter_by(user_id=current_user.id, group_id=group.id).first()
    if not member:
        flash('Вы не являетесь участником этой группы.')
        return redirect(url_for('main.group', id=group.id))
    
    # Проверяем, не является ли пользователь единственным администратором
    if member.is_admin:
        admin_count = GroupMember.query.filter_by(group_id=group.id, is_admin=True).count()
        if admin_count == 1:
            flash('Вы не можете покинуть группу, так как вы единственный администратор.')
            return redirect(url_for('main.group', id=group.id))
    
    # Удаляем пользователя из группы
    db.session.delete(member)
    db.session.commit()
    
    flash(f'Вы покинули группу {group.name}.')
    return redirect(url_for('main.groups')) 