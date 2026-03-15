"""Business logic layer for task management operations."""

from typing import Dict, List, Optional

from .models import Priority, Project, Task, TaskStatus, User
from .repository import ProjectRepository, TaskRepository, UserRepository
from .utils import generate_id, validate_email


class UserService:
    """Handles user-related business logic and validation."""

    def __init__(self, user_repo: UserRepository):
        self._repo = user_repo

    def create_user(self, username: str, email: str, display_name: str = "") -> User:
        if not validate_email(email):
            raise ValueError(f"Invalid email: {email}")
        user = User(id=generate_id(), username=username,
                     email=email, display_name=display_name)
        self._repo.add(user)
        return user

    def get_user(self, user_id: int) -> Optional[User]:
        return self._repo.get(user_id)

    def list_users(self) -> List[User]:
        return self._repo.list_all()


class TaskService:
    """Handles task-related business logic."""

    def __init__(self, task_repo: TaskRepository, user_repo: UserRepository):
        self._task_repo = task_repo
        self._user_repo = user_repo

    def create_task(self, title: str, description: str = "",
                    priority: Priority = Priority.MEDIUM,
                    assignee_id: Optional[int] = None) -> Task:
        assignee = None
        if assignee_id:
            assignee = self._user_repo.get(assignee_id)
            if not assignee:
                raise ValueError(f"User {assignee_id} not found")
        task = Task(id=generate_id(), title=title, description=description,
                    priority=priority, assignee=assignee)
        self._task_repo.add(task)
        return task

    def update_status(self, task_id: int, status: TaskStatus) -> Task:
        task = self._task_repo.get(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        task.status = status
        return task

    def get_tasks_by_user(self, user_id: int) -> List[Task]:
        return self._task_repo.find_by_assignee(user_id)

    def get_overdue_tasks(self) -> List[Task]:
        return [t for t in self._task_repo.list_all() if t.is_overdue()]


class ProjectService:
    """Handles project-related business logic."""

    def __init__(self, project_repo: ProjectRepository,
                 task_service: TaskService, user_repo: UserRepository):
        self._project_repo = project_repo
        self._task_service = task_service
        self._user_repo = user_repo

    def create_project(self, name: str, owner_id: int,
                       description: str = "") -> Project:
        owner = self._user_repo.get(owner_id)
        if not owner:
            raise ValueError(f"Owner {owner_id} not found")
        project = Project(id=generate_id(), name=name, owner=owner,
                          description=description)
        self._project_repo.add(project)
        return project

    def add_task_to_project(self, project_id: int, task_id: int) -> Project:
        project = self._project_repo.get(project_id)
        task = self._task_service._task_repo.get(task_id)
        if not project or not task:
            raise ValueError("Project or task not found")
        project.tasks.append(task)
        return project

    def get_project_summary(self, project_id: int) -> Dict:
        project = self._project_repo.get(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        return {
            "id": project.id,
            "name": project.name,
            "owner": project.owner.full_display(),
            "task_count": project.task_count(),
            "completion_rate": project.completion_rate(),
        }
