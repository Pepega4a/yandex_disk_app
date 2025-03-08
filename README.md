# Yandex Disk API Django App

## Описание

Django-приложение для работы с публичными ссылками Яндекс.Диска. Позволяет просматривать файлы и загружать их через веб-интерфейс.

## Требования

- Python 3.10+
- Redis (для кэширования)
- Docker & Docker Compose (опционально)

---

## Установка и запуск (локально)

### Установка зависимостей

```bash
pip install -r requirements.txt
```

### Запуск сервера Django

```bash
python manage.py migrate
python manage.py runserver
```

Приложение будет доступно по адресу: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## Запуск через Docker

### Сборка и запуск контейнеров

```bash
docker-compose build
docker-compose up -d
```

Приложение будет доступно по адресу: [http://127.0.0.1:8000](http://127.0.0.1:8000)

### Остановка контейнеров

```bash
docker-compose down
```

---

## Структура проекта

```
.
├── app/                # Основное Django-приложение
├── disk/               # Логика работы с API Яндекс.Диска
├── config/             # Настройки Django
├── templates/          # HTML-шаблоны
├── static/             # Статические файлы
├── Dockerfile          # Инструкция для сборки Docker-образа
├── docker-compose.yml  # Конфигурация Docker
├── requirements.txt    # Зависимости проекта
└── README.md           # Документация проекта
```

---

## Кэширование (Redis)

Приложение использует Redis для кэширования списка файлов, что ускоряет повторные запросы и снижает нагрузку на API.

Настройки Redis в `settings.py`:

```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'KEY_PREFIX': 'cache_',
            'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
        }
    }
}
CACHE_TTL = 300  # 5 минут
```

Django-Redis не отображает ключи в `redis-cli keys *`, так как использует внутренний механизм хранения. Для проверки используйте:

```bash
docker exec -it redis_cache redis-cli SCAN 0 MATCH cache_* COUNT 100
```

Если `SCAN` ничего не показывает, но запросы выполняются быстрее – значит, кэш работает.

---

## Полезные команды

### Проверить состояние контейнеров

```bash
docker-compose ps
```

### Пересобрать контейнеры

```bash
docker-compose down -v
docker-compose up --build -d
```

### Войти в Django Shell внутри контейнера

```bash
docker exec -it django_app python manage.py shell
```

### Очистить кэш Redis

```bash
docker exec -it redis_cache redis-cli FLUSHALL
```