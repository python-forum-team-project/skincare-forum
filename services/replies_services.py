from data.database import read_query, insert_query, update_query
from data.models.reply import Reply

_DATA_REPLY = 'reply_id, topic_id, author_id, content, created_at'


def get_by_topic(topic_id):
    sql = f'''
        SELECT {_DATA_REPLY}
        FROM replies
        WHERE topic_id = ?
        ORDER BY created_at
        '''
    data = read_query(sql, (topic_id,))
    return [Reply.from_query_result(*row) for row in data]


def get_by_id(reply_id):
    sql = f'''
        SELECT {_DATA_REPLY}
        FROM replies
        WHERE reply_id = ?
        '''
    data = read_query(sql, (reply_id,))
    return next((Reply.from_query_result(*row) for row in data), None)


def exists(reply_id):
    sql = '''
        SELECT 1 FROM replies
        WHERE reply_id = ?
        '''
    data = read_query(sql, (reply_id,))
    return any(data)


def create(reply):
    sql = '''
        INSERT INTO replies
        SET topic_id = ?, author_id = ?, content = ?
        '''
    new_id = insert_query(sql, (reply.topic_id, reply.author_id, reply.content))
    return get_by_id(new_id)


def get_replies_count() -> int:
    result = read_query("SELECT COUNT(*) FROM replies")
    return result[0][0]

def update(reply_id, content):
    sql = '''
           UPDATE replies
           SET content = ?
           WHERE reply_id = ?
           '''
    update_query(sql, (content, reply_id,))
    return get_by_id(reply_id)

def delete(reply_id):
    sql = '''
           DELETE FROM replies
           WHERE reply_id = ?
           '''
    update_query(sql, (reply_id,))

def get_by_author(author_id):
    sql = f'''
           SELECT {_DATA_REPLY}
           FROM replies
           WHERE author_id = ?
           ORDER BY created_at DESC
           '''
    data = read_query(sql, (author_id,))
    return [Reply.from_query_result(*row) for row in data]

def belongs_to_topic(reply_id, topic_id):
    sql = '''
    SELECT 1
    FROM replies
    WHERE reply_id = ? AND topic_id = ?
           '''
    data = read_query(sql, (reply_id, topic_id))
    return any(data)