import unittest
from unittest.mock import Mock, patch
from fastapi import HTTPException

with patch.dict('os.environ', {'JWT_SECRET': 'test-secret'}):
    from routers.web import web_user_routers
from data.models.user import User, UserProfile


def make_user(user_id=4, role='user'):
    return User(user_id=user_id, username='test_user', role_name=role, is_blocked=False)


def make_request():
    request = Mock()
    request.session = {'csrf_token': 'test-csrf'}
    return request


@patch('routers.web.web_user_routers.templates.TemplateResponse')
class WebRegister_Should(unittest.TestCase):

    @patch('routers.web.web_user_routers.register', return_value=4)
    def test_redirectsToLogin_whenRegistrationSucceeds(self, mock_register, mock_template):
        response = web_user_routers.register_user(make_request(), 'Test', 'User', 'test@example.com',
                                                  'test_user', 'password123', 'test-csrf')

        self.assertEqual(303, response.status_code)
        self.assertEqual('/login', response.headers['location'])
        self.assertEqual('test_user', mock_register.call_args[0][0].username)

    @patch('routers.web.web_user_routers.register')
    def test_returns422_whenRegistrationDataIsInvalid(self, mock_register, mock_template):
        web_user_routers.register_user(make_request(), 'Test', 'User', 'invalid-email',
                                      'test_user', 'password123', 'test-csrf')

        self.assertEqual(422, mock_template.call_args.kwargs['status_code'])
        mock_register.assert_not_called()

    @patch('routers.web.web_user_routers.register', return_value=None)
    def test_returns409_whenUsernameOrEmailExists(self, mock_register, mock_template):
        web_user_routers.register_user(make_request(), 'Test', 'User', 'test@example.com',
                                      'test_user', 'password123', 'test-csrf')

        self.assertEqual(409, mock_template.call_args.kwargs['status_code'])

    @patch('routers.web.web_user_routers.register')
    def test_rejectsInvalidCsrf_beforeRegistration(self, mock_register, mock_template):
        with self.assertRaises(HTTPException) as error:
            web_user_routers.register_user(make_request(), 'Test', 'User', 'test@example.com',
                                          'test_user', 'password123', 'wrong-csrf')

        self.assertEqual(403, error.exception.status_code)
        mock_register.assert_not_called()


@patch('routers.web.web_user_routers.templates.TemplateResponse')
@patch('routers.web.web_user_routers.create_token', return_value='test-token')
@patch('routers.web.web_user_routers.login')
class WebLogin_Should(unittest.TestCase):

    def test_setsHttpOnlyCookie_whenLoginSucceeds(self, mock_login, mock_token, mock_template):
        mock_login.return_value = make_user()

        response = web_user_routers.login_user(make_request(), 'test_user', 'password123', 'test-csrf')

        self.assertEqual(303, response.status_code)
        self.assertEqual('/', response.headers['location'])
        cookie = response.headers['set-cookie']
        self.assertIn('access_token=test-token', cookie)
        self.assertIn('HttpOnly', cookie)
        self.assertIn('SameSite=lax', cookie)
        self.assertIn(f'Max-Age={web_user_routers.EXPIRE_MINUTES * 60}', cookie)
        mock_token.assert_called_once_with(4)

    def test_returns401_whenCredentialsAreWrong(self, mock_login, mock_token, mock_template):
        mock_login.return_value = None

        web_user_routers.login_user(make_request(), 'test_user', 'wrong', 'test-csrf')

        self.assertEqual(401, mock_template.call_args.kwargs['status_code'])
        mock_token.assert_not_called()

    def test_returns422_whenUsernameIsInvalid(self, mock_login, mock_token, mock_template):
        web_user_routers.login_user(make_request(), 'a', 'password123', 'test-csrf')

        self.assertEqual(422, mock_template.call_args.kwargs['status_code'])
        mock_login.assert_not_called()

    def test_rejectsInvalidCsrf_beforeLogin(self, mock_login, mock_token, mock_template):
        with self.assertRaises(HTTPException) as error:
            web_user_routers.login_user(make_request(), 'test_user', 'password123', 'wrong-csrf')

        self.assertEqual(403, error.exception.status_code)
        mock_login.assert_not_called()


class WebLogout_Should(unittest.TestCase):

    def test_deletesCookie_andRedirectsHome(self):
        response = web_user_routers.logout_user(make_request(), 'test-csrf')

        self.assertEqual(303, response.status_code)
        self.assertEqual('/', response.headers['location'])
        self.assertIn('access_token=', response.headers['set-cookie'])
        self.assertIn('Max-Age=0', response.headers['set-cookie'])

    def test_rejectsInvalidCsrf(self):
        with self.assertRaises(HTTPException) as error:
            web_user_routers.logout_user(make_request(), 'wrong-csrf')

        self.assertEqual(403, error.exception.status_code)


class WebProfile_Should(unittest.TestCase):

    def setUp(self):
        self.request = make_request()
        self.user = make_user()
        self.profile = UserProfile(user_id=4, username='test_user', role_name='user', is_blocked=False,
                                   first_name='Test', last_name='User', email='test@example.com')

        user_patch = patch('routers.web.web_user_routers.get_web_current_user', return_value=self.user)
        self.mock_user = user_patch.start()
        self.addCleanup(user_patch.stop)

        profile_patch = patch('routers.web.web_user_routers.get_user_profile', return_value=self.profile)
        self.mock_profile = profile_patch.start()
        self.addCleanup(profile_patch.stop)

        template_patch = patch('routers.web.web_user_routers.templates.TemplateResponse')
        self.mock_template = template_patch.start()
        self.addCleanup(template_patch.stop)

    def test_redirectsToLogin_whenProfileVisitorIsGuest(self):
        self.mock_user.return_value = None

        response = web_user_routers.user_profile(self.request)

        self.assertEqual('/login', response.headers['location'])
        self.mock_profile.assert_not_called()

    def test_showsSuccessMessage_onceOnProfile(self):
        self.request.session['success_message'] = 'Profile updated successfully'

        web_user_routers.user_profile(self.request)

        context = self.mock_template.call_args.kwargs['context']
        self.assertEqual(self.profile, context['profile'])
        self.assertEqual('Profile updated successfully', context['message'])
        self.assertNotIn('success_message', self.request.session)

    def test_loadsEditProfile_withCurrentProfile(self):
        web_user_routers.edit_profile_page(self.request)

        self.assertEqual('edit_profile.html', self.mock_template.call_args.kwargs['name'])
        self.assertEqual(self.profile, self.mock_template.call_args.kwargs['context']['profile'])

    @patch('routers.web.web_user_routers.update_user_profile')
    def test_redirectsGuest_beforeUpdatingProfile(self, mock_update):
        self.mock_user.return_value = None

        response = web_user_routers.update_user(self.request, 'New', None, None, 'test-csrf')

        self.assertEqual('/login', response.headers['location'])
        mock_update.assert_not_called()

    @patch('routers.web.web_user_routers.update_user_profile', return_value=True)
    def test_stripsInput_andStoresSuccessMessage(self, mock_update):
        response = web_user_routers.update_user(self.request, ' New ', ' ', '', 'test-csrf')

        data = mock_update.call_args[0][1]
        self.assertEqual('New', data.first_name)
        self.assertIsNone(data.last_name)
        self.assertIsNone(data.email)
        self.assertEqual('/profile', response.headers['location'])
        self.assertEqual('Profile updated successfully', self.request.session['success_message'])

    @patch('routers.web.web_user_routers.update_user_profile')
    def test_returns422_withoutUpdatingInvalidData(self, mock_update):
        web_user_routers.update_user(self.request, None, None, 'invalid-email', 'test-csrf')

        self.assertEqual(422, self.mock_template.call_args.kwargs['status_code'])
        mock_update.assert_not_called()

    @patch('routers.web.web_user_routers.update_user_profile', return_value=False)
    def test_returns409_whenEmailAlreadyExists(self, mock_update):
        web_user_routers.update_user(self.request, None, None, 'used@example.com', 'test-csrf')

        self.assertEqual(409, self.mock_template.call_args.kwargs['status_code'])
        self.assertNotIn('success_message', self.request.session)

    @patch('routers.web.web_user_routers.update_user_profile', return_value=None)
    def test_redirectsHome_whenUpdatedUserNoLongerExists(self, mock_update):
        response = web_user_routers.update_user(self.request, 'New', None, None, 'test-csrf')

        self.assertEqual('/', response.headers['location'])

    @patch('routers.web.web_user_routers.update_user_profile')
    def test_rejectsInvalidCsrf_beforeUpdatingProfile(self, mock_update):
        with self.assertRaises(HTTPException) as error:
            web_user_routers.update_user(self.request, 'New', None, None, 'wrong-csrf')

        self.assertEqual(403, error.exception.status_code)
        mock_update.assert_not_called()

    @patch('routers.web.web_user_routers.self_delete_user')
    @patch('routers.web.web_user_routers.login', return_value=None)
    def test_doesNotDelete_whenPasswordIsWrong(self, mock_login, mock_delete):
        web_user_routers.delete_user(self.request, 'test_user', 'wrong', 'test-csrf')

        self.assertEqual(401, self.mock_template.call_args.kwargs['status_code'])
        mock_delete.assert_not_called()

    @patch('routers.web.web_user_routers.self_delete_user')
    @patch('routers.web.web_user_routers.login')
    def test_doesNotDelete_whenConfirmedUserIsAnotherAccount(self, mock_login, mock_delete):
        mock_login.return_value = make_user(user_id=7)

        web_user_routers.delete_user(self.request, 'other_user', 'password123', 'test-csrf')

        self.assertEqual(401, self.mock_template.call_args.kwargs['status_code'])
        mock_delete.assert_not_called()

    @patch('routers.web.web_user_routers.self_delete_user')
    @patch('routers.web.web_user_routers.login')
    def test_doesNotDelete_whenConfirmationDataIsInvalid(self, mock_login, mock_delete):
        web_user_routers.delete_user(self.request, 'a', 'password123', 'test-csrf')

        self.assertEqual(401, self.mock_template.call_args.kwargs['status_code'])
        mock_login.assert_not_called()
        mock_delete.assert_not_called()

    @patch('routers.web.web_user_routers.self_delete_user', return_value=True)
    @patch('routers.web.web_user_routers.login')
    def test_deletesCookie_whenOwnAccountIsDeactivated(self, mock_login, mock_delete):
        mock_login.return_value = self.user

        response = web_user_routers.delete_user(self.request, 'test_user', 'password123', 'test-csrf')

        self.assertEqual(303, response.status_code)
        self.assertEqual('/', response.headers['location'])
        self.assertIn('Max-Age=0', response.headers['set-cookie'])
        mock_delete.assert_called_once_with(self.user)

    @patch('routers.web.web_user_routers.self_delete_user', return_value=False)
    @patch('routers.web.web_user_routers.login')
    def test_redirectsToProfile_whenDeactivationFails(self, mock_login, mock_delete):
        mock_login.return_value = self.user

        response = web_user_routers.delete_user(self.request, 'test_user', 'password123', 'test-csrf')

        self.assertEqual('/profile', response.headers['location'])
        self.assertNotIn('set-cookie', response.headers)

    @patch('routers.web.web_user_routers.self_delete_user')
    def test_rejectsInvalidCsrf_beforeDeletingProfile(self, mock_delete):
        with self.assertRaises(HTTPException) as error:
            web_user_routers.delete_user(self.request, 'test_user', 'password123', 'wrong-csrf')

        self.assertEqual(403, error.exception.status_code)
        mock_delete.assert_not_called()


class WebAdmin_Should(unittest.TestCase):

    def setUp(self):
        self.request = make_request()
        self.admin = make_user(role='admin')
        user_patch = patch('routers.web.web_user_routers.get_web_current_user', return_value=self.admin)
        self.mock_user = user_patch.start()
        self.addCleanup(user_patch.stop)

    @patch('routers.web.web_user_routers.admin_search_users')
    def test_redirectsGuest_toLogin(self, mock_search):
        self.mock_user.return_value = None

        response = web_user_routers.admin_search(self.request, '', 20, 0)

        self.assertEqual('/login', response.headers['location'])
        mock_search.assert_not_called()

    @patch('routers.web.web_user_routers.admin_search_users')
    def test_rejectsNonAdmin_beforeSearching(self, mock_search):
        self.mock_user.return_value = make_user()

        with self.assertRaises(HTTPException) as error:
            web_user_routers.admin_search(self.request, '', 20, 0)

        self.assertEqual(403, error.exception.status_code)
        mock_search.assert_not_called()

    @patch('routers.web.web_user_routers.templates.TemplateResponse')
    @patch('routers.web.web_user_routers.admin_search_users', return_value=[])
    def test_passesResultsAndMessages_toAdminTemplate(self, mock_search, mock_template):
        self.request.session['success_message'] = 'User blocked successfully'
        self.request.session['error_message'] = 'Cannot demote an administrator'

        web_user_routers.admin_search(self.request, 'Test', 10, 20)

        mock_search.assert_called_once_with(self.admin, 'Test', 10, 20)
        context = mock_template.call_args.kwargs['context']
        self.assertEqual([], context['result'])
        self.assertEqual('Test', context['search'])
        self.assertEqual(10, context['limit'])
        self.assertEqual(20, context['offset'])
        self.assertEqual('User blocked successfully', context['message'])
        self.assertEqual('Cannot demote an administrator', context['error'])
        self.assertNotIn('success_message', self.request.session)
        self.assertNotIn('error_message', self.request.session)

    @patch('routers.web.web_user_routers.admin_set_blocked', return_value=(True, None))
    def test_storesSuccessMessage_whenUserIsBlocked(self, mock_block):
        response = web_user_routers.admin_block(self.request, 7, True, 'test-csrf')

        self.assertEqual('/admin/users', response.headers['location'])
        self.assertEqual('User blocked successfully', self.request.session['success_message'])
        mock_block.assert_called_once_with(self.admin, 7, True)

    @patch('routers.web.web_user_routers.admin_set_blocked', return_value=(True, None))
    def test_storesSuccessMessage_whenUserIsUnblocked(self, mock_block):
        web_user_routers.admin_block(self.request, 7, False, 'test-csrf')

        self.assertEqual('User unblocked successfully', self.request.session['success_message'])
        mock_block.assert_called_once_with(self.admin, 7, False)

    @patch('routers.web.web_user_routers.admin_set_blocked')
    def test_rejectsNonAdmin_beforeBlockingUser(self, mock_block):
        self.mock_user.return_value = make_user()

        with self.assertRaises(HTTPException) as error:
            web_user_routers.admin_block(self.request, 7, True, 'test-csrf')

        self.assertEqual(403, error.exception.status_code)
        mock_block.assert_not_called()

    @patch('routers.web.web_user_routers.admin_set_blocked', return_value=(False, 'self_change'))
    def test_rejectsChangingOwnStatus(self, mock_block):
        with self.assertRaises(HTTPException) as error:
            web_user_routers.admin_block(self.request, 4, True, 'test-csrf')

        self.assertEqual(403, error.exception.status_code)

    @patch('routers.web.web_user_routers.admin_set_blocked', return_value=(False, 'not_found'))
    def test_returns404_whenBlockedUserDoesNotExist(self, mock_block):
        with self.assertRaises(HTTPException) as error:
            web_user_routers.admin_block(self.request, 99, True, 'test-csrf')

        self.assertEqual(404, error.exception.status_code)

    @patch('routers.web.web_user_routers.admin_set_blocked')
    def test_rejectsInvalidCsrf_beforeBlockingUser(self, mock_block):
        with self.assertRaises(HTTPException) as error:
            web_user_routers.admin_block(self.request, 7, True, 'wrong-csrf')

        self.assertEqual(403, error.exception.status_code)
        mock_block.assert_not_called()

    @patch('routers.web.web_user_routers.admin_set_role', return_value=(True, None))
    def test_storesSuccessMessage_whenRoleIsChanged(self, mock_role):
        response = web_user_routers.admin_role_update(self.request, 7, 'moderator', 'test-csrf')

        self.assertEqual('/admin/users', response.headers['location'])
        self.assertEqual('User role updated successfully', self.request.session['success_message'])
        mock_role.assert_called_once_with(self.admin, 7, 'moderator')

    @patch('routers.web.web_user_routers.admin_set_role')
    def test_rejectsNonAdmin_beforeChangingRole(self, mock_role):
        self.mock_user.return_value = make_user()

        with self.assertRaises(HTTPException) as error:
            web_user_routers.admin_role_update(self.request, 7, 'admin', 'test-csrf')

        self.assertEqual(403, error.exception.status_code)
        mock_role.assert_not_called()

    @patch('routers.web.web_user_routers.admin_set_role', return_value=(False, 'invalid_change'))
    def test_storesErrorMessage_whenTargetIsAdmin(self, mock_role):
        response = web_user_routers.admin_role_update(self.request, 7, 'user', 'test-csrf')

        self.assertEqual('/admin/users', response.headers['location'])
        self.assertEqual('Cannot demote an administrator', self.request.session['error_message'])
        self.assertNotIn('success_message', self.request.session)

    @patch('routers.web.web_user_routers.admin_set_role', return_value=(False, 'invalid_role'))
    def test_returns422_whenRoleIsInvalid(self, mock_role):
        with self.assertRaises(HTTPException) as error:
            web_user_routers.admin_role_update(self.request, 7, 'owner', 'test-csrf')

        self.assertEqual(422, error.exception.status_code)

    @patch('routers.web.web_user_routers.admin_set_role')
    def test_rejectsInvalidCsrf_beforeChangingRole(self, mock_role):
        with self.assertRaises(HTTPException) as error:
            web_user_routers.admin_role_update(self.request, 7, 'admin', 'wrong-csrf')

        self.assertEqual(403, error.exception.status_code)
        mock_role.assert_not_called()
