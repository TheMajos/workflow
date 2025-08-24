# This file should be in src
from src.app import TaskManagerApp


if __name__ == "__main__":
    app = TaskManagerApp()

    # Only use __import__ when metaprogramming
    __import__("asyncio").run(app.start())
