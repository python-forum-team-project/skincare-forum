from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone
from os import environ
import jwt
from jwt.exceptions import InvalidTokenError
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = environ["JWT_SECRET"]
ALGORITHM = "HS256"
EXPIRE_MINUTES = int(environ.get("JWT_EXPIRE_MINUTES", "30"))

password_hasher = PasswordHash.recommended()

def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return password_hasher.verify(password, password_hash)


def create_token(user_id: int) -> str:
    token_expires_at = datetime.now(timezone.utc) + timedelta(minutes=EXPIRE_MINUTES)
    payload = {
        'sub': str(user_id),
        'exp': token_expires_at
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_user_id_from_token(token: str) -> int | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={'require': ['sub', 'exp']})
        user_id = int(payload['sub'])

        if user_id < 1:
            return None

        return user_id

    except (InvalidTokenError, ValueError, TypeError):
        return None