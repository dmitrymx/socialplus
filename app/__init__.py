# Пакет приложения SocialPlus 

import os
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect, generate_csrf
import emoji
from app.config import config
from logging.handlers import RotatingFileHandler
import logging

# Инициализация расширений
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Пожалуйста, войдите, чтобы получить доступ к этой странице.'
csrf = CSRFProtect()

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')
    
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Создаем директории если их нет
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    try:
        os.makedirs(os.path.join(app.root_path, 'static/images'))
    except OSError:
        pass

    # Инициализация расширений
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Настройка CSRF для AJAX-запросов
    @app.after_request
    def add_csrf_header(response):
        response.headers.set('X-CSRFToken', generate_csrf())
        return response
    
    # Добавляем фильтр для эмодзи в Jinja2
    app.jinja_env.filters['emoji'] = lambda text: emoji.emojize(text, language='alias')

    # Регистрация маршрутов
    from app.routes import auth, main, posts, messages
    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(posts.bp, url_prefix='/posts')
    app.register_blueprint(messages.bp)
    
    from app.routes.notifications import notifications as notifications_blueprint
    app.register_blueprint(notifications_blueprint)
    
    # Создаем шаблоны для страниц футера, если они не существуют
    create_footer_templates(app)
    
    # Загрузчик пользователя для Flask-Login
    from app.models.user import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Настройка логирования
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/social_network.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('SocialPlus запущена')
    
    return app 

def create_footer_templates(app):
    """Создает базовые шаблоны для страниц футера, если они не существуют"""
    footer_pages = {
        'about.html': 'О нас',
        'contact.html': 'Контакты',
        'privacy.html': 'Политика конфиденциальности',
        'terms.html': 'Условия использования',
        'help.html': 'Помощь',
        'careers.html': 'Карьера',
        'developers.html': 'Разработчикам'
    }
    
    # Создаем директорию для шаблонов, если она не существует
    templates_dir = app.template_folder
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
    
    for template_name, title in footer_pages.items():
        template_path = os.path.join(templates_dir, template_name)
        if not os.path.exists(template_path):
            with open(template_path, 'w') as f:
                content = '{% extends "base.html" %}\n\n'
                content += '{% block title %}' + title + ' - SocialPlus{% endblock %}\n\n'
                content += '{% block content %}\n'
                content += '<div class="max-w-4xl mx-auto">\n'
                content += '    <div class="bg-white rounded-xl shadow-lg overflow-hidden mb-6 hover-lift glass-effect">\n'
                content += '        <div class="bg-gradient-to-r from-blue-500 to-purple-600 p-6 text-white animate-gradient">\n'
                content += '            <h1 class="text-2xl font-bold">' + title + '</h1>\n'
                content += '        </div>\n'
                content += '        <div class="p-6">\n'
                content += '            <p class="text-gray-700 mb-4">Страница находится в разработке.</p>\n'
                content += '            <p class="text-gray-700">Скоро здесь появится информация.</p>\n'
                content += '        </div>\n'
                content += '    </div>\n'
                content += '</div>\n'
                content += '{% endblock %}\n'
                f.write(content) 