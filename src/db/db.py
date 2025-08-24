from config import MONGO_DB_CONNECTION, MONGO_DB_NAME, MONGO_DB_COLLECTION
from typing import Optional
from src.utils.utils import filter_non_expired_tasks


class MongoHandler:
    _instance = None
    _client = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if MongoHandler._client is None:
            MongoHandler._client = MONGO_DB_CONNECTION

        self.client = MongoHandler._client
        self.db = self.client[MONGO_DB_NAME]
        self.collection = self.db[MONGO_DB_COLLECTION]

    async def insert(self, payload: dict):
        await self.collection.insert_one(payload)

    async def query(self, payload: dict) -> Optional[dict]:
        return await self.collection.find_one(payload)


class TaskRepository:
    _instance = None
    _client = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.collection = MongoHandler().collection

    # Procedure
    async def add_task_to_user(self, email: str, task: dict):
        await self.collection.update_one(
            {"email": email},  # find the user
            {"$push": {"tasks": task}},  # push new task into the tasks array
            upsert=True,  # create user document if it doesn't exist
        )

    # Procedure
    async def delete_task_for_user(self, email: str, task_id: str):
        """Remove a specific task from the user's task list based on task_id."""
        result = await self.collection.update_one(
            {
                "email": email,
                "tasks.id": task_id,
            },
            {"$pull": {"tasks": {"id": task_id}}},  # Remove the task with matching id
        )

        # Return whether the task was deleted based on the update result
        if result.modified_count > 0:
            return True
        return False

    # Procedure
    async def replace_task_for_user(self, email: str, task_id: str, update: dict):
        """Replace a specific task for the user based on task_id."""
        result = await self.collection.update_one(
            {"email": email, "tasks.id": task_id},  # Find the user + task
            {"$set": {"tasks.$": update}},
        )

        if result.modified_count > 0:
            return True  # Task was replaced
        return False  # Task not found or not modified

    async def get_active_tasks_for_user(self, email: str) -> list[dict]:
        """Fetch all non-expired tasks for a given user."""
        user = await self.collection.find_one({"email": email}, {"_id": 0, "tasks": 1})
        tasks = user.get("tasks", []) if user else []
        return filter_non_expired_tasks(tasks)

    async def get_task_by_id(self, email: str, task_id: str) -> dict | None:
        """Return a specific task for a user using MongoDB elemMatch."""
        user = await self.collection.find_one(
            {"email": email, "tasks.id": task_id},
            {"_id": 0, "tasks": {"$elemMatch": {"id": task_id}}},
        )
        if not user or "tasks" not in user or not user["tasks"]:
            return None

        return user["tasks"][0]
