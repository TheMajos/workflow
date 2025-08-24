from src.app import TaskManagerApp


if __name__ == "__main__":
    app = TaskManagerApp()
    # Start the app

    __import__("asyncio").run(app.start())
