import unittest
from unittest.mock import Mock
from fastapi import HTTPException
from common.csrf import csrf_context, verify_csrf


class Csrf_Should(unittest.TestCase):

    def setUp(self):
        self.request = Mock()
        self.request.session = {}

    def test_createsAndStoresToken_whenSessionHasNoToken(self):
        result = csrf_context(self.request)

        self.assertTrue(result['csrf_token'])
        self.assertEqual(result['csrf_token'], self.request.session['csrf_token'])

    def test_reusesExistingToken(self):
        self.request.session['csrf_token'] = 'existing-token'

        self.assertEqual({'csrf_token': 'existing-token'}, csrf_context(self.request))

    def test_acceptsMatchingToken(self):
        self.request.session['csrf_token'] = 'test-token'

        self.assertIsNone(verify_csrf(self.request, 'test-token'))

    def test_raises403_whenSubmittedTokenIsWrong(self):
        self.request.session['csrf_token'] = 'test-token'

        with self.assertRaises(HTTPException) as error:
            verify_csrf(self.request, 'wrong-token')

        self.assertEqual(403, error.exception.status_code)

    def test_raises403_whenSessionTokenIsMissing(self):
        with self.assertRaises(HTTPException) as error:
            verify_csrf(self.request, 'test-token')

        self.assertEqual(403, error.exception.status_code)
