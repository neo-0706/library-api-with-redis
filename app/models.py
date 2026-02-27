from pydantic import BaseModel
from typing import List , Optional

class AuthorResponse(BaseModel):
    id: int
    author_name: str
    book_count: int

    class Config:
        from_attributes = True

class SearchQuery(BaseModel):
    q: str
    limit: Optional[int] = 10

    
class BookResponse(BaseModel):
    id: int
    title: str
