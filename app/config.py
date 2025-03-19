import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'default-dev-key-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Путь для загрузки файлов
    UPLOAD_FOLDER = 'app/static/images'
    
    # Настройки почты (если потребуется)
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 25))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', '').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), '../instance/social_network.db')

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///:memory:'

class ProductionConfig(Config):
    # Для MySQL на хостинге
    # Формат: mysql://username:password@localhost/database_name
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Запись логов в файл (для отладки на хостинге)
        import logging
        from logging import FileHandler
        file_handler = FileHandler('app.log')
        file_handler.setLevel(logging.WARNING)
        app.logger.addHandler(file_handler)

class InfinityFreeConfig(ProductionConfig):
    """Конфигурация для хостинга InfinityFree"""
    
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)
        
        # Настройка для работы за прокси
        from werkzeug.middleware.proxy_fix import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app)

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'infinityfree': InfinityFreeConfig,
    
    'default': DevelopmentConfig
} 