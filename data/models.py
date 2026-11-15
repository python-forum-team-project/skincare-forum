from datetime import datetime
from pydantic import BaseModel, constr, StringConstraints
from typing_extensions import Annotated


class Category(BaseModel):
    id: int | None
    name: str


class Product(BaseModel):
    id: int | None
    name: str
    description: str
    price: float
    category_id: int

    @classmethod
    def from_query_result(cls, id, name, description, price, category_id):
        return cls(
            id=id,
            name=name,
            description=description,
            price=price,
            category_id=category_id)



class Role:
    CUSTOMER = 'customer'
    ADMIN = 'admin'

class User(BaseModel):
    id: int | None
    username: Annotated[str, StringConstraints(pattern=r'^\w{2,30}$')]
    password: str
    role: str

    def is_admin(self):
        return self.role == Role.ADMIN

    @classmethod
    def from_query_result(cls, id, username, password, role):
        return cls(
            id=id,
            username=username,
            password=password,
            role=role)


class LoginData(BaseModel):
    username: Annotated[str, StringConstraints(pattern=r'^\w{2,30}$')]
    password: str



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
            reply_id=reply_id
            vote=vote,
        )