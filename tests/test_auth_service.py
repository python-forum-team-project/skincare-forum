import unittest
from unittest.mock import patch
from datetime import datetime, timedelta, timezone
import jwt

with patch.dict('os.environ', {'JWT_SECRET': 'test-secret'}):
    from services import auth_service


TEST_SECRET = 'test-secret-for-auth-tests-at-least-32-characters'


class Password_Should(unittest.TestCase):

    def test_hashPassword_withoutSavingPlainText(self):
        password_hash = auth_service.hash_password('password123')

        self.assertNotEqual('password123', password_hash)
        self.assertTrue(auth_service.verify_password('password123', password_hash))

    def test_rejectWrongPassword(self):
        password_hash = auth_service.hash_password('password123')

        self.assertFalse(auth_service.verify_password('wrong-password', password_hash))

    def test_useDifferentHashes_forSamePassword(self):
        first_hash = auth_service.hash_password('password123')
        second_hash = auth_service.hash_password('password123')

        self.assertNotEqual(first_hash, second_hash)


class Token_Should(unittest.TestCase):

    def setUp(self):
        secret_patch = patch.object(auth_service, 'SECRET_KEY', TEST_SECRET)
        secret_patch.start()
        self.addCleanup(secret_patch.stop)
        self.expires = datetime.now(timezone.utc) + timedelta(minutes=10)

    def test_returnsUserId_fromCreatedToken(self):
        token = auth_service.create_token(4)

        self.assertEqual(4, auth_service.get_user_id_from_token(token))

    def test_setsSubjectAndExpiration(self):
        before = datetime.now(timezone.utc)
        token = auth_service.create_token(4)
        after = datetime.now(timezone.utc)

        payload = jwt.decode(token, TEST_SECRET, algorithms=['HS256'])

        self.assertEqual('4', payload['sub'])
        self.assertGreaterEqual(payload['exp'], int(before.timestamp()) + auth_service.EXPIRE_MINUTES * 60)
        self.assertLessEqual(payload['exp'], int(after.timestamp()) + auth_service.EXPIRE_MINUTES * 60)

    def test_returnsNone_whenTokenIsMalformed(self):
        self.assertIsNone(auth_service.get_user_id_from_token('invalid-token'))

    def test_returnsNone_whenTokenIsExpired(self):
        expired = datetime.now(timezone.utc) - timedelta(minutes=1)
        token = jwt.encode({'sub': '4', 'exp': expired}, TEST_SECRET, algorithm='HS256')

        self.assertIsNone(auth_service.get_user_id_from_token(token))

    def test_returnsNone_whenSignatureIsWrong(self):
        token = jwt.encode({'sub': '4', 'exp': self.expires}, 'another-secret-at-least-32-characters', algorithm='HS256')

        self.assertIsNone(auth_service.get_user_id_from_token(token))

    def test_returnsNone_whenSubjectIsMissing(self):
        token = jwt.encode({'exp': self.expires}, TEST_SECRET, algorithm='HS256')

        self.assertIsNone(auth_service.get_user_id_from_token(token))

    def test_returnsNone_whenExpirationIsMissing(self):
        token = jwt.encode({'sub': '4'}, TEST_SECRET, algorithm='HS256')

        self.assertIsNone(auth_service.get_user_id_from_token(token))

    def test_returnsNone_whenSubjectIsNotInteger(self):
        token = jwt.encode({'sub': 'abc', 'exp': self.expires}, TEST_SECRET, algorithm='HS256')

        self.assertIsNone(auth_service.get_user_id_from_token(token))

    def test_returnsNone_whenUserIdIsZero(self):
        token = jwt.encode({'sub': '0', 'exp': self.expires}, TEST_SECRET, algorithm='HS256')

        self.assertIsNone(auth_service.get_user_id_from_token(token))

    def test_returnsNone_whenUserIdIsNegative(self):
        token = jwt.encode({'sub': '-4', 'exp': self.expires}, TEST_SECRET, algorithm='HS256')

        self.assertIsNone(auth_service.get_user_id_from_token(token))

    def test_returnsNone_whenAlgorithmIsNotAllowed(self):
        token = jwt.encode({'sub': '4', 'exp': self.expires}, TEST_SECRET, algorithm='HS384')

        self.assertIsNone(auth_service.get_user_id_from_token(token))
