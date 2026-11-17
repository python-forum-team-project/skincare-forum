from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from data.models.reply import Reply


class Topic(BaseModel):
    topic_id: int
    author_id: int
    title: str
    content: str
    is_private: bool
    is_locked: bool

    @classmethod
    def from_query_result(cls, topic_id, author_id, title, content, is_private, is_locked):
        return cls(
            topic_id=topic_id,
            author_id=author_id,
            title=title,
            content=content,
            is_private=is_private,
            is_locked=is_locked
        )



class TopicUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=16, max_length=128)
    content: str = Field(min_length=32, max_length=8192)


class TopicCreate(TopicUpdate):
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