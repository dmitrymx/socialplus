import sys, os

# Добавим текущую директорию в пути
sys.path.insert(0, os.path.dirname(__file__))

# Импортируем приложение Flask
from app import create_app

# Создаем экземпляр приложения
application = create_app()

# Для совместимости с Passenger
def application(environ, start_response):
    return application.wsgi_app(environ, start_response) 