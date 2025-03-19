# SocialPlus

Базовая социальная сеть на Flask с использованием SQLite, Tailwind CSS и Alpine.js.

## Функциональность

- Регистрация и авторизация пользователей
- Создание, просмотр и удаление постов
- Лайки и комментарии к постам
- Профили пользователей
- Система подписок на других пользователей
- Лента новостей с постами от подписок

## Технологии

- **Backend**: Flask, Flask-Login, Flask-SQLAlchemy
- **База данных**: SQLite
- **Frontend**: Tailwind CSS, Alpine.js
- **Шаблонизатор**: Jinja2

## Установка и запуск

1. Клонируйте репозиторий:
   ```
   git clone https://github.com/yourusername/socialplus.git
   cd socialplus
   ```

2. Создайте и активируйте виртуальное окружение:
   ```
   python -m venv venv
   source venv/bin/activate  # На Windows: venv\Scripts\activate
   ```

3. Установите зависимости:
   ```
   pip install -r requirements.txt
   ```

4. Создайте файл .env с секретным ключом:
   ```
   echo "SECRET_KEY=your-secret-key" > .env
   ```

5. Запустите приложение:
   ```
   python app.py
   ```

6. Откройте браузер и перейдите по адресу http://127.0.0.1:5000/

## Структура проекта

```
SocialPlus/
├── app/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── post.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── main.py
│   │   └── posts.py
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   ├── templates/
│   │   ├── auth/
│   │   │   ├── login.html
│   │   │   └── register.html
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── user.html
│   │   ├── post.html
│   │   └── create_post.html
│   └── __init__.py
├── app.py
├── requirements.txt
└── README.md
```

## Дальнейшее развитие

- Добавление загрузки изображений для постов и аватаров
- Реализация поиска пользователей и постов
- Добавление уведомлений
- Личные сообщения между пользователями
- Улучшение мобильной версии 