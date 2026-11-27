import unittest
from unittest.mock import patch

from fastapi import HTTPException

with patch.dict('os.environ', {'JWT_SECRET': 'test-secret'}):
    from routers.api import replies_routers, stats_routers

from data.models.reply import Reply, ReplyCreate, ReplyUpdate, VoteCreate
from data.models.user import User


def make_user(user_id=4):
    return User(user_id=user_id, username='test_user', role_name='user', is_blocked=False)


def make_reply(author_id=4):
    return Reply(reply_id=1, topic_id=1, author_id=author_id, content='A valid reply')


@patch('routers.api.replies_routers.replies_service')
class RepliesRouters_Should(unittest.TestCase):

    def test_getReplies_returnsRepliesOfTopic(self, mock_service):
        mock_service.get_by_topic.return_value = [make_reply()]

        result = replies_routers.get_replies(1)

        self.assertEqual([make_reply()], result)
        mock_service.get_by_topic.assert_called_once_with(1)

    def test_createReply_setsTopicAndAuthor(self, mock_service):
        mock_service.create.return_value = make_reply()

        result = replies_routers.create_reply(1, ReplyCreate(content='Nice one'), make_user(user_id=4))

        created = mock_service.create.call_args[0][0]
        self.assertEqual(1, created.topic_id)
        self.assertEqual(4, created.author_id)
        self.assertEqual('Nice one', created.content)
        self.assertEqual(mock_service.create.return_value, result)

    def test_updateReply_updatesReply_whenUserIsAuthor(self, mock_service):
        mock_service.get_by_id.return_value = make_reply(author_id=4)
        mock_service.update.return_value = make_reply()

        result = replies_routers.update_reply(1, ReplyUpdate(content='Edited text'), make_user(user_id=4))

        mock_service.update.assert_called_once_with(1, 'Edited text')
        self.assertEqual(mock_service.update.return_value, result)

    def test_updateReply_raises403_whenUserIsNotAuthor(self, mock_service):
        mock_service.get_by_id.return_value = make_reply(author_id=4)

        with self.assertRaises(HTTPException) as ctx:
            replies_routers.update_reply(1, ReplyUpdate(content='Edited text'), make_user(user_id=5))

        self.assertEqual(403, ctx.exception.status_code)
        mock_service.update.assert_not_called()

    def test_updateReply_raises404_whenReplyIsMissing(self, mock_service):
        mock_service.get_by_id.return_value = None

        with self.assertRaises(HTTPException) as ctx:
            replies_routers.update_reply(1, ReplyUpdate(content='Edited text'), make_user())

        self.assertEqual(404, ctx.exception.status_code)

    @patch('routers.api.replies_routers.votes_service')
    def test_voteReply_savesVoteAndReturnsCounts(self, mock_votes, mock_service):
        mock_service.get_by_id.return_value = make_reply()
        mock_votes.count_votes.return_value = {'likes': 1, 'dislikes': 0}

        result = replies_routers.vote_reply(1, VoteCreate(vote=1), make_user(user_id=4))

        mock_votes.vote.assert_called_once_with(4, 1, 1)
        self.assertEqual({'likes': 1, 'dislikes': 0}, result)

    @patch('routers.api.replies_routers.votes_service')
    def test_deleteVote_removesVote_whenVoteExists(self, mock_votes, mock_service):
        mock_service.get_by_id.return_value = make_reply()
        mock_votes.get_vote.return_value = object()

        replies_routers.delete_vote(1, make_user(user_id=4))

        mock_votes.remove_vote.assert_called_once_with(4, 1)

    @patch('routers.api.replies_routers.votes_service')
    def test_deleteVote_raises404_whenNoVote(self, mock_votes, mock_service):
        mock_service.get_by_id.return_value = make_reply()
        mock_votes.get_vote.return_value = None

        with self.assertRaises(HTTPException) as ctx:
            replies_routers.delete_vote(1, make_user())

        self.assertEqual(404, ctx.exception.status_code)
        mock_votes.remove_vote.assert_not_called()


@patch('routers.api.stats_routers.stats_service')
class StatsRouters_Should(unittest.TestCase):

    def test_homeStats_returnsServiceResult(self, mock_service):
        mock_service.get_home_stats.return_value = {'users': 1}

        self.assertEqual({'users': 1}, stats_routers.home_stats())

    def test_recentTopics_returnsServiceResult(self, mock_service):
        mock_service.get_recent_topics.return_value = [{'topic_id': 1}]

        self.assertEqual([{'topic_id': 1}], stats_routers.recent_topics())

    def test_topTopics_returnsServiceResult(self, mock_service):
        mock_service.get_topics_by_replies.return_value = [{'topic_id': 2}]

        self.assertEqual([{'topic_id': 2}], stats_routers.top_topics())