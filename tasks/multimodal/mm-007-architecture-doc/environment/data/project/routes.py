"""API route handlers for the web application.

Defines FastAPI route handlers that process HTTP requests,
delegate to service layer, and return responses.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from schemas import (
    CommentCreate,
    CommentResponse,
    PostCreate,
    PostResponse,
    PostUpdate,
    UserCreate,
    UserResponse,
)
from services import CommentService, PostService, UserService
from auth import get_current_user

router = APIRouter()


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    service = UserService(db)
    user = service.create_user(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
    )
    return user


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get a user by ID."""
    service = UserService(db)
    user = service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/users", response_model=List[UserResponse])
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all users with pagination."""
    service = UserService(db)
    return service.list_users(skip=skip, limit=limit)


@router.post("/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(
    post_data: PostCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new blog post (authenticated)."""
    service = PostService(db)
    return service.create_post(
        title=post_data.title, body=post_data.body, author_id=current_user.id
    )


@router.get("/posts/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    """Get a post by ID."""
    service = PostService(db)
    post = service.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.get("/posts", response_model=List[PostResponse])
def list_posts(
    status_filter: str = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """List posts with optional status filter."""
    service = PostService(db)
    return service.list_posts(status=status_filter, skip=skip, limit=limit)


@router.put("/posts/{post_id}", response_model=PostResponse)
def update_post(
    post_id: int,
    post_data: PostUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update an existing post (authenticated)."""
    service = PostService(db)
    post = service.update_post(post_id, **post_data.dict(exclude_unset=True))
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.post("/posts/{post_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    post_id: int,
    comment_data: CommentCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a comment to a post (authenticated)."""
    service = CommentService(db)
    return service.create_comment(
        body=comment_data.body, post_id=post_id, author_id=current_user.id
    )


@router.get("/posts/{post_id}/comments", response_model=List[CommentResponse])
def list_comments(post_id: int, db: Session = Depends(get_db)):
    """List all comments for a post."""
    service = CommentService(db)
    return service.list_comments(post_id=post_id)
