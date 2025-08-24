from src.app import TaskManagerApp


if __name__ == "__main__":
    app = TaskManagerApp()

    __import__("asyncio").run(app.start())
