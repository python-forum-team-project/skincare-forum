import unittest
from unittest.mock import patch

from services import topics_service
from common import errors
from data.models.topics import Topic, TopicCreate, TopicUpdate
from data.models.user import User



VALID_TITLE = 'A valid topic title'
VALID_CONTENT = 'A valid topic content that is at least 32 chars'


def make_user(user_id=4, role='user', is_blocked=False):
    return User(user_id=user_id, username='test_user', role_name=role, is_blocked=is_blocked)


def make_topic(topic_id=1, author_id=4, is_locked=False, is_private=False):
    return Topic(topic_id=topic_id, author_id=author_id, title=VALID_TITLE,
                 content=VALID_CONTENT, is_private=is_private, is_locked=is_locked)


def make_topic_create(title=VALID_TITLE, content=VALID_CONTENT, is_private=False):
    return TopicCreate(title=title, content=content, is_private=is_private)


def make_topic_update(title='An updated topic title', content='Updated content that is also at least 32 chars'):
    return TopicUpdate(title=title, content=content)



TOPIC_ROW = (1, 'test_user', VALID_TITLE, VALID_CONTENT, '2026-11-21 12:00:00')
REPLY_ROW_1 = (10, 1, 5, 'First reply', '2026-11-21 12:05:00')
REPLY_ROW_2 = (11, 1, 6, 'Second reply', '2026-11-21 12:10:00')






@patch('services.topics_service.update_query')
@patch('services.topics_service._get_topic_model')
class DeleteTopic_Should(unittest.TestCase):

    def test_returnsNotFound_whenTopicDoesNotExist(self, mock_get, mock_update):
        mock_get.return_value = None

        result = topics_service.delete_topic(99, make_user())

        self.assertEqual(errors.TOPIC_NOT_FOUND, result)
        mock_update.assert_not_called()

    def test_returnsCannotDelete_whenUserIsNotAuthorOrAdmin(self, mock_get, mock_update):
        mock_get.return_value = make_topic(author_id=4)

        result = topics_service.delete_topic(1, make_user(user_id=7))

        self.assertEqual(errors.CANNOT_DELETE_TOPIC, result)
        mock_update.assert_not_called()

    def test_deletesTopic_whenUserIsAuthor(self, mock_get, mock_update):
        mock_get.return_value = make_topic(author_id=4)

        result = topics_service.delete_topic(1, make_user(user_id=4))

        self.assertIsNone(result)
        mock_update.assert_called_once()

    def test_deletesTopic_whenUserIsAdmin(self, mock_get, mock_update):
        mock_get.return_value = make_topic(author_id=4)

        topics_service.delete_topic(1, make_user(user_id=1, role='admin'))

        mock_update.assert_called_once()




@patch('services.topics_service.TopicResponse')
@patch('services.topics_service.Reply')
@patch('services.topics_service.read_query')
class GetTopicById_Should(unittest.TestCase):

    def test_returnsNotFound_whenTopicDoesNotExist(self, mock_read, mock_reply, mock_response):
        mock_read.return_value = []

        result = topics_service.get_topic_by_id(99)

        self.assertEqual(errors.TOPIC_NOT_FOUND, result)

    def test_doesNotQueryReplies_whenTopicDoesNotExist(self, mock_read, mock_reply, mock_response):
        mock_read.return_value = []

        topics_service.get_topic_by_id(99)

        mock_read.assert_called_once()
        mock_response.from_query_results.assert_not_called()

    def test_returnsTopicResponse_whenTopicExists(self, mock_read, mock_reply, mock_response):
        mock_read.side_effect = [[TOPIC_ROW], []]

        result = topics_service.get_topic_by_id(1)

        self.assertEqual(mock_response.from_query_results.return_value, result)

    def test_passesTopicRowAndReplies_toTopicResponse(self, mock_read, mock_reply, mock_response):
        mock_read.side_effect = [[TOPIC_ROW], [REPLY_ROW_1, REPLY_ROW_2]]
        mock_reply.from_query_result.side_effect = ['reply_1', 'reply_2']

        topics_service.get_topic_by_id(1)

        mock_response.from_query_results.assert_called_once_with(*TOPIC_ROW, replies=['reply_1', 'reply_2'])

    def test_passesEmptyReplies_whenTopicHasNoReplies(self, mock_read, mock_reply, mock_response):
        mock_read.side_effect = [[TOPIC_ROW], []]

        topics_service.get_topic_by_id(1)

        mock_reply.from_query_result.assert_not_called()
        mock_response.from_query_results.assert_called_once_with(*TOPIC_ROW, replies=[])

    def test_buildsOneReply_perReplyRow(self, mock_read, mock_reply, mock_response):
        mock_read.side_effect = [[TOPIC_ROW], [REPLY_ROW_1, REPLY_ROW_2]]

        topics_service.get_topic_by_id(1)

        self.assertEqual(2, mock_reply.from_query_result.call_count)
        mock_reply.from_query_result.assert_any_call(*REPLY_ROW_1)
        mock_reply.from_query_result.assert_any_call(*REPLY_ROW_2)




@patch('services.topics_service.get_topic_by_id')
@patch('services.topics_service.insert_query')
class CreateTopic_Should(unittest.TestCase):

    def test_returnsUserIsBlocked_whenAuthorIsBlocked(self, mock_insert, mock_get):
        result = topics_service.create_topic(make_topic_create(), make_user(is_blocked=True))

        self.assertEqual(errors.USER_IS_BLOCKED, result)

    def test_doesNotInsert_whenAuthorIsBlocked(self, mock_insert, mock_get):
        topics_service.create_topic(make_topic_create(), make_user(is_blocked=True))

        mock_insert.assert_not_called()
        mock_get.assert_not_called()

    def test_insertsTopic_withAuthorIdAndTopicData(self, mock_insert, mock_get):
        topic = make_topic_create(is_private=True)

        topics_service.create_topic(topic, make_user(user_id=4))

        mock_insert.assert_called_once()
        params = mock_insert.call_args[0][1]
        self.assertEqual((4, topic.title, topic.content, True), params)

    def test_fetchesTopic_byNewId(self, mock_insert, mock_get):
        mock_insert.return_value = 42

        topics_service.create_topic(make_topic_create(), make_user())

        mock_get.assert_called_once_with(42)

    def test_returnsCreatedTopic(self, mock_insert, mock_get):
        mock_insert.return_value = 42
        mock_get.return_value = 'created topic'

        result = topics_service.create_topic(make_topic_create(), make_user())

        self.assertEqual('created topic', result)




@patch('services.topics_service.get_topic_by_id')
@patch('services.topics_service.update_query')
@patch('services.topics_service._get_topic_model')
class UpdateTopic_Should(unittest.TestCase):

    def test_returnsNotFound_whenTopicDoesNotExist(self, mock_model, mock_update, mock_get):
        mock_model.return_value = None

        result = topics_service.update_topic(99, make_topic_update(), make_user())

        self.assertEqual(errors.TOPIC_NOT_FOUND, result)
        mock_update.assert_not_called()

    def test_returnsCannotEdit_whenUserIsNotAuthor(self, mock_model, mock_update, mock_get):
        mock_model.return_value = make_topic(author_id=4)

        result = topics_service.update_topic(1, make_topic_update(), make_user(user_id=7))

        self.assertEqual(errors.CANNOT_EDIT_TOPIC, result)
        mock_update.assert_not_called()

    def test_returnsCannotEdit_whenTopicIsLocked(self, mock_model, mock_update, mock_get):
        mock_model.return_value = make_topic(author_id=4, is_locked=True)

        result = topics_service.update_topic(1, make_topic_update(), make_user(user_id=4))

        self.assertEqual(errors.CANNOT_EDIT_TOPIC, result)
        mock_update.assert_not_called()

    def test_returnsCannotEdit_whenUserIsBlocked(self, mock_model, mock_update, mock_get):
        mock_model.return_value = make_topic(author_id=4)

        result = topics_service.update_topic(1, make_topic_update(), make_user(user_id=4, is_blocked=True))

        self.assertEqual(errors.CANNOT_EDIT_TOPIC, result)
        mock_update.assert_not_called()

    def test_returnsCannotEdit_whenAdminIsNotAuthor(self, mock_model, mock_update, mock_get):
        mock_model.return_value = make_topic(author_id=4)

        result = topics_service.update_topic(1, make_topic_update(), make_user(user_id=1, role='admin'))

        self.assertEqual(errors.CANNOT_EDIT_TOPIC, result)
        mock_update.assert_not_called()

    def test_updatesTopic_withNewTitleAndContent(self, mock_model, mock_update, mock_get):
        mock_model.return_value = make_topic(topic_id=1, author_id=4)
        updated = make_topic_update()

        topics_service.update_topic(1, updated, make_user(user_id=4))

        mock_update.assert_called_once()
        params = mock_update.call_args[0][1]
        self.assertEqual((updated.title, updated.content, 1), params)

    def test_returnsUpdatedTopic_whenUserIsAuthor(self, mock_model, mock_update, mock_get):
        mock_model.return_value = make_topic(topic_id=1, author_id=4)
        mock_get.return_value = 'updated topic'

        result = topics_service.update_topic(1, make_topic_update(), make_user(user_id=4))

        mock_get.assert_called_once_with(1)
        self.assertEqual('updated topic', result)




@patch('services.topics_service.update_query')
@patch('services.topics_service._get_topic_model')
class DeleteTopic_Should(unittest.TestCase):

    def test_returnsNotFound_whenTopicDoesNotExist(self, mock_get, mock_update):
        mock_get.return_value = None

        result = topics_service.delete_topic(99, make_user())

        self.assertEqual(errors.TOPIC_NOT_FOUND, result)
        mock_update.assert_not_called()

    def test_returnsCannotDelete_whenUserIsNotAuthorOrAdmin(self, mock_get, mock_update):
        mock_get.return_value = make_topic(author_id=4)

        result = topics_service.delete_topic(1, make_user(user_id=7))

        self.assertEqual(errors.CANNOT_DELETE_TOPIC, result)
        mock_update.assert_not_called()

    def test_deletesTopic_whenUserIsAuthor(self, mock_get, mock_update):
        mock_get.return_value = make_topic(author_id=4)

        result = topics_service.delete_topic(1, make_user(user_id=4))

        self.assertIsNone(result)
        mock_update.assert_called_once()

    def test_deletesTopic_whenUserIsAdmin(self, mock_get, mock_update):
        mock_get.return_value = make_topic(author_id=4)

        result = topics_service.delete_topic(1, make_user(user_id=1, role='admin'))

        self.assertIsNone(result)
        mock_update.assert_called_once()

    def test_deletesTopic_whenTopicIsLocked(self, mock_get, mock_update):
        mock_get.return_value = make_topic(author_id=4, is_locked=True)

        topics_service.delete_topic(1, make_user(user_id=4))

        mock_update.assert_called_once()

    def test_deletesCorrectTopic(self, mock_get, mock_update):
        mock_get.return_value = make_topic(topic_id=3, author_id=4)

        topics_service.delete_topic(3, make_user(user_id=4))

        params = mock_update.call_args[0][1]
        self.assertEqual((3,), params)




@patch('services.topics_service.read_query')
class GetTopicsCount_Should(unittest.TestCase):

    def test_returnsCount_fromQueryResult(self, mock_read):
        mock_read.return_value = [(5,)]

        self.assertEqual(5, topics_service.get_topics_count())

    def test_returnsZero_whenNoTopics(self, mock_read):
        mock_read.return_value = [(0,)]

        self.assertEqual(0, topics_service.get_topics_count())




@patch('services.topics_service.Topic')
@patch('services.topics_service.read_query')
class GetTopicModel_Should(unittest.TestCase):

    def test_returnsNone_whenTopicDoesNotExist(self, mock_read, mock_topic):
        mock_read.return_value = []

        self.assertIsNone(topics_service._get_topic_model(99))

    def test_returnsTopic_whenTopicExists(self, mock_read, mock_topic):
        row = (1, 4, VALID_TITLE, VALID_CONTENT, False, False)
        mock_read.return_value = [row]

        result = topics_service._get_topic_model(1)

        mock_topic.from_query_result.assert_called_once_with(*row)
        self.assertEqual(mock_topic.from_query_result.return_value, result)