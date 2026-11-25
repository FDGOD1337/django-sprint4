# Блогикум. Часть 3

Учебный блог на Django с публикациями, изображениями, комментариями и профилями пользователей. В проекте используются SQLite и готовые шаблоны Практикума.

Для запуска на Windows с Python 3.12 из корня проекта:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe blogicum/manage.py migrate
.\.venv\Scripts\python.exe blogicum/manage.py runserver
```

Адрес сайта: http://127.0.0.1:8000/.

Чтобы загрузить демонстрационные записи, после миграций выполните `.\.venv\Scripts\python.exe blogicum/manage.py loaddata db.json`. Для работы через админку создайте своего пользователя командой `.\.venv\Scripts\python.exe blogicum/manage.py createsuperuser`. Для запуска проверок используйте `.\.venv\Scripts\python.exe -m pytest`.

Загруженные изображения сохраняются в `blogicum/media/`, а письма для сброса пароля — в `blogicum/sent_emails/`.
