



# In this file we have all user permission checks!!!



def can_create_topic(user) -> bool:
    if user.is_blocked is True:
        return False
    return True


def can_edit_topic(user, topic) -> bool:
    return (user is not None
            and not user.is_blocked
            and not topic.is_locked
            and user.user_id == topic.author_id)