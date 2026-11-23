from data.models.user import User
from data.models.topics import Topic
from data.models.reply import Reply



# In this file we have all user permission checks!!!



def can_create_topic(user: User) -> bool:
    if user.is_blocked is True:
        return False
    return True

def can_edit_topic(user: User, topic: Topic) -> bool:
    return (user is not None
            and not user.is_blocked
            and not topic.is_locked
            and user.user_id == topic.author_id)


def can_delete_topic(user: User, topic: Topic):
    if user.is_admin():
        return True
    if user.user_id == topic.author_id:
        return True
    return False

# All functions above are tested in test_permissions.py 


def can_lock_topic(user: User):
    return user.is_admin()


def can_view_topic(user: User | None, topic: Topic, member_ids: list[int]) -> bool:
    if not topic.is_private:
        return True
    if user is None:
        return False
    return (user.is_admin()
            or user.user_id == topic.author_id
            or user.user_id in member_ids)


def can_reply(user: User | None, topic: Topic, member_ids: list[int]) -> bool:
    return (user is not None
            and not user.is_blocked
            and not topic.is_locked
            and can_view_topic(user, topic, member_ids))


def can_vote(user: User | None, topic: Topic, member_ids: list[int]) -> bool:
    return (user is not None
            and not user.is_blocked
            and can_view_topic(user, topic, member_ids))


def can_edit_reply(user: User, reply: Reply) -> bool:
    return (user is not None
            and not user.is_blocked
            and user.user_id == reply.author_id)


def can_delete_reply(user: User, reply: Reply) -> bool:
    return (user is not None
            and (user.is_admin() or user.user_id == reply.author_id))