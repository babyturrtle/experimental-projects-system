# Управление базой данных экспериментальных проектов

###### Выполнили: Пантелей А. С., Кондеев П. Ю.

## Запуск приложения:

### 1. Переменные окружения

Необходимо заменить значения в файле **.env** на необходимые:

* `FLASK_APP`: Входная точка приложения; должно быть `wsgi.py`.
* `FLASK_ENV`: Окружение, в котором работает приложение; либо `development` либо `production`.
* `SECRET_KEY`: Случайчным образом сгенерированная строка символов для кодирования данных приложения.
* `SQLALCHEMY_DATABASE_URI`: URI соединение SQLAlchemy с базой данных SQL (MySQL).

### 2. Установка

```shell
$ git clone https://github.com/babyturrtle/practice.git
$ cd practice
$ make deploy
``` 

### 3. Создание базы данных SQL

- Зайдите в MySQL сервер и создайте базу данных

```shell
mysql -u root -p
CREATE DATABASE experimental_projects CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
\q
```

- Создайте необходимые таблицы из моделей

```shell
python models.py shell
from models import db
db.create_all()
```