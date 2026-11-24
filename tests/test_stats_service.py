import unittest
from unittest.mock import Mock, patch
from datetime import datetime

with patch.dict('os.environ', {'JWT_SECRET': 'test-secret'}):
    from services import stats_service
    from routers.api import home_routers
    from routers.web import web_home_routers
    NOW = datetime(2026, 11, 24, 12, 0, 0)


@patch('services.stats_service.get_replies_count')
@patch('services.stats_service.get_topics_count')
@patch('services.stats_service.get_active_users_count')
@patch('services.stats_service.get_all_users_count')
class GetHomeStats_Should(unittest.TestCase):

    def test_returnsCounts_fromAllServices(self, mock_users, mock_active, mock_topics, mock_replies):
        mock_users.return_value = 12
        mock_active.return_value = 8
        mock_topics.return_value = 5
        mock_replies.return_value = 20

        result = stats_service.get_home_stats()

        self.assertEqual({'users': 12, 'active_users': 8, 'topics': 5, 'replies': 20}, result)
        mock_users.assert_called_once_with()
        mock_active.assert_called_once_with()
        mock_topics.assert_called_once_with()
        mock_replies.assert_called_once_with()

    def test_returnsZeros_whenForumIsEmpty(self, mock_users, mock_active, mock_topics, mock_replies):
        mock_users.return_value = 0
        mock_active.return_value = 0
        mock_topics.return_value = 0
        mock_replies.return_value = 0

        self.assertEqual({'users': 0, 'active_users': 0, 'topics': 0, 'replies': 0}, stats_service.get_home_stats())


class HomeRouters_Should(unittest.TestCase):

    @patch('routers.api.home_routers.get_home_stats')
    def test_returnsStats_fromApi(self, mock_stats):
        mock_stats.return_value = {'users': 5, 'topics': 2, 'active_users': 4, 'replies': 8}

        self.assertEqual(mock_stats.return_value, home_routers.home())

    @patch('routers.web.web_home_routers.templates.TemplateResponse')
    @patch('routers.web.web_home_routers.get_web_current_user')
    @patch('routers.web.web_home_routers.get_home_stats')
    def test_passesStatsAndUser_toHomeTemplate(self, mock_stats, mock_user, mock_template):
        request = Mock()
        mock_stats.return_value = {'users': 5, 'topics': 2, 'active_users': 4, 'replies': 8}
        mock_user.return_value = None

        result = web_home_routers.index(request)

        self.assertEqual(mock_template.return_value, result)
        mock_template.assert_called_once_with(request=request, name='index.html',
                                              context={'stats': mock_stats.return_value, 'current_user': None})

class StatsTopics_Should(unittest.TestCase):

    @patch('services.stats_service.read_query')
    def test_getRecentTopics_returnsListOfDicts(self, mock_read):
        mock_read.return_value = [(1, 'Best SPF', 'anna', NOW)]

        result = stats_service.get_recent_topics()

        self.assertEqual(
            [{'topic_id': 1, 'title': 'Best SPF', 'author': 'anna', 'created_at': NOW}],
            result)

    @patch('services.stats_service.read_query')
    def test_getRecentTopics_returnsEmptyList_whenNoTopics(self, mock_read):
        mock_read.return_value = []

        self.assertEqual([], stats_service.get_recent_topics())

    @patch('services.stats_service.read_query')
    def test_getTopicsByReplies_returnsListWithRepliesCount(self, mock_read):
        mock_read.return_value = [(1, 'Best SPF', 'anna', NOW, 5)]

        result = stats_service.get_topics_by_replies()

        self.assertEqual(
            [{'topic_id': 1, 'title': 'Best SPF', 'author': 'anna',
              'created_on': NOW, 'replies_count': 5}],
            result)

    @patch('services.stats_service.read_query')
    def test_getTopicsByReplies_returnsEmptyList_whenNoTopics(self, mock_read):
        mock_read.return_value = []

        self.assertEqual([], stats_service.get_topics_by_replies())