from fastapi import APIRouter, HTTPException, status, Depends
from services import replies_services, votes_service
from data.models.reply import Reply, ReplyCreate, ReplyUpdate, VoteCreate
from data.models.user import User
from common import auth, permissions

replies_router = APIRouter(tags=['Replies'])


def _reply_or_404(reply_id: int):
    reply = replies_services.get_by_id(reply_id)
    if reply is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Reply with ID: ({reply_id}) was not found!')
    return reply


@replies_router.get('/topics/{topic_id}/replies')
def get_replies(topic_id: int):
    return replies_services.get_by_topic(topic_id)


@replies_router.post('/topics/{topic_id}/replies', status_code=status.HTTP_201_CREATED)
def create_reply(topic_id: int, body: ReplyCreate, user: User = Depends(auth.get_current_user)):
    reply = Reply(topic_id=topic_id, author_id=user.user_id, content=body.content)
    return replies_services.create(reply)


@replies_router.put('/replies/{reply_id}')
def update_reply(reply_id: int, body: ReplyUpdate, user: User = Depends(auth.get_current_user)):
    reply = _reply_or_404(reply_id)

    if not permissions.can_edit_reply(user, reply):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You cannot edit this reply!')

    return