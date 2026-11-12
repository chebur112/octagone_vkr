# Telegram-бот для руководителя по данным 1С:УНФ

Бот принимает вопрос обычным текстом («Сколько сегодня продала точка на Партизанской?»), строит запрос на языке запросов 1С с помощью YandexGPT, выполняет его через HTTP-сервис в 1С:УНФ и отвечает коротким текстом с цифрами.

## Настройка `.env`

Скопируйте `.env.example` в `.env` и заполните поля.

| Переменная | Описание | Пример |
| --- | --- | --- |
| `BOT_TOKEN` | Токен бота от @BotFather | `123456:ABC-DEF...` |
| `ADMIN_IDS` | Telegram ID администраторов через запятую | `123456789` |
| `YC_FOLDER_ID` | ID каталога Yandex Cloud | `b1g...` |
| `YC_API_KEY` | API-ключ сервисного аккаунта с ролью `ai.languageModels.user` | `AQVN...` |
| `ONEC_BASE_URL` | Адрес HTTP-сервиса 1С | `http://host.docker.internal/unf/hs/bot` |
| `ONEC_USER` | Пользователь 1С с правами только на чтение | `bot` |
| `ONEC_PASSWORD` | Пароль этого пользователя | `secret` |
| `POSTGRES_DB` | Имя базы PostgreSQL | `vkr` |
| `POSTGRES_USER` | Пользователь PostgreSQL | `vkr` |
| `POSTGRES_PASSWORD` | Пароль PostgreSQL | `secret` |
| `POSTGRES_HOST` | Хост PostgreSQL (имя сервиса в docker-compose) | `db` |
| `POSTGRES_PORT` | Порт PostgreSQL | `5432` |
