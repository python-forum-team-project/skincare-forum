import unittest
from unittest.mock import patch
from fastapi import HTTPException

with patch.dict('os.environ', {'JWT_SECRET': 'test-secret'}):
    from routers.api import user_routers
from data.models.user import User, UserCreate, UserUpdate, LoginData, BlockUpdate, RoleUpdate


def make_user(role='user'):
    return User(user_id=4, username='test_user', role_name=role, is_blocked=False)


class RegisterUser_Should(unittest.TestCase):

    @patch('routers.api.user_routers.register')
    def test_returnsNewId_whenRegistrationSucceeds(self, mock_register):
        data = UserCreate(first_name='Test', last_name='User', email='test@example.com',
                          username='test_user', password='password123')
        mock_register.return_value = 4

        self.assertEqual({'user_id': 4}, user_routers.register_user(data))
        mock_register.assert_called_once_with(data)

    @patch('routers.api.user_routers.register')
    def test_raises409_whenUsernameOrEmailExists(self, mock_register):
        data = UserCreate(first_name='Test', last_name='User', email='test@example.com',
                          username='test_user', password='password123')
        mock_register.return_value = None

        with self.assertRaises(HTTPException) as error:
            user_routers.register_user(data)

        self.assertEqual(409, error.exception.status_code)


@patch('routers.api.user_routers.create_token')
@patch('routers.api.user_routers.login')
class LoginUser_Should(unittest.TestCase):

    def test_returnsBearerToken_whenCredentialsAreValid(self, mock_login, mock_token):
        data = LoginData(username='test_user', password='password123')
        mock_login.return_value = make_user()
        mock_token.return_value = 'test-token'

        result = user_routers.login_user(data)

        self.assertEqual({'access_token': 'test-token', 'token_type': 'bearer'}, result)
        mock_login.assert_called_once_with(data)
        mock_token.assert_called_once_with(4)

    def test_raises401_whenCredentialsAreInvalid(self, mock_login, mock_token):
        mock_login.return_value = None

        with self.assertRaises(HTTPException) as error:
            user_routers.login_user(LoginData(username='test_user', password='wrong'))

        self.assertEqual(401, error.exception.status_code)
        mock_token.assert_not_called()


class Profile_Should(unittest.TestCase):

    @patch('routers.api.user_routers.get_user_profile')
    def test_returnsCurrentProfile(self, mock_profile):
        result = user_routers.my_profile(make_user())

        self.assertEqual(mock_profile.return_value, result)
        mock_profile.assert_called_once_with(make_user())

    @patch('routers.api.user_routers.get_user_profile', return_value=None)
    def test_raises404_whenProfileDoesNotExist(self, mock_profile):
        with self.assertRaises(HTTPException) as error:
            user_routers.my_profile(make_user())

        self.assertEqual(404, error.exception.status_code)

    @patch('routers.api.user_routers.update_user_profile', return_value=True)
    def test_returnsSuccess_whenProfileIsUpdated(self, mock_update):
        data = UserUpdate(first_name='New')

        self.assertEqual({'message': 'Profile updated successfully'}, user_routers.update_profile(data, make_user()))
        mock_update.assert_called_once_with(make_user(), data)

    @patch('routers.api.user_routers.update_user_profile', return_value=False)
    def test_raises409_whenEmailIsTaken(self, mock_update):
        with self.assertRaises(HTTPException) as error:
            user_routers.update_profile(UserUpdate(email='used@example.com'), make_user())

        self.assertEqual(409, error.exception.status_code)

    @patch('routers.api.user_routers.update_user_profile', return_value=None)
    def test_raises404_whenUpdatedUserDoesNotExist(self, mock_update):
        with self.assertRaises(HTTPException) as error:
            user_routers.update_profile(UserUpdate(first_name='New'), make_user())

        self.assertEqual(404, error.exception.status_code)

    @patch('routers.api.user_routers.self_delete_user', return_value=True)
    def test_returnsNone_whenProfileIsDeactivated(self, mock_delete):
        self.assertIsNone(user_routers.delete_profile(make_user()))
        mock_delete.assert_called_once_with(make_user())

    @patch('routers.api.user_routers.self_delete_user', return_value=False)
    def test_raises409_whenProfileCannotBeDeactivated(self, mock_delete):
        with self.assertRaises(HTTPException) as error:
            user_routers.delete_profile(make_user())

        self.assertEqual(409, error.exception.status_code)


@patch('routers.api.user_routers.admin_search_users')
class AdminSearch_Should(unittest.TestCase):

    def test_passesSearchAndPagination_toService(self, mock_search):
        mock_search.return_value = []
        admin = make_user(role='admin')

        self.assertEqual([], user_routers.admin_search('Test', 10, 20, admin))
        mock_search.assert_called_once_with(admin, 'Test', 10, 20)

    def test_raises403_whenServiceRejectsUser(self, mock_search):
        mock_search.return_value = None

        with self.assertRaises(HTTPException) as error:
            user_routers.admin_search('Test', 20, 0, make_user())

        self.assertEqual(403, error.exception.status_code)


@patch('routers.api.user_routers.admin_set_blocked')
class AdminBlockUser_Should(unittest.TestCase):

    def test_returnsSuccess_whenStatusIsUpdated(self, mock_block):
        mock_block.return_value = (True, None)
        admin = make_user(role='admin')

        result = user_routers.admin_block_user(7, BlockUpdate(is_blocked=True), admin)

        self.assertEqual({'message': 'User status updated successfully'}, result)
        mock_block.assert_called_once_with(admin, 7, True)

    def test_raises403_whenUserIsNotAdmin(self, mock_block):
        mock_block.return_value = (False, 'not_admin')

        with self.assertRaises(HTTPException) as error:
            user_routers.admin_block_user(7, BlockUpdate(is_blocked=True), make_user())

        self.assertEqual(403, error.exception.status_code)

    def test_raises403_whenAdminChangesOwnStatus(self, mock_block):
        mock_block.return_value = (False, 'self_change')

        with self.assertRaises(HTTPException) as error:
            user_routers.admin_block_user(4, BlockUpdate(is_blocked=True), make_user(role='admin'))

        self.assertEqual(403, error.exception.status_code)

    def test_raises404_whenUserDoesNotExist(self, mock_block):
        mock_block.return_value = (False, 'not_found')

        with self.assertRaises(HTTPException) as error:
            user_routers.admin_block_user(99, BlockUpdate(is_blocked=True), make_user(role='admin'))

        self.assertEqual(404, error.exception.status_code)


@patch('routers.api.user_routers.admin_set_role')
class AdminChangeRole_Should(unittest.TestCase):

    def test_returnsSuccess_whenRoleIsUpdated(self, mock_role):
        mock_role.return_value = (True, None)
        admin = make_user(role='admin')

        result = user_routers.admin_change_role(7, RoleUpdate(role_name='moderator'), admin)

        self.assertEqual({'message': 'User role updated successfully'}, result)
        mock_role.assert_called_once_with(admin, 7, 'moderator')

    def test_raises403_whenUserIsNotAdmin(self, mock_role):
        mock_role.return_value = (False, 'not_admin')

        with self.assertRaises(HTTPException) as error:
            user_routers.admin_change_role(7, RoleUpdate(role_name='admin'), make_user())

        self.assertEqual(403, error.exception.status_code)

    def test_raises403_whenAdminChangesOwnRole(self, mock_role):
        mock_role.return_value = (False, 'self_change')

        with self.assertRaises(HTTPException) as error:
            user_routers.admin_change_role(4, RoleUpdate(role_name='user'), make_user(role='admin'))

        self.assertEqual(403, error.exception.status_code)

    def test_raises404_whenUserDoesNotExist(self, mock_role):
        mock_role.return_value = (False, 'not_found')

        with self.assertRaises(HTTPException) as error:
            user_routers.admin_change_role(99, RoleUpdate(role_name='user'), make_user(role='admin'))

        self.assertEqual(404, error.exception.status_code)

    def test_raises422_whenServiceRejectsRole(self, mock_role):
        mock_role.return_value = (False, 'invalid_role')

        with self.assertRaises(HTTPException) as error:
            user_routers.admin_change_role(7, RoleUpdate(role_name='user'), make_user(role='admin'))

        self.assertEqual(422, error.exception.status_code)

    def test_raises403_whenTargetIsAdmin(self, mock_role):
        mock_role.return_value = (False, 'invalid_change')

        with self.assertRaises(HTTPException) as error:
            user_routers.admin_change_role(7, RoleUpdate(role_name='user'), make_user(role='admin'))

        self.assertEqual(403, error.exception.status_code)
