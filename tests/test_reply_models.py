import unittest
from datetime import datetime

from pydantic import ValidationError

from data.models.reply import Reply, Vote, ReplyCreate, ReplyUpdate, VoteCreate


class ReplyCreate_Should(unittest.TestCase):

    def test_acceptsValidContent(self):
        self.assertEqual('Nice one', ReplyCreate(content='Nice one').content)

    def test_rejectsContentShorterThan2(self):
        with self.assertRaises(ValidationError):
            ReplyCreate(content='a')

    def test_rejectsContentLongerThan8192(self):
        with self.assertRaises(ValidationError):
            ReplyCreate(content='a' * 8193)

    def test_acceptsContentOfExactLimits(self):
        ReplyCreate(content='ab')
        ReplyCreate(content='a' * 8192)


class ReplyUpdate_Should(unittest.TestCase):

    def test_acceptsValidContent(self):
        self.assertEqual('Edited text', ReplyUpdate(content='Edited text').content)

    def test_rejectsContentShorterThan2(self):
        with self.assertRaises(ValidationError):
            ReplyUpdate(content='a')

    def test_rejectsContentLongerThan8192(self):
        with self.assertRaises(ValidationError):
            ReplyUpdate(content='a' * 8193)


class VoteCreate_Should(unittest.TestCase):

    def test_acceptsLike(self):
        self.assertEqual(1, VoteCreate(vote=1).vote)

    def test_acceptsDislike(self):
        self.assertEqual(-1, VoteCreate(vote=-1).vote)

    def test_rejectsZero(self):
        with self.assertRaises(ValidationError):
            VoteCreate(vote=0)

    def test_rejectsOtherNumbers(self):
        with self.assertRaises(ValidationError):
            VoteCreate(vote=2)


class FromQueryResult_Should(unittest.TestCase):

    def test_reply_buildsReplyFromRow(self):
        now = datetime(2026, 11, 27, 12, 0, 0)

        reply = Reply.from_query_result(1, 2, 3, 'A valid reply', now)

        self.assertEqual(Reply(reply_id=1, topic_id=2, author_id=3, content='A valid reply', created_at=now), reply)

    def test_vote_buildsVoteFromRow(self):
        vote = Vote.from_query_result(1, 2, -1)

        self.assertEqual(Vote(user_id=1, reply_id=2, vote=-1), vote)