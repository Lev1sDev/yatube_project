# Yatube - социальная сеть для публикации дневников

## Стек технологий: Python 3, Django 2.2, PostgreSQL, gunicorn, nginx, Яндекс.Облако (Ubuntu 18.04), pytest.

### Используется пагинация постов и кэширование. Реализована регистрация пользователей с верификацией данных, сменой и восстановлением пароля через почту. Написаны тесты, проверяющие работу сервиса

### Ссылка на сайт: https://www.westnet.cf/

### Установка приложения:
```git clone https://github.com/Lev1sDev/yatube_project.git```
```python3 -m venv venv```
```source venv/bin/activate```
```pip install -r requirements.txt```

### Выполнить миграции
```python3 manage.py makemigrations```
```python3 manage.py migrate```

### Создать суперпользователя и заполнить базу начальными данными
```python3 manage.py createsuperuser```
```python3 manage.py loaddata dump.json```

### Запуск приложения
```python3 manage.py runserver```
