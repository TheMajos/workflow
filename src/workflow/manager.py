from src.auth.jwt import JWTManager
from src.db.db import TaskRepository
from src.exc.excs import AuthenticationError
from src.models import CreateTask, UpdateTask
from pydantic import ValidationError

# class name should be the same as filename
class TaskService:
    def __init__(self, repo: TaskRepository, jwt_manager: JWTManager):
        self.repo = repo
        self.jwt_manager = jwt_manager

    def _authenticate_user(self):
        session, email = self.jwt_manager.refresher()
        if not session:
            raise AuthenticationError("User is not authenticated")
        return email

    async def get_task_info(self, id):
        email = self._authenticate_user()
        content = await self.repo.get_task_by_id(email, id)
        return content.get("info", {}) if content else "Task does not exist"

    async def add_task(self, task: dict):
        email = self._authenticate_user()
        try:
            task = CreateTask(**task)
            await self.repo.add_task_to_user(email, task.model_dump())
        except ValidationError as e:
            raise e

    async def update_task(self, id, task: dict):
        email = self._authenticate_user()
        try:
            task = UpdateTask(**task)
            task_data = task.model_dump()
            task_data["id"] = id

            replaced = await self.repo.replace_task_for_user(email, id, task_data)
            if replaced:
                return "Task was replaced"
            return "Invalid ID"
        except ValidationError as e:
            raise e

    async def delete_task(self, id):
        email = self._authenticate_user()
        is_deleted = await self.repo.delete_task_for_user(email, id)
        if is_deleted:
            return "Deleted Task"
        return "Invalid ID"

    async def list_tasks(self):
        parsed = []

        email = self._authenticate_user()
        tasks = await self.repo.get_active_tasks_for_user(email)
        for i in tasks:
            id = i.get("id")
            name = i.get("task")
            deadline = i.get("deadline")
            parsed.append(f"Task Name: {name} | ID: {id} | Deadline: {deadline}")

        return parsed
