from datetime import datetime
from pydantic import BaseModel, Field
from typing import Literal



class Reply(BaseModel):
    reply_id: int | None = None
    topic_id: int
    author_id: int
    content: str
    created_at: datetime | None = None
    
    @classmethod
    def from_query_result(cls, reply_id, topic_id, author_id, content, created_at):
        return cls(
            reply_id=reply_id,
            topic_id=topic_id,
            author_id=author_id,
            content=content,
            created_at=created_at)
        
class Vote(BaseModel):
    user_id: int
    reply_id: int
    vote: int
    
    @classmethod
    def from_query_result(cls, user_id, reply_id, vote):
        return cls(
            user_id=user_id,
            reply_id=reply_id,
            vote=vote
        )
        


class ReplyCreate(BaseModel):
    content: str = Field(min_length=2, max_length=8192)


class ReplyUpdate(BaseModel):
    content: str = Field(min_length=2, max_length=8192)


class VoteCreate(BaseModel):
    vote: Literal[1, -1]