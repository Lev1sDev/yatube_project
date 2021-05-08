# Yatube - социальная сеть для публикации дневников

## Стек технологий: Python 3, Django 2.2, PostgreSQL, gunicorn, nginx, Яндекс.Облако (Ubuntu 18.04), pytest.

### Используется пагинация постов и кэширование. Реализована регистрация пользователей с верификацией данных, сменой и восстановлением пароля через почту. Написаны тесты, проверяющие работу сервиса

### Ссылка на сайт: https://www.westnet.cf/

### Запуск приложения:
``` git clone https://github.com/Lev1sDev/yatube_project.git  ``` \
```docker-compose up```

### Выполнить миграции:
```docker-compose exec web python manage.py makemigrations``` \
```docker-compose exec web python manage.py migrate --noinput```

### Создать суперпользователя:
```docker-compose exec web python manage.py createsuperuser```

### Привязать статические файлы:
```docker-compose exec web python manage.py collectstatic --no-input```

### Заполнить базу начальными данными:
```docker-compose exec web python manage.py loaddata fixtures.json```
