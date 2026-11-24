from services.users_service import get_all_users_count, get_active_users_count
from services.topics_service import get_topics_count
from services.replies_services import get_replies_count
from data.database import read_query


def get_home_stats() -> dict:
    return {
        'users': get_all_users_count(),
        'active_users': get_active_users_count(),
        'topics': get_topics_count(),
        'replies': get_replies_count()
    }


def get_recent_topics():
    sql = '''
    SELECT t.topic_id, t.title, u.username AS author, t.created_at
    FROM topics t
    JOIN users u on u.user_id = t.author_id
    WHERE t.is_private = FALSE
    ORDER BY t.created_at DESC
    LIMIT 10
    '''
    data = read_query(sql)
    return [
        {
            'topic_id' : topic_id,
            'title': title,
            'author': author,
            'created_at': created_at
        }
        for topic_id, title, author, created_at in data
    ]
    
    
def get_topics_by_replies():
    sql = '''
    SELECT t.topic_id, t.title, u.username AS author, t.created_at, COUNT(r.reply_id) AS replies_count
    FROM topics t
    JOIN users u ON t.author_id = u.user_id
    LEFT JOIN replies r ON r.topic_id = t.topic_id
    WHERE t.is_private = FALSE
    GROUP BY t.topic_id, t.title, u.username, t.created_at
    ORDER BY replies_count DESC
    LIMIT 10
    '''
    data = read_query(sql)
    return [
        {
            'topic_id': topic_id,
            'title': title,
            'author': username,
            'created_at': created_at,
            'replies_count': replies_count
        } for topic_id, title, username, created_at, replies_count in data
    ]


