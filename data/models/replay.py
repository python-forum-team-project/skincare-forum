from datetime import datetime
from pydantic import BaseModel



class Reply(BaseModel):
    reply_id: int
    topic_id: int
    author_id: int
    content: str
    created_at: datetime
    
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