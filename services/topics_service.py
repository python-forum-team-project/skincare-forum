from data.models.topics import TopicResponse, FakeUser, TopicCreate, Topic, TopicUpdate
from data.models.user import User
from data.models.reply import Reply
from data.database import read_query, insert_query, update_query
from common import permissions, errors


def get_current_fake_user(): # това е докато се направи Оторизацията и Автентикацията
    return FakeUser(user_id=8, username='spammer', role='user', is_blocked=True)

# FakeUser(user_id=4, username='zarko123', role='user', is_blocked=False)




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
        return errors.TOPIC_NOT_FOUND

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



def create_topic(topic: TopicCreate, author: User): #FakeUser впоследствие ще се превърне в юзър
    if not permissions.can_create_topic(author):
        return errors.USER_IS_BLOCKED


    new_topic_id = insert_query('''
    INSERT INTO `topics` (author_id, title, content, is_private)
    VALUES
        (?, ?, ?, ?)
    ''', (author.user_id, topic.title, topic.content, topic.is_private))

    return get_topic_by_id(new_topic_id)


def update_topic(topic_id: int, updated_topic: TopicUpdate, user: User):
    topic = _get_topic_model(topic_id)

    if not topic:
        return errors.TOPIC_NOT_FOUND

    if not permissions.can_edit_topic(user, topic):
        return errors.CANNOT_EDIT_TOPIC

    update_query('''
    UPDATE topics
    SET 
        title = ?,
        content = ?
    WHERE topic_id = ?
    ''', (updated_topic.title, updated_topic.content, topic_id))

    return get_topic_by_id(topic_id)





def get_topics_count() -> int:
    result = read_query("SELECT COUNT(*) FROM topics")

    return result[0][0]


def _get_topic_model(topic_id: int) -> Topic | None:
    rows = read_query('''
        SELECT topic_id, author_id, title, content, is_private, is_locked
        FROM topics WHERE topic_id = ?''', (topic_id,))
    return next((Topic.from_query_result(*row) for row in rows), None)