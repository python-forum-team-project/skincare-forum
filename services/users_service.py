from data.models.user import User, UserCreate, UserProfile, UserUpdate, Role, LoginData
from data.database import read_query, insert_query, update_query
from services.auth_service import hash_password, verify_password
from mariadb import IntegrityError


def get_user_by_id(user_id: int) -> User | None:
    data = read_query('''SELECT u.user_id, u.username, r.role_name, u.is_blocked
                         FROM users u JOIN roles r ON u.role_id = r.role_id
                         WHERE u.user_id = ?''',
                      (user_id, )
                      )

    if not data:
        return None

    return User.from_query_result(*data[0])


def get_user_by_username(username: str) -> User | None:
    data = read_query('''SELECT u.user_id, u.username, r.role_name, u.is_blocked
                         FROM users u JOIN roles r ON u.role_id = r.role_id
                         WHERE u.username = ?''',
                      (username, )
                      )

    if not data:
        return None

    return User.from_query_result(*data[0])


def register(new_user: UserCreate) -> int | None:
    password_hash = hash_password(new_user.password)

    try:
        user_id = insert_query(
            """
            INSERT INTO users
                (first_name, last_name, username, email, password_hash, role_id)
            VALUES (?, ?, ?, ?, ?,
                    (SELECT role_id FROM roles WHERE role_name = ?))
            """,
            (new_user.first_name, new_user.last_name, new_user.username, str(new_user.email), password_hash, Role.USER)
        )

    except IntegrityError as error:
        if error.errno == 1062:
            return None
        raise

    return user_id


def login(data: LoginData) -> User | None:
    result = read_query(""" SELECT u.user_id, u.username, r.role_name, u.is_blocked, u.password_hash 
        FROM users u JOIN roles r ON u.role_id = r.role_id WHERE u.username = ?""",
        (data.username, )
    )

    if not result:
        return None

    if result[0][3] or not verify_password(data.password, result[0][4]):
        return None

    logged_user = User.from_query_result(*result[0][:4])

    return logged_user


def get_user_profile(current_user: User) -> UserProfile | None:
    profile_data = read_query('''SELECT u.user_id, u.username, r.role_name, u.is_blocked, u.first_name, u.last_name, u.email 
                            FROM users u JOIN roles r ON u.role_id = r.role_id 
                            WHERE u.user_id = ?;''',
                         (current_user.user_id, )
                         )

    if not profile_data:
        return None

    return UserProfile.from_query_result(*profile_data[0])


def update_user_profile(current_user: User, data: UserUpdate) -> bool | None:
    user_id = current_user.user_id

    if get_user_by_id(user_id) is None:
        return None

    updates = []
    params = []

    if data.first_name is not None:
        updates.append("first_name = ?")
        params.append(data.first_name)

    if data.last_name is not None:
        updates.append("last_name = ?")
        params.append(data.last_name)

    if data.email is not None:
        updates.append("email = ?")
        params.append(str(data.email))

    if not updates:
        return True

    sql = f"UPDATE users SET {', '.join(updates)} WHERE user_id = ?"
    params.append(user_id)

    try:
        update_query(sql, tuple(params))

    except IntegrityError as error:
        if error.errno == 1062:
            return False
        raise

    return True


def self_delete_user(current_user: User) -> bool:
    result = update_query('''UPDATE users SET is_blocked = TRUE WHERE user_id = ? AND is_blocked = FALSE''',
                              (current_user.user_id, )
                              )

    is_deleted = result > 0

    return is_deleted



def admin_set_blocked(current_user: User, user_id: int, is_blocked: bool) -> tuple[bool, str | None]:
    if not current_user.is_admin():
        return False, "not_admin"

    if current_user.user_id == user_id:
        return False, "self_change"

    user = get_user_by_id(user_id)

    if user is None:
        return False, "not_found"

    if user.is_blocked == is_blocked:
        return True, None

    result = update_query("""UPDATE users SET is_blocked = ? WHERE user_id = ?""",
                          (is_blocked, user_id)
                          )

    is_updated = result > 0, None if result > 0 else "not_found"

    return is_updated



def admin_set_role(current_user: User, user_id: int, role_name: str) -> tuple[bool, str | None]:
    if not current_user.is_admin():
        return False, "not_admin"

    if current_user.user_id == user_id:
        return False, "self_change"

    if role_name not in (Role.USER, Role.ADMIN, Role.MODERATOR):
        return False, "invalid_role"

    user = get_user_by_id(user_id)

    if user is None:
        return False, "not_found"

    if user.role_name == role_name:
        return True, None

    result = update_query("""UPDATE users u JOIN roles r ON r.role_name = ? SET u.role_id = r.role_id WHERE u.user_id = ?""",
                          (role_name, user_id)
                          )

    if result == 0:
        return False, "not_found"

    return True, None


def admin_search_users(current_user: User, search: str, limit: int, offset: int) -> list[UserProfile] | None:
    if not current_user.is_admin():
        return None

    searching_data = f'%{search}%'

    results = read_query("""SELECT u.user_id, u.username, r.role_name, u.is_blocked, u.first_name, u.last_name, u.email FROM users u
                    JOIN roles r ON u.role_id = r.role_id
           WHERE u.username LIKE ? OR u.email LIKE ? OR u.first_name LIKE ? OR u.last_name LIKE ? ORDER BY u.user_id LIMIT ? OFFSET ?""",
                         (searching_data, searching_data, searching_data, searching_data, limit, offset)
                         )

    users = []
    for row in results:
        users.append(UserProfile.from_query_result(*row))

    return users


def get_all_users_count() -> int:
    result = read_query("SELECT COUNT(*) FROM users")

    return result[0][0]


def get_active_users_count() -> int:
    result = read_query("SELECT COUNT(*) FROM users WHERE is_blocked = FALSE")

    return result[0][0]