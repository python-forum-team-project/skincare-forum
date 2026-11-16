from data.models.topics import TopicResponse, FakeUser
from data.models.reply import Reply
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
        t.created_at
    FROM topics AS t
    JOIN users AS u ON t.author_id = u.user_id
    WHERE t.topic_id = ?
    ''', (id,))

    if not topic:
        return None

    topic_replies = read_query('''
    SELECT 
        r.reply_id, 
        r.topic_id, 
        r.author_id,
        r.content,
        r.created_at
    FROM replies AS r
    WHERE r.topic_id = ?
    ORDER BY r.created_at
    ''', (id,)) #после ще променим author_id на username

    all_topic_replies = [Reply.from_query_result(*row) for row in topic_replies]

    return TopicResponse.from_query_results(*topic[0], replies=all_topic_replies)