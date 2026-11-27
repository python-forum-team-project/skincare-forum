from fastapi import APIRouter, HTTPException, status, Depends
from services import replies_service, votes_service
from data.models.reply import Reply, ReplyCreate, ReplyUpdate, VoteCreate
from data.models.user import User
from common import auth, permissions

replies_router = APIRouter(tags=['Replies'])


def _reply_or_404(reply_id: int):
    reply = replies_service.get_by_id(reply_id)
    if reply is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Reply with ID: ({reply_id}) was not found!')
    return reply


@replies_router.get('/topics/{topic_id}/replies')
def get_replies(topic_id: int):
    return replies_service.get_by_topic(topic_id)


@replies_router.post('/topics/{topic_id}/replies', status_code=status.HTTP_201_CREATED)
def create_reply(topic_id: int, body: ReplyCreate, user: User = Depends(auth.get_current_user)):
    reply = Reply(topic_id=topic_id, author_id=user.user_id, content=body.content)
    return replies_service.create(reply)


@replies_router.put('/replies/{reply_id}')
def update_reply(reply_id: int, body: ReplyUpdate, user: User = Depends(auth.get_current_user)):
    reply = _reply_or_404(reply_id)

    if not permissions.can_edit_reply(user, reply):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You cannot edit this reply!')

    return replies_service.update(reply_id, body.content)

@replies_router.delete('/replies/{reply_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_reply(reply_id: int, user: User = Depends(auth.get_current_user)):
    reply = _reply_or_404(reply_id)

    if not permissions.can_delete_reply(user, reply):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You cannot delete this reply!')

    replies_service.delete(reply_id)
    
@replies_router.get('/replies/{reply_id}/votes')
def get_votes(reply_id: int):
    _reply_or_404(reply_id)
    return votes_service.count_votes(reply_id)

@replies_router.put('/replies/{reply_id}/vote')
def vote_reply(reply_id: int, body: VoteCreate, user: User = Depends(auth.get_current_user)):
    _reply_or_404(reply_id)
    votes_service.vote(user.user_id, reply_id, body.vote)
    return votes_service.count_votes(reply_id)


@replies_router.delete('/replies/{reply_id}/vote', status_code=204)
def delete_vote(reply_id: int, user: User = Depends(auth.get_current_user)):
    _reply_or_404(reply_id)
    if votes_service.get_vote(user.user_id, reply_id) is None:
        raise HTTPException(status_code=404, detail='Vote not found')
    votes_service.remove_vote(user.user_id, reply_id)