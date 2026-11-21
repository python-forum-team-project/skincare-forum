import unittest
from common import permissions
from data.models.topics import Topic
from data.models.user import User



def make_user(user_id=4, role='user', is_blocked=False):
    return User(user_id=user_id, username='test_user', role_name=role, is_blocked=is_blocked)


def make_topic(topic_id=1, author_id=4, is_locked=False, is_private=False):
    return Topic(topic_id=topic_id, author_id=author_id, title='A valid topic title',
                 content='A valid topic content that is at least 32 chars',
                 is_private=is_private, is_locked=is_locked)



class CanEditTopic_Should(unittest.TestCase):

    def test_returnsFalse_whenTopicIsLocked(self):
        user = make_user(user_id=4)
        topic = make_topic(author_id=4, is_locked=True)

        self.assertFalse(permissions.can_edit_topic(user, topic))


    def test_returnsTrue_whenTopicIsNotLocked(self):
        user = make_user(user_id=4)
        topic = make_topic(author_id=4, is_locked=False)

        self.assertTrue(permissions.can_edit_topic(user, topic))


    def test_returnsFalse_when_userID_is_Not_AuthorID(self):
        user = make_user(user_id=4)
        topic = make_topic(author_id=5, is_locked=False)

        self.assertFalse(permissions.can_edit_topic(user, topic))

    def test_returnsTrue_when_userID_is_AuthorID(self):
        user = make_user(user_id=4)
        topic = make_topic(author_id=4, is_locked=False)

        self.assertTrue(permissions.can_edit_topic(user, topic))



class CanCreateTopic_Should(unittest.TestCase):

    def test_returnsTrue_whenUserIsNotBlocked(self):
        user = make_user(is_blocked=False)

        self.assertTrue(permissions.can_create_topic(user))

    def test_returnsFalse_whenUserIsBlocked(self):
        user = make_user(is_blocked=True)

        self.assertFalse(permissions.can_create_topic(user))

    def test_returnsTrue_whenAdminIsNotBlocked(self):
        user = make_user(role='admin', is_blocked=False)

        self.assertTrue(permissions.can_create_topic(user))

    def test_returnsFalse_whenAdminIsBlocked(self):
        user = make_user(role='admin', is_blocked=True)

        self.assertFalse(permissions.can_create_topic(user))



class CanEditTopic_Should(unittest.TestCase):

    def test_returnsTrue_whenUserIsAuthor_andTopicIsNotLocked(self):
        user = make_user(user_id=4)
        topic = make_topic(author_id=4, is_locked=False)

        self.assertTrue(permissions.can_edit_topic(user, topic))

    def test_returnsFalse_whenTopicIsLocked(self):
        user = make_user(user_id=4)
        topic = make_topic(author_id=4, is_locked=True)

        self.assertFalse(permissions.can_edit_topic(user, topic))

    def test_returnsFalse_whenUserIsNotAuthor(self):
        user = make_user(user_id=4)
        topic = make_topic(author_id=5)

        self.assertFalse(permissions.can_edit_topic(user, topic))

    def test_returnsFalse_whenUserIsBlocked(self):
        user = make_user(user_id=4, is_blocked=True)
        topic = make_topic(author_id=4)

        self.assertFalse(permissions.can_edit_topic(user, topic))

    def test_returnsFalse_whenUserIsNone(self):
        topic = make_topic(author_id=4)

        self.assertFalse(permissions.can_edit_topic(None, topic))

    def test_returnsFalse_whenAdminIsNotAuthor(self):
        # Admins can't edit other people's topics (they can only delete them)
        user = make_user(user_id=1, role='admin')
        topic = make_topic(author_id=4)

        self.assertFalse(permissions.can_edit_topic(user, topic))

    def test_returnsTrue_whenTopicIsPrivate_andUserIsAuthor(self):
        # Privacy doesn't affect editing, only lock/author/blocked do
        user = make_user(user_id=4)
        topic = make_topic(author_id=4, is_private=True)

        self.assertTrue(permissions.can_edit_topic(user, topic))



class CanDeleteTopic_Should(unittest.TestCase):

    def test_returnsTrue_whenUserIsAuthor(self):
        user = make_user(user_id=4)
        topic = make_topic(author_id=4)

        self.assertTrue(permissions.can_delete_topic(user, topic))

    def test_returnsTrue_whenUserIsAdmin_andNotAuthor(self):
        user = make_user(user_id=1, role='admin')
        topic = make_topic(author_id=4)

        self.assertTrue(permissions.can_delete_topic(user, topic))

    def test_returnsFalse_whenUserIsNotAuthor_andNotAdmin(self):
        user = make_user(user_id=4)
        topic = make_topic(author_id=5)

        self.assertFalse(permissions.can_delete_topic(user, topic))

    def test_returnsTrue_whenTopicIsLocked_andUserIsAuthor(self):
        user = make_user(user_id=4)
        topic = make_topic(author_id=4, is_locked=True)

        self.assertTrue(permissions.can_delete_topic(user, topic))

    def test_returnsTrue_whenAdmin_andTopicIsLocked(self):
        user = make_user(user_id=1, role='admin')
        topic = make_topic(author_id=4, is_locked=True)

        self.assertTrue(permissions.can_delete_topic(user, topic))