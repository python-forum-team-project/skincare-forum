import unittest
from unittest.mock import Mock, patch
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

with patch.dict('os.environ', {'JWT_SECRET': 'test-secret'}):
    from common import auth
from data.models.user import User


def make_user(role='user', is_blocked=False):
    return User(user_id=4, username='test_user', role_name=role, is_blocked=is_blocked)


@patch('common.auth.get_user_by_id')
@patch('common.auth.get_user_id_from_token')
class ResolveUser_Should(unittest.TestCase):

    def test_returnsNone_whenTokenIsMissing(self, mock_token, mock_get):
        self.assertIsNone(auth.resolve_user(None))
        mock_token.assert_not_called()
        mock_get.assert_not_called()

    def test_returnsNone_whenTokenIsInvalid(self, mock_token, mock_get):
        mock_token.return_value = None

        self.assertIsNone(auth.resolve_user('invalid-token'))
        mock_get.assert_not_called()

    def test_returnsNone_whenUserDoesNotExist(self, mock_token, mock_get):
        mock_token.return_value = 4
        mock_get.return_value = None

        self.assertIsNone(auth.resolve_user('test-token'))
        mock_get.assert_called_once_with(4)

    def test_returnsNone_whenUserIsBlocked(self, mock_token, mock_get):
        mock_token.return_value = 4
        mock_get.return_value = make_user(is_blocked=True)

        self.assertIsNone(auth.resolve_user('test-token'))

    def test_returnsCurrentUser_whenTokenAndUserAreValid(self, mock_token, mock_get):
        mock_token.return_value = 4
        mock_get.return_value = make_user()

        self.assertEqual(make_user(), auth.resolve_user('test-token'))
        mock_token.assert_called_once_with('test-token')
        mock_get.assert_called_once_with(4)


@patch('common.auth.resolve_user')
class GetCurrentUser_Should(unittest.TestCase):

    def test_raises401_whenCredentialsAreMissing(self, mock_resolve):
        with self.assertRaises(HTTPException) as error:
            auth.get_current_user(None)

        self.assertEqual(401, error.exception.status_code)
        mock_resolve.assert_not_called()

    def test_raises401_whenTokenIsRejected(self, mock_resolve):
        mock_resolve.return_value = None
        credentials = HTTPAuthorizationCredentials(scheme='Bearer', credentials='invalid')

        with self.assertRaises(HTTPException) as error:
            auth.get_current_user(credentials)

        self.assertEqual(401, error.exception.status_code)

    def test_returnsUser_whenCredentialsAreValid(self, mock_resolve):
        mock_resolve.return_value = make_user()
        credentials = HTTPAuthorizationCredentials(scheme='Bearer', credentials='test-token')

        self.assertEqual(make_user(), auth.get_current_user(credentials))
        mock_resolve.assert_called_once_with('test-token')


class GetCurrentAdmin_Should(unittest.TestCase):

    def test_returnsAdmin_whenUserIsAdmin(self):
        admin = make_user(role='admin')

        self.assertEqual(admin, auth.get_current_admin(admin))

    def test_raises403_whenUserIsNotAdmin(self):
        with self.assertRaises(HTTPException) as error:
            auth.get_current_admin(make_user())

        self.assertEqual(403, error.exception.status_code)

    def test_raises403_whenUserIsModerator(self):
        with self.assertRaises(HTTPException) as error:
            auth.get_current_admin(make_user(role='moderator'))

        self.assertEqual(403, error.exception.status_code)


@patch('common.auth.resolve_user')
class GetWebCurrentUser_Should(unittest.TestCase):

    def test_resolvesAccessToken_fromCookie(self, mock_resolve):
        request = Mock()
        request.cookies = {'access_token': 'cookie-token'}
        mock_resolve.return_value = make_user()

        self.assertEqual(make_user(), auth.get_web_current_user(request))
        mock_resolve.assert_called_once_with('cookie-token')

    def test_returnsNone_whenCookieIsMissing(self, mock_resolve):
        request = Mock()
        request.cookies = {}
        mock_resolve.return_value = None

        self.assertIsNone(auth.get_web_current_user(request))
        mock_resolve.assert_called_once_with(None)
