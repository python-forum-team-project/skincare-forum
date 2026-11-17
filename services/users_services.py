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


def get_user_profile(user_id: int) -> UserProfile | None:
    profile_data = read_query('''SELECT u.user_id, u.username, r.role_name, u.is_blocked, u.first_name, u.last_name, u.email 
                            FROM users u JOIN roles r ON u.role_id = r.role_id 
                            WHERE u.user_id = ?;''',
                         (user_id, )
                         )

    if not profile_data:
        return None

    return UserProfile.from_query_result(*profile_data[0])

def update_user_profile(user_id: int, data: UserUpdate) -> bool | None:
    pass