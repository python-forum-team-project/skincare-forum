from secrets import token_urlsafe, compare_digest
from fastapi import Request, HTTPException


def csrf_context(request: Request) -> dict:
    token = request.session.get('csrf_token')

    if token is None:
        token = token_urlsafe(32)
        request.session['csrf_token'] = token

    return {'csrf_token': token}


def verify_csrf(request: Request, submitted_token: str):
    expected_token = request.session.get('csrf_token')

    if not isinstance(expected_token, str) or not compare_digest(expected_token, submitted_token):
        raise HTTPException(
            status_code=403,
            detail='Invalid CSRF token'
        )