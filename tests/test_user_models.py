import unittest
from pydantic import ValidationError
from data.models.user import UserCreate, UserUpdate, LoginData, RoleUpdate


def registration_data():
    return {'first_name': 'Test', 'last_name': 'User', 'email': 'test@example.com',
            'username': 'test_user', 'password': 'password123'}


class UserCreate_Should(unittest.TestCase):

    def test_stripsSpaces_fromNamesAndUsername(self):
        data = registration_data()
        data.update(first_name=' Test ', last_name=' User ', username=' test_user ')

        user = UserCreate(**data)

        self.assertEqual('Test', user.first_name)
        self.assertEqual('User', user.last_name)
        self.assertEqual('test_user', user.username)

    def test_rejectsInvalidEmail(self):
        data = registration_data()
        data['email'] = 'invalid-email'

        with self.assertRaises(ValidationError):
            UserCreate(**data)

    def test_rejectsShortPassword(self):
        data = registration_data()
        data['password'] = 'short'

        with self.assertRaises(ValidationError):
            UserCreate(**data)

    def test_rejectsLongPassword(self):
        data = registration_data()
        data['password'] = 'a' * 129

        with self.assertRaises(ValidationError):
            UserCreate(**data)

    def test_rejectsShortUsername(self):
        data = registration_data()
        data['username'] = 'a'

        with self.assertRaises(ValidationError):
            UserCreate(**data)

    def test_rejectsLongUsername(self):
        data = registration_data()
        data['username'] = 'a' * 17

        with self.assertRaises(ValidationError):
            UserCreate(**data)

    def test_rejectsBlankFirstName(self):
        data = registration_data()
        data['first_name'] = '   '

        with self.assertRaises(ValidationError):
            UserCreate(**data)

    def test_rejectsLongLastName(self):
        data = registration_data()
        data['last_name'] = 'a' * 33

        with self.assertRaises(ValidationError):
            UserCreate(**data)

    def test_rejectsRoleProvidedDuringRegistration(self):
        data = registration_data()
        data['role_name'] = 'admin'

        with self.assertRaises(ValidationError):
            UserCreate(**data)


class UserUpdate_Should(unittest.TestCase):

    def test_allowsEmptyUpdate(self):
        data = UserUpdate()

        self.assertIsNone(data.first_name)
        self.assertIsNone(data.last_name)
        self.assertIsNone(data.email)

    def test_stripsSpaces_fromNames(self):
        data = UserUpdate(first_name=' New ', last_name=' Name ')

        self.assertEqual('New', data.first_name)
        self.assertEqual('Name', data.last_name)

    def test_rejectsUsernameChange(self):
        with self.assertRaises(ValidationError):
            UserUpdate(username='new_username')

    def test_rejectsRoleChange(self):
        with self.assertRaises(ValidationError):
            UserUpdate(role_name='admin')

    def test_rejectsInvalidEmail(self):
        with self.assertRaises(ValidationError):
            UserUpdate(email='invalid-email')

    def test_rejectsBlankName(self):
        with self.assertRaises(ValidationError):
            UserUpdate(first_name='  ')


class LoginData_Should(unittest.TestCase):

    def test_stripsUsername_butPreservesPassword(self):
        data = LoginData(username=' test_user ', password=' password123 ')

        self.assertEqual('test_user', data.username)
        self.assertEqual(' password123 ', data.password)

    def test_rejectsEmptyUsername(self):
        with self.assertRaises(ValidationError):
            LoginData(username='', password='password123')


class RoleUpdate_Should(unittest.TestCase):

    def test_acceptsModeratorRole(self):
        self.assertEqual('moderator', RoleUpdate(role_name='moderator').role_name)

    def test_rejectsUnknownRole(self):
        with self.assertRaises(ValidationError):
            RoleUpdate(role_name='owner')
