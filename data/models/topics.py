from pydantic import BaseModel, Field
from datetime import datetime
from data.models.reply import Reply


class Topic(BaseModel):
    id: int
    author: str
    title: str
    content: str
    replies: list[Reply] = []



class TopicCreate(BaseModel):
    author_id: int
    title: str = Field(min_length=16, max_length=128)
    content: str = Field(min_length=32, max_length=8192)
    is_private: bool = False


class TopicUpdate(BaseModel):
    title: str = Field(min_length=16, max_length=128)
    content: str = Field(min_length=32, max_length=8192)
    is_private: bool = False


class TopicResponse(BaseModel):
    id: int
    author: str
    title: str
    content: str
    created_at: datetime
    replies: list[Reply] = []

    @classmethod
    def from_query_results(cls, id, author, title, content, created_at, replies):
        return cls(id=id, 
                   author=author, 
                   title=title, 
                   content=content,
                   created_at=created_at, 
                   replies=replies
                   )



# Това е само докато се направи изтински юзър и автентикация / оторизация
# Ползва се от Topics
class FakeUser(BaseModel): 
    user_id: int
    username: str
    role: str
    is_blocked: bool = False