from data.models import Topic, TopicCreate, TopicUpdate, FakeUser
from data.database import read_query, insert_query, update_query


def get_current_fake_user(): # това е докато се направи Оторизацията и Автентикацията
    return FakeUser(user_id=4, username='zarko123', role='user', is_blocked=False)


def get_topic_by_id(id: int):
    topic = read_query('''
    SELECT 
        t.topic_id,
        u.username AS `author`,
        t.title,
        t.content,
        t.created_at,
        t.is_private,
        t.is_locked
    FROM topics AS t
    JOIN users As u ON t.author_id = u.user_id
    WHERE topic_id = ?
    ''', (id,))

    return topic
