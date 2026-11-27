from data.database import read_query, insert_query, update_query
from data.models.reply import Vote

_VOTES_DATA = 'user_id, reply_id, vote'


def get_vote(user_id, reply_id):
    sql = f'''
        SELECT {_VOTES_DATA}
        FROM reply_votes
        WHERE user_id = ? AND reply_id = ?
        '''
    data = read_query(sql, (user_id, reply_id))
    return next((Vote.from_query_result(*row) for row in data), None)


def vote(user_id, reply_id, value):
    sql = '''
        INSERT INTO reply_votes
        SET user_id = ?, reply_id = ?, vote = ?
        ON DUPLICATE KEY UPDATE vote = ?
        '''
    insert_query(sql, (user_id, reply_id, value, value))
    return get_vote(user_id, reply_id)


def count_votes(reply_id):
    sql = '''
        SELECT SUM(vote = 1), SUM(vote = -1)
        FROM reply_votes
        WHERE reply_id = ?
        '''
    data = read_query(sql, (reply_id,))
    likes, dislikes = data[0]
    return {'likes': int(likes or 0), 'dislikes': int(dislikes or 0)}

def remove_vote(user_id, reply_id):
    sql = 'DELETE FROM reply_votes WHERE user_id = ? AND reply_id = ?'
    update_query(sql, (user_id, reply_id))