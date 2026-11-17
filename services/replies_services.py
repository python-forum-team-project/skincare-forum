from data.database import read_query
from data.models import Reply

# get_by_id(reply_id)	One reply, or None if it doesn’t exist
# create(reply)	Adds a reply and returns it with its new id
# exists(reply_id)

_DATA_REPLY = 'reply_id, topic_id, author_id, content, created_at'
def get_by_topic(topic_id):
    reply = ('''
        SELECT f{_DATA_REPLY}
        FROM replies
        WHERE topic_id = ?
        ORDER BY created_at
        '''
    )
    data = read_query(reply, (topic_id,) )
    return [Reply.from_query_result(*row) for row in data]


def get_replies_count() -> int:
    result = read_query("SELECT COUNT(*) FROM replies")

    return result[0][0]