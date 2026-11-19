from services.users_service import get_all_users_count, get_active_users_count
from services.topics_service import get_topics_count
from services.replies_services import get_replies_count


def get_home_stats() -> dict:
    return {
        'users': get_all_users_count(),
        'active_users': get_active_users_count(),
        'topics': get_topics_count(),
        'replies': get_replies_count()
    }