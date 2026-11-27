import unittest
from datetime import datetime
from unittest.mock import patch

from data.models.reply import Reply
from services import replies_service

NOW = datetime(2026, 11, 23, 12, 0)
ROW = (1, 10, 5, 'Nice topic', NOW)  # reply_id, topic_id, author_id, content, created_at


class RepliesServiceShould(unittest.TestCase):

    @patch('services.replies_service.read_query')
    def test_getByTopic_returnsReplies(self, mock_read):
        mock_read.return_value = [ROW]

        result = replies_service.get_by_topic(10)

        self.assertEqual([Reply.from_query_result(*ROW)], result)

    @patch('services.replies_service.read_query')
    def test_getByTopic_returnsEmptyList_whenNoReplies(self, mock_read):
        mock_read.return_value = []

        self.assertEqual([], replies_service.get_by_topic(10))

    @patch('services.replies_service.read_query')
    def test_getById_returnsReply_whenFound(self, mock_read):
        mock_read.return_value = [ROW]

        result = replies_service.get_by_id(1)

        self.assertEqual(Reply.from_query_result(*ROW), result)

    @patch('services.replies_service.read_query')
    def test_getById_returnsNone_whenMissing(self, mock_read):
        mock_read.return_value = []

        self.assertIsNone(replies_service.get_by_id(99))

    @patch('services.replies_service.read_query')
    def test_exists_returnsTrue_whenFound(self, mock_read):
        mock_read.return_value = [(1,)]

        self.assertTrue(replies_service.exists(1))

    @patch('services.replies_service.read_query')
    def test_exists_returnsFalse_whenMissing(self, mock_read):
        mock_read.return_value = []

        self.assertFalse(replies_service.exists(99))

    @patch('services.replies_service.read_query')
    def test_belongsToTopic_returnsTrue_whenFound(self, mock_read):
        mock_read.return_value = [(1,)]

        self.assertTrue(replies_service.belongs_to_topic(1, 10))

    @patch('services.replies_service.read_query')
    def test_belongsToTopic_returnsFalse_whenMissing(self, mock_read):
        mock_read.return_value = []

        self.assertFalse(replies_service.belongs_to_topic(1, 99))

    @patch('services.replies_service.read_query')
    def test_getByAuthor_returnsReplies(self, mock_read):
        mock_read.return_value = [ROW]

        result = replies_service.get_by_author(5)

        self.assertEqual([Reply.from_query_result(*ROW)], result)

    @patch('services.replies_service.read_query')
    @patch('services.replies_service.insert_query')
    def test_create_savesReply_andReturnsIt(self, mock_insert, mock_read):
        mock_insert.return_value = 1
        mock_read.return_value = [ROW]
        reply = Reply(topic_id=10, author_id=5, content='Nice topic')

        result = replies_service.create(reply)

        self.assertEqual((10, 5, 'Nice topic'), mock_insert.call_args[0][1])
        self.assertEqual(Reply.from_query_result(*ROW), result)

    @patch('services.replies_service.read_query')
    @patch('services.replies_service.update_query')
    def test_update_changesContent_andReturnsReply(self, mock_update, mock_read):
        mock_read.return_value = [ROW]

        result = replies_service.update(1, 'New text')

        self.assertEqual(('New text', 1), mock_update.call_args[0][1])
        self.assertEqual(Reply.from_query_result(*ROW), result)

    @patch('services.replies_service.update_query')
    def test_delete_callsDatabaseWithReplyId(self, mock_update):
        replies_service.delete(1)

        self.assertEqual((1,), mock_update.call_args[0][1])


if __name__ == '__main__':
    unittest.main()