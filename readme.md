# TeamFinder

Платформа для поиска участников в pet-проекты. Реализован **Вариант 1** — «Избранное» и фильтрация пользователей.

**Автор:** Никита Филиппов — [github.com/nekitgo](https://github.com/nekitgo)

## Стек

- **Backend**: Django 5.2, PostgreSQL 16
- **Frontend**: HTML-шаблоны `templates_var1/` + статика из `static/`

---

## Инструкция для ревьюера

### Способ 1: Docker Compose (рекомендуется)

1. Скопируйте `.env_example` в `.env`:
   ```bash
   cp .env_example .env
   ```

2. Запустите контейнеры (PostgreSQL + Django):
   ```bash
   docker-compose up -d
   ```
   При первом запуске образ Django соберётся автоматически.
   Миграции и сборка статики выполняются автоматически при старте контейнера.

3. Загрузите тестовые данные:
   ```bash
   docker-compose exec web python manage.py seed_data
   ```

4. Откройте http://localhost:8000

---

### Способ 2: Локальный запуск

**Требования:** Python 3.12+, PostgreSQL (или Docker для БД)

1. Создайте и активируйте виртуальное окружение:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

3. Создайте `.env` (пример в `.env_example`):
   ```bash
   cp .env_example .env
   ```
   Укажите параметры вашего PostgreSQL. Если используете Docker:
   ```bash
   docker-compose up -d db
   ```
   База будет на `localhost:5436`.

4. Примените миграции:
   ```bash
   python manage.py migrate
   ```

5. Загрузите тестовые данные:
   ```bash
   python manage.py seed_data
   ```

6. Запустите сервер:
   ```bash
   python manage.py runserver
   ```

Откройте http://localhost:8000

---

## Тестовые аккаунты

| Email | Пароль | Роль |
|-------|--------|------|
| admin@teamfinder.ru | adminpass123 | Администратор |
| maria@yandex.ru | password | Пользователь |
| alex@gmail.com | password123 | Пользователь |
| anna@mail.ru | password123 | Пользователь |
| ivan@yandex.ru | password123 | Пользователь |

Каждый пользователь имеет как минимум 2 проекта. Между пользователями настроено несколько участий и избранных проектов.

---

## Запуск автотестов

```bash
# Убедитесь, что у пользователя БД есть права CREATEDB:
# docker exec <postgres_container> psql -U <superuser> -c "ALTER USER team_finder CREATEDB;"

python manage.py test users projects
```

---

## Структура проекта

```
team-finder-ad/
├── team_finder/         # Настройки Django
├── users/               # Пользователи: модель, формы, вьюшки
│   └── management/commands/seed_data.py
├── projects/            # Проекты: модель, формы, вьюшки
├── templates_var1/      # HTML-шаблоны (Вариант 1)
├── static/              # CSS, JS, шрифты, изображения
├── media/               # Загруженные файлы
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## Реализованная функциональность

### Страницы
- `/` — редирект на главную
- `/projects/list/` — список актуальных проектов с пагинацией (12/стр.)
- `/projects/<id>/` — страница проекта
- `/projects/create-project/` — создание проекта
- `/projects/<id>/edit/` — редактирование проекта
- `/projects/favorites/` — избранные проекты (только для авторизованных)
- `/users/list/` — список пользователей с пагинацией и фильтрацией
- `/users/<id>/` — публичный профиль пользователя
- `/users/register/` — регистрация
- `/users/login/` — вход
- `/users/logout/` — выход
- `/users/edit-profile/` — редактирование профиля
- `/users/change-password/` — смена пароля
- `/admin/` — административная панель

### API-эндпоинты (POST)
- `/projects/<id>/toggle-favorite/` — добавить/убрать из избранного
- `/projects/<id>/complete/` — завершить проект
- `/projects/<id>/toggle-participate/` — присоединиться/выйти из проекта

### Фильтрация пользователей (Вариант 1)
- `?filter=owners-of-favorite-projects` — авторы избранных проектов
- `?filter=owners-of-participating-projects` — авторы проектов, в которых я участвую
- `?filter=interested-in-my-projects` — пользователи, которым нравятся мои проекты
- `?filter=participants-of-my-projects` — участники моих проектов
