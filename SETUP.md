# Skincare Forum — Installation & Setup Guide

Инструкции за инсталиране, конфигуриране и локално стартиране на Skincare Forum под Windows (PowerShell), както и за използване на уеб интерфейса и REST API.

## 1. Предварителни условия

- Локално копие на GitHub repository-то (изтеглено чрез Git clone или Download ZIP).
- Python. Проверената проектна среда е Python 3.14.2.
- Инсталиран и стартиран MariaDB Server. Python пакетът `mariadb` е клиентски connector, не самият сървър.
- MariaDB клиент или SQL GUI за изпълнение на schema скрипта.

Отворете PowerShell и отидете в главната папка на проекта, където се намира `main.py`. Заменете примерния път с вашия локален път:

```powershell
Set-Location 'C:\path\to\skincare_forum'
python --version
```

## 2. Виртуална среда

Ако `.venv` липсва, създайте я:

```powershell
python -m venv .venv
```

Следващите команди използват нейния Python директно и не изискват промяна на PowerShell execution policy. Не пресъздавайте съществуваща работеща `.venv` без причина.

## 3. Зависимости

Ако в repository-то има `requirements.txt`, инсталирайте зависимостите чрез:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Ако файлът липсва, инсталирайте необходимите пакети директно:

```powershell
.\.venv\Scripts\python.exe -m pip install fastapi uvicorn pydantic mariadb python-dotenv "pwdlib[argon2]" PyJWT email-validator Jinja2 python-multipart itsdangerous
```

| Зависимост | За какво е |
| --- | --- |
| FastAPI / Uvicorn | Приложение и HTTP server |
| Pydantic / email-validator | Модели и EmailStr |
| mariadb / python-dotenv | DB връзка и `.env` |
| pwdlib с Argon2 / PyJWT | Пароли и подписани токени |
| Jinja2 / python-multipart | HTML шаблони и Form данни |
| itsdangerous | SessionMiddleware, използван за CSRF и съобщения |

Ако `mariadb` не се инсталира, проверете съобщението за съвместим wheel/нужен MariaDB Connector/C и архитектурата на Python. Не заменяйте DB библиотеката без съгласуване. `httpx` не е необходим за стартиране; добавя се само ако използвате TestClient тестове.

## 4. `.env`

В корена до `main.py` създайте `.env`. Следващата команда копира примерния файл само ако `.env` още липсва:

```powershell
if (-not (Test-Path -LiteralPath '.env')) {
    Copy-Item -LiteralPath 'env.example' -Destination '.env'
}
```

Примерно съдържание (заменете placeholders с вашите локални стойности):

```dotenv
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=forum

JWT_SECRET=replace_with_first_generated_value
JWT_EXPIRE_MINUTES=30
SESSION_SECRET=replace_with_second_generated_value
```

Генерирайте две различни тайни локално:

```powershell
.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_hex(32)); print(secrets.token_hex(32))"
```

Първият ред поставете в JWT_SECRET, втория в SESSION_SECRET. Не публикувайте истинските стойности или `.env` в Git. `env.example` съдържа само примери. Не сменяйте тайните при всяко стартиране: това обезсилва токени/сесии.

## 5. MariaDB и schema/seed

1. Стартирайте локалния MariaDB service.
2. Проверете host/port и потребителя от `.env`.
3. Отворете `sql/shema_with_seed_data_v1.sql` в SQL клиента.
4. Прегледайте първите редове: скриптът съдържа **DROP DATABASE IF EXISTS forum**. Изпълнявайте го само при първоначална настройка или съзнателен reset на development база.
5. При нужда запазете данните преди reset. Изпълнете целия скрипт и проверете всички SQL грешки.

Алтернатива с MariaDB CLI (въвеждате паролата в prompt-а, не в командата):

```powershell
mariadb -h localhost -P 3306 -u your_database_user -p
```

После вътре в MariaDB клиента, само ако сте избрали да reset-нете базата:

```sql
SOURCE sql/shema_with_seed_data_v1.sql;
```

Това е команда в MariaDB клиента, стартиран от главната папка на проекта, а не PowerShell команда. При нужда използвайте абсолютния локален път до SQL файла. Ако `mariadb` не е в PATH, използвайте GUI или действителния път до инсталирания клиент.

Проверки след setup:

```sql
USE forum;
SHOW TABLES;
SELECT role_id, role_name FROM roles;
SELECT COUNT(*) AS users_count FROM users;
SELECT COUNT(*) AS topics_count FROM topics;
SELECT COUNT(*) AS replies_count FROM replies;
```

Скриптът съдържа примерни данни (9 потребители, 5 теми и 17 отговора). За първа проверка регистрирайте нов тестов потребител. За Admin Panel използвайте съществуващ admin акаунт с известни данни за вход. Регистрацията създава акаунт с роля `user`, а не `admin`.

## 6. Стартиране

От главната папка:

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

Съществува и main guard, затова може алтернативно:

```powershell
.\.venv\Scripts\python.exe main.py
```

Не стартирайте и двете едновременно. Спиране: Ctrl+C. `--reload` е за локална разработка.

| Адрес | Текущо предназначение |
| --- | --- |
| `http://127.0.0.1:8000/` | Начална HTML страница; изисква работеща DB за статистиката |
| `http://127.0.0.1:8000/docs` | Swagger API документация |
| `http://127.0.0.1:8000/redoc` | Алтернативна API документация |
| `http://127.0.0.1:8000/register` | HTML регистрация |
| `http://127.0.0.1:8000/login` | HTML вход |
| `http://127.0.0.1:8000/profile` | Собствен профил след вход |
| `http://127.0.0.1:8000/admin/users` | Admin panel |
| `http://127.0.0.1:8000/home/stats` | Текущ JSON endpoint за статистика |

Използвайте последователно `127.0.0.1` или `localhost`: cookies за единия host не се прехвърлят към другия. Не отваряйте HTML файловете чрез двоен клик — те трябва да се обработят от Jinja2 през FastAPI.

## 7. PyCharm

1. Отворете главната папка `skincare_forum`.
2. Изберете interpreter `.venv\Scripts\python.exe`.
3. Направете Python Run Configuration: module `uvicorn`, parameters `main:app --reload`.
4. Working directory: главната папка на проекта (`skincare_forum`).
5. `.env` се зарежда от `load_dotenv()`. Не поставяйте тайните в споделена run configuration.

Алтернатива: run на `main.py` със същия interpreter и working directory.

## 8. Използване на Web интерфейса и REST API

### Web интерфейс

1. Отворете [началната страница](http://127.0.0.1:8000/).
2. Изберете **Register**, за да създадете акаунт, или **Login**, ако вече имате такъв.
3. След вход отворете **Profile**, за да видите и редактирате данните си. Username не може да се променя.
4. При необходимост можете да деактивирате собствения си профил, като потвърдите username и парола.
5. Изберете **Logout**, за да излезете от акаунта си.
6. С администраторски акаунт отворете **Admin Panel**, за да търсите потребители, променяте разрешените роли и блокирате или отблокирате акаунти.

Web входът използва JWT в HttpOnly cookie. Браузърът изпраща cookie автоматично. Използвайте нормалните HTML форми, които включват CSRF токен; не изключвайте `verify_csrf()` при ръчни проверки.

### REST API (Swagger UI)

1. Отворете [Swagger UI](http://127.0.0.1:8000/docs).
2. Изпратете `POST /users` с валидни `first_name`, `last_name`, `email`, `username` и `password` (ако още нямате акаунт).
3. Изпратете `POST /users/login` с username и password.
4. Копирайте получения `access_token`.
5. Натиснете **Authorize** и въведете самия токен, без допълнителен префикс `Bearer` в полето на Swagger.
6. Изпратете `GET /users/me`, за да проверите достъпа до собствения профил.

Bearer authentication в Swagger и cookie authentication в Web интерфейса са различни начини за предаване на JWT. За останалите налични API операции използвайте автоматично генерираната документация в `/docs`.

## 9. Тестове

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Изпълнете командата от главната папка на проекта, за да стартирате наличните автоматизирани тестове.

## 10. Чести проблеми

| Симптом | Проверка/решение |
| --- | --- |
| `KeyError: JWT_SECRET` / `SESSION_SECRET` / `DB_NAME` | `.env` в корена и всички необходими ключове |
| `email-validator is not installed` | Инсталирайте email-validator в избраната `.venv` |
| Form data requires python-multipart | Инсталирайте python-multipart |
| Липсва itsdangerous | Нужен е за SessionMiddleware |
| `OperationalError 2002` | Стартиран MariaDB service, правилни host/port и достъп от средата |
| Access denied към DB | Проверете DB потребител, парола и права |
| Unknown database/table | Изпълнена ли е схемата и DB_NAME=forum ли е |
| Static directory does not exist | Стартирате от грешна working directory |
| CSS липсва само на вложена страница | Заменете относителните static URL с url_for или `/static/...` |
| Port 8000 е зает | Спрете предишния процес или използвайте `--port 8001` |
| 403 при форма | Заредете страницата наново; проверете session cookie и hidden csrf_token |
| Токенът вече не работи | Изтекъл срок, променен JWT_SECRET или деактивиран user |
| Няма бутон за admin след вход | Акаунтът е user; проверете действителната роля |

> **Важно:** Тези инструкции са за локална разработка. При публикуване с HTTPS включете `secure=True` за authentication cookie и `https_only=True` за `SessionMiddleware`. Не записвайте токени, пароли или други authentication данни в логовете.
