from fastapi import APIRouter, HTTPException, status
from services import topics_service
from data.models.topics import TopicResponse

topics_router = APIRouter(prefix='/topics', tags=['Topics'])


@topics_router.get('/{id}')
def get_topic_by_id(id: int):
    topic = topics_service.get_topic_by_id(id)

    if topic is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Topic with ID: ({id}) was not found!')

    return topic