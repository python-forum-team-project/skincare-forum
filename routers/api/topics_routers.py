from fastapi import APIRouter, HTTPException, status, Depends
from services import topics_service
from data.models.topics import TopicCreate, TopicUpdate, TopicLock
from data.models.user import User
from common import errors, auth

topics_router = APIRouter(prefix='/topics', tags=['Topics'])


@topics_router.get('/{topic_id}')
def get_topic_by_id(id: int):
    topic = topics_service.get_topic_by_id(id)

    if topic is errors.TOPIC_NOT_FOUND:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Topic with ID: ({id}) was not found!')

    return topic


@topics_router.post('', status_code=status.HTTP_201_CREATED)
def create_topic(topic: TopicCreate, author: User = Depends(auth.get_current_user)):
    new_topic = topics_service.create_topic(topic, author)

    if new_topic is errors.USER_IS_BLOCKED:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=('This user is prohibited from creating new topics!'))

    return new_topic


@topics_router.put('/{topic_id}')
def update_topic(topic_id:int, updated_topic: TopicUpdate, user: User = Depends(auth.get_current_user)):
    topic_update = topics_service.update_topic(topic_id, updated_topic, user)

    if topic_update == errors.TOPIC_NOT_FOUND:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Topic with ID: ({topic_id}) was not found!')

    if topic_update == errors.CANNOT_EDIT_TOPIC:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=('You cannot edit this topic!'))

    return topic_update


@topics_router.delete('/{topic_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_topic(topic_id: int, user: User = Depends(auth.get_current_user)):
    result = topics_service.delete_topic(topic_id, user)

    if result == errors.CANNOT_DELETE_TOPIC:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=('You cannot delete this topic!'))
    
    if result == errors.TOPIC_NOT_FOUND:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Topic with ID: ({topic_id}) was not found!')



@topics_router.put('/{topic_id}/lock')
def set_topic_lock(topic_id: int, lock: TopicLock, user: User = Depends(auth.get_current_user)):
    result = topics_service.set_topic_lock(topic_id, lock.is_locked, user)

    if result == errors.TOPIC_NOT_FOUND:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Topic with ID: ({topic_id}) was not found!')

    if result == errors.CANNOT_LOCK_TOPIC:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Only admins can lock/unlock topics')

    return result