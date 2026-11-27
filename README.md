# Forum System

## Overview

Forum System is a team project developed during the Telerik Academy Alpha Python program.

We are building a skincare forum where users can discuss products, share their skincare routines and experiences, and ask questions about skin care. Registered users will be able to create topics, write replies and vote on other users' replies.

The project is in its initial development stage. We will implement the required features first and add optional features if time allows.

## Planned Features

- User registration, login and profile editing.
- Browsing, searching and sorting topics.
- Creating, editing and deleting topics and replies, based on user permissions.
- Viewing your own topics and replies.
- Liking or disliking other users' replies.
- Selecting the best reply to your topic.
- Admin tools for managing users, locking topics and deleting content.
- A home page with basic forum statistics.
- A REST API.
- Dynamic interface with CSS, Jinja2 and HTML.

## Technologies

We plan to use:

- Python and FastAPI
- MariaDB
- Pydantic
- Jinja2, HTML and CSS
- unittest and unittest.mock
- Git and GitHub

## Project Structure

| Folder | Purpose |
| --- | --- |
| `models/` | Input and output models |
| `routers/` | API endpoints and web pages |
| `services/` | Business logic and database queries |
| `data/` | Database connection and helper functions |
| `common/` | Shared helpers |
| `templates/` | HTML templates |
| `static/` | CSS and images |
| `sql/` | Database setup and sample data |
| `tests/` | Automated tests |
| `docs/` | Project documentation |

This is the planned structure and will be updated as we build the project.

## Installation and Setup

These instructions cover local installation, configuration and use on Windows with PowerShell.

### 1. Prerequisites

- A local copy of the repository, downloaded with Git clone or Download ZIP.
- Python 3.14, the version used for project development.
- An installed and running MariaDB Server. The Python `mariadb` package is a database connector, not the server itself.
- A MariaDB command-line client or SQL GUI to run the schema script.

Open PowerShell in the project root, where `main.py` is located. Replace the example path with your local path:

```powershell
Set-Location 'C:\path\to\skincare_forum'
python --version
```

### 2. Virtual Environment

If `.venv` does not exist, create it:

```powershell
python -m venv .venv
```

The commands below use the virtual environment's Python directly, so activation and changes to the PowerShell execution policy are not required. Keep an existing working `.venv` unless you need to recreate it.

### 3. Dependencies

Install the packages listed in [requirements.txt](requirements.txt):

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

| Dependency | Purpose |
| --- | --- |
| FastAPI / Uvicorn | Web application and HTTP server |
| Pydantic / email-validator | Data models and email validation |
| mariadb / python-dotenv | Database connection and `.env` configuration |
| pwdlib with Argon2 / PyJWT | Password hashing and signed tokens |
| Jinja2 / python-multipart | HTML templates and form data |
| itsdangerous | Sessions used for CSRF protection and messages |

If `mariadb` fails to install, check the error for a compatible wheel or a required MariaDB Connector/C installation, and check your Python architecture. The existing tests use `unittest` and mocks and do not require an HTTP test client.

### 4. Environment Variables

Create `.env` in the project root, next to `main.py`. This command copies [env.example](env.example) only if `.env` does not already exist:

```powershell
if (-not (Test-Path -LiteralPath '.env')) {
    Copy-Item -LiteralPath 'env.example' -Destination '.env'
}
```

Replace the placeholders with your local values:

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

Generate two different secrets locally:

```powershell
.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_hex(32)); print(secrets.token_hex(32))"
```

Use the first value for `JWT_SECRET` and the second for `SESSION_SECRET`. Keep the values between application restarts: changing them invalidates existing tokens or sessions. Do not commit `.env` or real secrets to Git. `env.example` contains example values only.

### 5. Database and Sample Data

1. Start the local MariaDB service.
2. Check the host, port and database user in `.env`.
3. Open [sql/shema_with_seed_data_v1.sql](sql/shema_with_seed_data_v1.sql) in your SQL client.
4. Review the script before running it. It starts with **DROP DATABASE IF EXISTS forum**, which deletes an existing `forum` database. Run it only for initial setup or an intentional reset of the development database. Back up any data you want to keep.
5. Run the complete script and check for SQL errors.

Alternatively, open the MariaDB CLI from the project root. Enter your password at the prompt:

```powershell
mariadb -h localhost -P 3306 -u your_database_user -p
```

Then run the following inside the MariaDB client, after reviewing the reset described above:

```sql
SOURCE sql/shema_with_seed_data_v1.sql;
```

`SOURCE` is a MariaDB client command, not a PowerShell command. Use an absolute local path to the SQL file if needed. If `mariadb` is not on `PATH`, use your SQL GUI or the full path to the installed client.

Check the database after setup:

```sql
USE forum;
SHOW TABLES;
SELECT role_id, role_name FROM roles;
SELECT COUNT(*) AS users_count FROM users;
SELECT COUNT(*) AS topics_count FROM topics;
SELECT COUNT(*) AS replies_count FROM replies;
```

The script includes 9 users, 5 topics and 17 replies. Register a new test user for your first login check. To use the Admin Panel, sign in with an existing admin account whose login credentials you know. Registration creates a `user` account.

### 6. Run the Application

From the project root, run:

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

Alternatively, use the existing entry point:

```powershell
.\.venv\Scripts\python.exe main.py
```

Use one command at a time. Press `Ctrl+C` to stop the server. `--reload` is intended for local development.

| Address | Purpose |
| --- | --- |
| [Home page](http://127.0.0.1:8000/) | HTML home page; requires a working database for statistics and topic lists |
| [Swagger UI](http://127.0.0.1:8000/docs) | Interactive API documentation |
| [ReDoc](http://127.0.0.1:8000/redoc) | Alternative API documentation |
| [Register](http://127.0.0.1:8000/register) | Account registration |
| [Login](http://127.0.0.1:8000/login) | Account login |
| [Profile](http://127.0.0.1:8000/profile) | Your profile after login |
| [Admin Panel](http://127.0.0.1:8000/admin/users) | User administration |
| [Home statistics](http://127.0.0.1:8000/stats/home) | JSON statistics endpoint |

Use either `127.0.0.1` or `localhost` consistently: cookies set for one host are not shared with the other. Open pages through FastAPI so Jinja2 can render them; opening HTML files directly will not render the templates.

### 7. PyCharm

1. Open the `skincare_forum` project root.
2. Select `.venv\Scripts\python.exe` as the project interpreter.
3. Create a Python Run Configuration with module `uvicorn` and parameters `main:app --reload`.
4. Set the working directory to the project root (`skincare_forum`).
5. The application loads `.env` through `load_dotenv()`. Keep secrets out of shared run configurations.

You can also run `main.py` with the same interpreter and working directory.

### 8. Using the Web Interface and REST API

#### Web Interface

1. Open the [home page](http://127.0.0.1:8000/).
2. Choose **Register** to create an account or **Login** if you already have one.
3. After login, open **Profile** to view or edit your details. The username cannot be changed.
4. To deactivate your account, confirm your username and password in the profile deletion form.
5. Choose **Logout** to sign out.
6. With an admin account, open **Admin Panel** to search users, make allowed role changes, and block or unblock accounts.

Web login stores a JWT in an HttpOnly cookie, which the browser sends automatically. Use the HTML forms, which include a CSRF token. Keep CSRF verification enabled during manual checks.

#### REST API with Swagger UI

1. Open [Swagger UI](http://127.0.0.1:8000/docs).
2. If needed, send `POST /users` with valid `first_name`, `last_name`, `email`, `username` and `password` values to register.
3. Send `POST /users/login` with your username and password.
4. Copy the returned `access_token`.
5. Click **Authorize** and paste the token itself, without adding a `Bearer` prefix in the Swagger field.
6. Send `GET /users/me` to check access to your profile.

Swagger bearer authentication and web cookie authentication pass the JWT in different ways. Use `/docs` to explore the other available API operations.

### 9. Troubleshooting

| Problem | Check or solution |
| --- | --- |
| `KeyError: JWT_SECRET`, `SESSION_SECRET` or `DB_NAME` | Check that `.env` exists in the project root and contains the required keys. |
| `email-validator is not installed` | Install the requirements in the selected `.venv`. |
| Form data requires python-multipart | Install `python-multipart` in the selected `.venv`. |
| Missing itsdangerous | Install `itsdangerous`, which is required by SessionMiddleware. |
| `OperationalError 2002` | Check that MariaDB is running and the configured host and port are reachable. |
| Database access denied | Check the database username, password and permissions. |
| Unknown database or table | Check that the schema has been run and `DB_NAME` is set to `forum`. |
| Static directory does not exist | Run the application from the project root. |
| CSS is missing on a nested page | Check that static links use `url_for` or `/static/...` paths. |
| Port 8000 is already in use | Stop the previous server or add `--port 8001` to the Uvicorn command. |
| A form returns 403 | Reload the page and check the session cookie and hidden `csrf_token` field. |
| A token no longer works | Check for expiration, a changed `JWT_SECRET`, or a deactivated account. |
| Admin Panel is missing after login | Check the account's actual role. |

These instructions are for local development. When deploying with HTTPS, set `secure=True` for the authentication cookie and `https_only=True` for `SessionMiddleware`. Keep tokens, passwords and other authentication data out of application logs.

## Tests

Run the automated tests from the project root:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The tests use `unittest` and `unittest.mock` to check models, services, authentication and routers without a live database.

## Showcase

Screenshots of the main pages will be added when the interface is ready.

## Database Diagram

The database diagram will be added after the schema is implemented.

## Contributors

- Sophia Sotirova
- Stoyan Mezinov
- Aleksandar Shunev
