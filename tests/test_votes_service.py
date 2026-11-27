import unittest
from unittest.mock import patch

from data.models.reply import Vote
from services import votes_service


class VotesService_Should(unittest.TestCase):

    @patch('services.votes_service.read_query')
    def test_getVote_returnsVote_whenExists(self, mock_read):
        mock_read.return_value = [(1, 2, 1)]

        result = votes_service.get_vote(1, 2)

        self.assertEqual(Vote(user_id=1, reply_id=2, vote=1), result)

    @patch('services.votes_service.read_query')
    def test_getVote_returnsNone_whenMissing(self, mock_read):
        mock_read.return_value = []

        result = votes_service.get_vote(1, 2)

        self.assertIsNone(result)

    @patch('services.votes_service.read_query')
    @patch('services.votes_service.insert_query')
    def test_vote_savesAndReturnsVote(self, mock_insert, mock_read):
        mock_read.return_value = [(1, 2, -1)]

        result = votes_service.vote(1, 2, -1)

        mock_insert.assert_called_once()
        self.assertEqual(Vote(user_id=1, reply_id=2, vote=-1), result)

    @patch('services.votes_service.read_query')
    def test_countVotes_returnsLikesAndDislikes(self, mock_read):
        mock_read.return_value = [(3, 1)]

        result = votes_service.count_votes(2)

        self.assertEqual({'likes': 3, 'dislikes': 1}, result)

    @patch('services.votes_service.read_query')
    def test_countVotes_returnsZeros_whenNoVotes(self, mock_read):
        mock_read.return_value = [(None, None)]

        result = votes_service.count_votes(2)

        self.assertEqual({'likes': 0, 'dislikes': 0}, result)
        
        
    @patch('services.votes_service.update_query')
    def test_removeVote_deletesTheVote(self, mock_update):
        votes_service.remove_vote(1, 2)

        mock_update.assert_called_once()
        self.assertEqual((1, 2), mock_update.call_args[0][1])