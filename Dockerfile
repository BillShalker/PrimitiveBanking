# Используйте официальный образ Python как базовый
FROM python:3.12

# Установите зависимости для PostgreSQL
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

# Установите рабочую директорию в контейнере
WORKDIR /usr/src/app

# Скопируйте файлы зависимостей и установите их
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Скопируйте проект в контейнер
COPY . .

# Удалите эту команду из Dockerfile, так как она требует доступ к базе данных, который не доступен во время сборки образа
# RUN python manage.py collectstatic --no-input

# Укажите порт, на котором будет работать приложение
EXPOSE 8000

# Используйте entrypoint скрипт для выполнения начальных действий перед запуском сервера, например, для применения миграций и сбора статических файлов
COPY entrypoint.sh /usr/src/app/entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]

# Команда для запуска приложения
CMD ["gunicorn", "-b", "0.0.0.0:8000", "SimpleBanking.wsgi:application"]
