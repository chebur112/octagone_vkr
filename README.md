# Telegram-бот для руководителя по данным 1С:УНФ

Бот принимает вопрос обычным текстом («Сколько сегодня продала точка на Партизанской?»), строит запрос на языке запросов 1С с помощью YandexGPT, выполняет его через HTTP-сервис в 1С:УНФ и отвечает коротким текстом с цифрами.

## Состав

- `app/` — приложение на Python 3.12: бот на aiogram 3 (polling), клиент HTTP-сервиса 1С на httpx, база PostgreSQL через SQLAlchemy 2 (async, asyncpg).
- `1c/` — модуль HTTP-сервиса расширения 1С: методы `/metadata`, `/lookup`, `/query`.
- `docker-compose.yml` — два контейнера: приложение и PostgreSQL 16.

## Запуск

Нужны Docker с Docker Compose и опубликованная на веб-сервере база 1С:УНФ с расширением из `1c/`.

```bash
cp .env.example .env    # заполнить поля, см. таблицу ниже
docker compose up --build
```

При первом запуске приложение создаёт таблицы и загружает каталог объектов 1С в таблицу `metadata_objects`. В логе должно появиться `Каталог 1С загружен: ... объектов` и `Start polling`.

Перезагрузить каталог после изменений в конфигурации 1С:

```bash
docker compose exec app python -m app.db.catalog
```

## Настройка `.env`

Скопируйте `.env.example` в `.env` и заполните поля.

| Переменная | Описание | Пример |
| --- | --- | --- |
| `BOT_TOKEN` | Токен бота от @BotFather | `123456:ABC-DEF...` |
| `ADMIN_IDS` | Telegram ID администраторов через запятую | `123456789` |
| `YC_FOLDER_ID` | ID каталога Yandex Cloud | `b1g...` |
| `YC_API_KEY` | API-ключ сервисного аккаунта с ролью `ai.languageModels.user` | `AQVN...` |
| `UNF_BASE_URL` | Адрес HTTP-сервиса 1С:УНФ | `http://host.docker.internal/unf/hs/bot` |
| `UNF_USER` | Пользователь 1С с правами только на чтение | `bot` |
| `UNF_PASSWORD` | Пароль пользователя; на учебной платформе 1С только пустой | (пусто) |
| `POSTGRES_DB` | Имя базы PostgreSQL | `vkr` |
| `POSTGRES_USER` | Пользователь PostgreSQL | `vkr` |
| `POSTGRES_PASSWORD` | Пароль PostgreSQL | `secret` |
| `POSTGRES_HOST` | Хост PostgreSQL (имя сервиса в docker-compose) | `db` |
| `POSTGRES_PORT` | Порт PostgreSQL | `5432` |
