"""API controller layer exposing task management operations."""

from typing import Any, Dict, List

from .models import Priority, TaskStatus
from .service import ProjectService, TaskService, UserService


class APIController:
    """HTTP-style controller that delegates to service layer.

    Accepts dict-based requests and returns dict-based responses,
    simulating a REST API without a web framework dependency.
    """

    def __init__(self, user_service: UserService, task_service: TaskService,
                 project_service: ProjectService):
        self._user_svc = user_service
        self._task_svc = task_service
        self._project_svc = project_service

    def create_user(self, data: Dict[str, Any]) -> Dict[str, Any]:
        user = self._user_svc.create_user(
            username=data["username"],
            email=data["email"],
            display_name=data.get("display_name", ""),
        )
        return {"id": user.id, "username": user.username, "email": user.email}

    def list_users(self) -> List[Dict[str, Any]]:
        return [{"id": u.id, "username": u.username, "email": u.email}
                for u in self._user_svc.list_users()]

    def create_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
        priority = Priority[data.get("priority", "MEDIUM").upper()]
        task = self._task_svc.create_task(
            title=data["title"],
            description=data.get("description", ""),
            priority=priority,
            assignee_id=data.get("assignee_id"),
        )
        return {"id": task.id, "title": task.title, "status": task.status.value}

    def update_task_status(self, task_id: int, status_str: str) -> Dict[str, Any]:
        status = TaskStatus(status_str)
        task = self._task_svc.update_status(task_id, status)
        return {"id": task.id, "status": task.status.value}

    def create_project(self, data: Dict[str, Any]) -> Dict[str, Any]:
        project = self._project_svc.create_project(
            name=data["name"],
            owner_id=data["owner_id"],
            description=data.get("description", ""),
        )
        return {"id": project.id, "name": project.name}

    def get_project_summary(self, project_id: int) -> Dict[str, Any]:
        return self._project_svc.get_project_summary(project_id)
