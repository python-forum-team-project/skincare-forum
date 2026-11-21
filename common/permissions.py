from data.models.user import User
from data.models.topics import Topic



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