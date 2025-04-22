from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List


class Book(BaseModel):
    title: str
    price: float = Field(..., ge=0)
    category: str
    url: str
    image_url: Optional[str] = None


class PaginatedBooksResponse(BaseModel):
    message: str
    total_books: int
    page: int
    page_size: int
    data: List[Book]


class HackerNewsStory(BaseModel):
    title: str
    url: str
    score: int = Field(..., ge=0)


class HackerNewsResponse(BaseModel):
    message: str
    data: List[HackerNewsStory]


class ScrapedBook(BaseModel):
    url: str
    title: str
    price: str
    category: str
    image_url: Optional[str] = None


class ScrapingResult(BaseModel):
    total_books: int
    books: List[ScrapedBook]


class HNStory(BaseModel):
    title: str
    url: HttpUrl
    score: int


class HNStoriesResponse(BaseModel):
    stories: List[HNStory]
    total: int
