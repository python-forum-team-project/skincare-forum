import unittest
from unittest.mock import patch
from mariadb import IntegrityError

with patch.dict('os.environ', {'JWT_SECRET': 'test-secret'}):
    from services import users_service
from data.models.user import User, UserCreate, UserProfile, UserUpdate, LoginData


USER_ROW = (4, 'test_user', 'user', False)
PROFILE_ROW = (*USER_ROW, 'Test', 'User', 'test@example.com')


def make_user(user_id=4, role='user', is_blocked=False):
    return User(user_id=user_id, username='test_user', role_name=role, is_blocked=is_blocked)


def make_user_create():
    return UserCreate(first_name='Test', last_name='User', email='test@example.com',
                      username='test_user', password='password123')


@patch('services.users_service.read_query')
class GetUser_Should(unittest.TestCase):

    def test_returnsUser_whenIdExists(self, mock_read):
        mock_read.return_value = [USER_ROW]

        result = users_service.get_user_by_id(4)

        self.assertEqual(User.from_query_result(*USER_ROW), result)
        self.assertEqual((4,), mock_read.call_args[0][1])

    def test_returnsNone_whenIdDoesNotExist(self, mock_read):
        mock_read.return_value = []

        self.assertIsNone(users_service.get_user_by_id(99))

    def test_returnsUser_whenUsernameExists(self, mock_read):
        mock_read.return_value = [USER_ROW]

        result = users_service.get_user_by_username('test_user')

        self.assertEqual(User.from_query_result(*USER_ROW), result)
        self.assertEqual(('test_user',), mock_read.call_args[0][1])

    def test_returnsNone_whenUsernameDoesNotExist(self, mock_read):
        mock_read.return_value = []

        self.assertIsNone(users_service.get_user_by_username('unknown'))

    def test_returnsProfile_whenUserExists(self, mock_read):
        mock_read.return_value = [PROFILE_ROW]

        result = users_service.get_user_profile(make_user())

        self.assertEqual(UserProfile.from_query_result(*PROFILE_ROW), result)
        self.assertEqual((4,), mock_read.call_args[0][1])

    def test_returnsNone_whenProfileDoesNotExist(self, mock_read):
        mock_read.return_value = []

        self.assertIsNone(users_service.get_user_profile(make_user()))


@patch('services.users_service.insert_query')
@patch('services.users_service.hash_password')
class Register_Should(unittest.TestCase):

    def test_returnsNewId_andSavesHashedPassword(self, mock_hash, mock_insert):
        mock_hash.return_value = 'hashed-password'
        mock_insert.return_value = 7
        new_user = make_user_create()

        result = users_service.register(new_user)

        self.assertEqual(7, result)
        mock_hash.assert_called_once_with('password123')
        self.assertEqual(('Test', 'User', 'test_user', 'test@example.com', 'hashed-password', 'user'),
                         mock_insert.call_args[0][1])

    def test_returnsNone_whenUsernameOrEmailAlreadyExists(self, mock_hash, mock_insert):
        error = IntegrityError('Duplicate entry')
        error.errno = 1062
        mock_insert.side_effect = error

        self.assertIsNone(users_service.register(make_user_create()))

    def test_raisesError_whenDatabaseErrorIsNotDuplicate(self, mock_hash, mock_insert):
        error = IntegrityError('Foreign key error')
        error.errno = 1452
        mock_insert.side_effect = error

        with self.assertRaises(IntegrityError):
            users_service.register(make_user_create())


@patch('services.users_service.verify_password')
@patch('services.users_service.read_query')
class Login_Should(unittest.TestCase):

    def test_returnsUser_whenCredentialsAreValid(self, mock_read, mock_verify):
        mock_read.return_value = [(*USER_ROW, 'hashed-password')]
        mock_verify.return_value = True

        result = users_service.login(LoginData(username='test_user', password='password123'))

        self.assertEqual(make_user(), result)
        mock_verify.assert_called_once_with('password123', 'hashed-password')
        self.assertEqual(('test_user',), mock_read.call_args[0][1])

    def test_returnsNone_whenUsernameDoesNotExist(self, mock_read, mock_verify):
        mock_read.return_value = []

        result = users_service.login(LoginData(username='unknown', password='password123'))

        self.assertIsNone(result)
        mock_verify.assert_not_called()

    def test_returnsNone_whenPasswordIsWrong(self, mock_read, mock_verify):
        mock_read.return_value = [(*USER_ROW, 'hashed-password')]
        mock_verify.return_value = False

        self.assertIsNone(users_service.login(LoginData(username='test_user', password='wrong')))

    def test_returnsNone_whenUserIsBlocked(self, mock_read, mock_verify):
        mock_read.return_value = [(4, 'test_user', 'user', True, 'hashed-password')]

        result = users_service.login(LoginData(username='test_user', password='password123'))

        self.assertIsNone(result)
        mock_verify.assert_not_called()


@patch('services.users_service.update_query')
@patch('services.users_service.get_user_by_id')
class UpdateUserProfile_Should(unittest.TestCase):

    def test_returnsNone_whenUserDoesNotExist(self, mock_get, mock_update):
        mock_get.return_value = None

        result = users_service.update_user_profile(make_user(), UserUpdate(first_name='New'))

        self.assertIsNone(result)
        mock_update.assert_not_called()

    def test_returnsTrue_withoutQuery_whenNoFieldsAreChanged(self, mock_get, mock_update):
        mock_get.return_value = make_user()

        self.assertTrue(users_service.update_user_profile(make_user(), UserUpdate()))
        mock_update.assert_not_called()

    def test_updatesOnlyProvidedFields(self, mock_get, mock_update):
        mock_get.return_value = make_user()

        result = users_service.update_user_profile(make_user(), UserUpdate(first_name='New'))

        self.assertTrue(result)
        self.assertEqual(('New', 4), mock_update.call_args[0][1])
        sql = mock_update.call_args[0][0]
        self.assertIn('first_name = ?', sql)
        self.assertNotIn('last_name =', sql)
        self.assertNotIn('username =', sql)

    def test_updatesAllEditableFields(self, mock_get, mock_update):
        mock_get.return_value = make_user()
        data = UserUpdate(first_name='New', last_name='Name', email='new@example.com')

        self.assertTrue(users_service.update_user_profile(make_user(), data))
        self.assertEqual(('New', 'Name', 'new@example.com', 4), mock_update.call_args[0][1])

    def test_returnsFalse_whenEmailAlreadyExists(self, mock_get, mock_update):
        mock_get.return_value = make_user()
        error = IntegrityError('Duplicate email')
        error.errno = 1062
        mock_update.side_effect = error

        self.assertFalse(users_service.update_user_profile(make_user(), UserUpdate(email='used@example.com')))

    def test_raisesError_whenDatabaseErrorIsNotDuplicate(self, mock_get, mock_update):
        mock_get.return_value = make_user()
        error = IntegrityError('Foreign key error')
        error.errno = 1452
        mock_update.side_effect = error

        with self.assertRaises(IntegrityError):
            users_service.update_user_profile(make_user(), UserUpdate(first_name='New'))


@patch('services.users_service.update_query')
class SelfDeleteUser_Should(unittest.TestCase):

    def test_deactivatesCurrentUser_whenAccountIsActive(self, mock_update):
        mock_update.return_value = 1

        self.assertTrue(users_service.self_delete_user(make_user()))
        self.assertEqual((4,), mock_update.call_args[0][1])
        self.assertIn('SET is_blocked = TRUE', mock_update.call_args[0][0])

    def test_returnsFalse_whenNoAccountIsChanged(self, mock_update):
        mock_update.return_value = 0

        self.assertFalse(users_service.self_delete_user(make_user()))


@patch('services.users_service.update_query')
@patch('services.users_service.get_user_by_id')
class AdminSetBlocked_Should(unittest.TestCase):

    def test_returnsNotAdmin_whenUserIsNotAdmin(self, mock_get, mock_update):
        self.assertEqual((False, 'not_admin'), users_service.admin_set_blocked(make_user(), 7, True))
        mock_get.assert_not_called()
        mock_update.assert_not_called()

    def test_returnsSelfChange_whenAdminChangesOwnStatus(self, mock_get, mock_update):
        self.assertEqual((False, 'self_change'), users_service.admin_set_blocked(make_user(role='admin'), 4, True))
        mock_get.assert_not_called()
        mock_update.assert_not_called()

    def test_returnsNotFound_whenUserDoesNotExist(self, mock_get, mock_update):
        mock_get.return_value = None

        self.assertEqual((False, 'not_found'), users_service.admin_set_blocked(make_user(role='admin'), 7, True))
        mock_update.assert_not_called()

    def test_blocksUser_whenUserIsActive(self, mock_get, mock_update):
        mock_get.return_value = make_user(user_id=7)
        mock_update.return_value = 1

        self.assertEqual((True, None), users_service.admin_set_blocked(make_user(role='admin'), 7, True))
        self.assertEqual((True, 7), mock_update.call_args[0][1])

    def test_unblocksUser_whenUserIsBlocked(self, mock_get, mock_update):
        mock_get.return_value = make_user(user_id=7, is_blocked=True)
        mock_update.return_value = 1

        self.assertEqual((True, None), users_service.admin_set_blocked(make_user(role='admin'), 7, False))
        self.assertEqual((False, 7), mock_update.call_args[0][1])

    def test_doesNotUpdate_whenStatusIsAlreadyTheSame(self, mock_get, mock_update):
        mock_get.return_value = make_user(user_id=7, is_blocked=True)

        self.assertEqual((True, None), users_service.admin_set_blocked(make_user(role='admin'), 7, True))
        mock_update.assert_not_called()

    def test_returnsNotFound_whenUpdateChangesNoRows(self, mock_get, mock_update):
        mock_get.return_value = make_user(user_id=7)
        mock_update.return_value = 0

        self.assertEqual((False, 'not_found'), users_service.admin_set_blocked(make_user(role='admin'), 7, True))


@patch('services.users_service.update_query')
@patch('services.users_service.get_user_by_id')
class AdminSetRole_Should(unittest.TestCase):

    def test_returnsNotAdmin_whenUserIsNotAdmin(self, mock_get, mock_update):
        self.assertEqual((False, 'not_admin'), users_service.admin_set_role(make_user(), 7, 'moderator'))
        mock_get.assert_not_called()
        mock_update.assert_not_called()

    def test_returnsSelfChange_whenAdminChangesOwnRole(self, mock_get, mock_update):
        self.assertEqual((False, 'self_change'), users_service.admin_set_role(make_user(role='admin'), 4, 'user'))
        mock_update.assert_not_called()

    def test_returnsInvalidRole_whenRoleDoesNotExist(self, mock_get, mock_update):
        self.assertEqual((False, 'invalid_role'), users_service.admin_set_role(make_user(role='admin'), 7, 'owner'))
        mock_get.assert_not_called()
        mock_update.assert_not_called()

    def test_returnsNotFound_whenUserDoesNotExist(self, mock_get, mock_update):
        mock_get.return_value = None

        self.assertEqual((False, 'not_found'), users_service.admin_set_role(make_user(role='admin'), 7, 'moderator'))
        mock_update.assert_not_called()

    def test_promotesUser_toModerator(self, mock_get, mock_update):
        mock_get.return_value = make_user(user_id=7)
        mock_update.return_value = 1

        self.assertEqual((True, None), users_service.admin_set_role(make_user(role='admin'), 7, 'moderator'))
        self.assertEqual(('moderator', 7), mock_update.call_args[0][1])

    def test_promotesUser_toAdmin(self, mock_get, mock_update):
        mock_get.return_value = make_user(user_id=7)
        mock_update.return_value = 1

        self.assertEqual((True, None), users_service.admin_set_role(make_user(role='admin'), 7, 'admin'))
        self.assertEqual(('admin', 7), mock_update.call_args[0][1])

    def test_demotesModerator_toUser(self, mock_get, mock_update):
        mock_get.return_value = make_user(user_id=7, role='moderator')
        mock_update.return_value = 1

        self.assertEqual((True, None), users_service.admin_set_role(make_user(role='admin'), 7, 'user'))
        self.assertEqual(('user', 7), mock_update.call_args[0][1])

    def test_returnsInvalidChange_whenTargetIsAdmin(self, mock_get, mock_update):
        mock_get.return_value = make_user(user_id=7, role='admin')

        self.assertEqual((False, 'invalid_change'), users_service.admin_set_role(make_user(role='admin'), 7, 'user'))
        mock_update.assert_not_called()

    def test_doesNotUpdate_whenRoleIsAlreadyTheSame(self, mock_get, mock_update):
        mock_get.return_value = make_user(user_id=7)

        self.assertEqual((True, None), users_service.admin_set_role(make_user(role='admin'), 7, 'user'))
        mock_update.assert_not_called()

    def test_returnsNotFound_whenUpdateChangesNoRows(self, mock_get, mock_update):
        mock_get.return_value = make_user(user_id=7)
        mock_update.return_value = 0

        self.assertEqual((False, 'not_found'), users_service.admin_set_role(make_user(role='admin'), 7, 'moderator'))


@patch('services.users_service.read_query')
class AdminSearchUsers_Should(unittest.TestCase):

    def test_returnsNone_whenUserIsNotAdmin(self, mock_read):
        self.assertIsNone(users_service.admin_search_users(make_user(), 'Test', 20, 0))
        mock_read.assert_not_called()

    def test_returnsProfiles_whenUsersAreFound(self, mock_read):
        mock_read.return_value = [PROFILE_ROW]

        result = users_service.admin_search_users(make_user(role='admin'), 'Test', 10, 20)

        self.assertEqual([UserProfile.from_query_result(*PROFILE_ROW)], result)
        self.assertEqual(('%Test%', '%Test%', '%Test%', '%Test%', 10, 20), mock_read.call_args[0][1])
        sql = mock_read.call_args[0][0]
        self.assertIn('u.username LIKE ?', sql)
        self.assertIn('u.email LIKE ?', sql)
        self.assertIn('u.first_name LIKE ?', sql)
        self.assertIn('u.last_name LIKE ?', sql)

    def test_returnsEmptyList_whenNoUsersMatch(self, mock_read):
        mock_read.return_value = []

        self.assertEqual([], users_service.admin_search_users(make_user(role='admin'), 'unknown', 20, 0))

    def test_usesAllUsersPattern_whenSearchIsEmpty(self, mock_read):
        mock_read.return_value = []

        users_service.admin_search_users(make_user(role='admin'), '', 20, 0)

        self.assertEqual(('%%', '%%', '%%', '%%', 20, 0), mock_read.call_args[0][1])


@patch('services.users_service.read_query')
class UserCounts_Should(unittest.TestCase):

    def test_returnsAllUsersCount(self, mock_read):
        mock_read.return_value = [(12,)]

        self.assertEqual(12, users_service.get_all_users_count())

    def test_returnsActiveUsersCount(self, mock_read):
        mock_read.return_value = [(8,)]

        self.assertEqual(8, users_service.get_active_users_count())
        self.assertIn('is_blocked = FALSE', mock_read.call_args[0][0])

    def test_returnsZero_whenNoUsersExist(self, mock_read):
        mock_read.return_value = [(0,)]

        self.assertEqual(0, users_service.get_all_users_count())
        self.assertEqual(0, users_service.get_active_users_count())
