"""Business logic layer for the application.

Contains service classes that implement the core business rules
and orchestrate interactions between models and external systems.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from models import Comment, Post, User
from auth import hash_password, verify_password


class UserService:
    """Handles user-related business logic."""

    def __init__(self, db: Session):
        self.db = db

    def create_user(self, username: str, email: str, password: str) -> User:
        """Create a new user with hashed password."""
        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_user(self, user_id: int) -> Optional[User]:
        """Retrieve a user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()

    def list_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """List users with pagination."""
        return self.db.query(User).offset(skip).limit(limit).all()

    def authenticate(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user by username and password."""
        user = self.db.query(User).filter(User.username == username).first()
        if user and verify_password(password, user.password_hash):
            return user
        return None


class PostService:
    """Handles post-related business logic."""

    def __init__(self, db: Session):
        self.db = db

    def create_post(self, title: str, body: str, author_id: int) -> Post:
        """Create a new blog post."""
        post = Post(title=title, body=body, author_id=author_id)
        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)
        return post

    def get_post(self, post_id: int) -> Optional[Post]:
        """Retrieve a post by ID."""
        return self.db.query(Post).filter(Post.id == post_id).first()

    def list_posts(self, status: str = None, skip: int = 0, limit: int = 20) -> List[Post]:
        """List posts with optional status filter and pagination."""
        query = self.db.query(Post)
        if status:
            query = query.filter(Post.status == status)
        return query.offset(skip).limit(limit).all()

    def update_post(self, post_id: int, **kwargs) -> Optional[Post]:
        """Update a post's fields."""
        post = self.get_post(post_id)
        if post:
            for key, value in kwargs.items():
                if value is not None:
                    setattr(post, key, value)
            self.db.commit()
            self.db.refresh(post)
        return post


class CommentService:
    """Handles comment-related business logic."""

    def __init__(self, db: Session):
        self.db = db

    def create_comment(self, body: str, post_id: int, author_id: int) -> Comment:
        """Create a new comment on a post."""
        comment = Comment(body=body, post_id=post_id, author_id=author_id)
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        return comment

    def list_comments(self, post_id: int) -> List[Comment]:
        """List all comments for a given post."""
        return self.db.query(Comment).filter(Comment.post_id == post_id).all()
