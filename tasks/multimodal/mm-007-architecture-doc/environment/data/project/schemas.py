"""Request and response schemas for API validation.

Uses Pydantic models to validate incoming request data and
serialize outgoing response data.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """Schema for creating a new user."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserResponse(BaseModel):
    """Schema for user data in API responses."""
    id: int
    username: str
    email: str
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PostCreate(BaseModel):
    """Schema for creating a new post."""
    title: str = Field(..., min_length=1, max_length=200)
    body: str = Field(..., min_length=1)


class PostUpdate(BaseModel):
    """Schema for updating an existing post."""
    title: Optional[str] = Field(None, max_length=200)
    body: Optional[str] = None
    status: Optional[str] = None


class PostResponse(BaseModel):
    """Schema for post data in API responses."""
    id: int
    title: str
    body: str
    status: str
    author_id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CommentCreate(BaseModel):
    """Schema for creating a comment."""
    body: str = Field(..., min_length=1)


class CommentResponse(BaseModel):
    """Schema for comment data in API responses."""
    id: int
    body: str
    post_id: int
    author_id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
