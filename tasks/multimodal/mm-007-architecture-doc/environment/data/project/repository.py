"""Data access layer for persisting and retrieving projects and tasks."""

from typing import Dict, List, Optional

from .models import Project, Task, User


class UserRepository:
    """In-memory storage and retrieval for User entities."""

    def __init__(self):
        self._users: Dict[int, User] = {}

    def add(self, user: User) -> None:
        self._users[user.id] = user

    def get(self, user_id: int) -> Optional[User]:
        return self._users.get(user_id)

    def list_all(self) -> List[User]:
        return list(self._users.values())

    def delete(self, user_id: int) -> bool:
        return self._users.pop(user_id, None) is not None


class TaskRepository:
    """In-memory storage and retrieval for Task entities."""

    def __init__(self):
        self._tasks: Dict[int, Task] = {}

    def add(self, task: Task) -> None:
        self._tasks[task.id] = task

    def get(self, task_id: int) -> Optional[Task]:
        return self._tasks.get(task_id)

    def list_all(self) -> List[Task]:
        return list(self._tasks.values())

    def delete(self, task_id: int) -> bool:
        return self._tasks.pop(task_id, None) is not None

    def find_by_assignee(self, user_id: int) -> List[Task]:
        return [t for t in self._tasks.values()
                if t.assignee and t.assignee.id == user_id]


class ProjectRepository:
    """In-memory storage and retrieval for Project entities."""

    def __init__(self):
        self._projects: Dict[int, Project] = {}

    def add(self, project: Project) -> None:
        self._projects[project.id] = project

    def get(self, project_id: int) -> Optional[Project]:
        return self._projects.get(project_id)

    def list_all(self) -> List[Project]:
        return list(self._projects.values())

    def delete(self, project_id: int) -> bool:
        return self._projects.pop(project_id, None) is not None

    def find_by_owner(self, user_id: int) -> List[Project]:
        return [p for p in self._projects.values()
                if p.owner.id == user_id]
