from src.terminal.app import TaskManagerApp


if __name__ == "__main__":
    app = TaskManagerApp()
    # Start the app
    import asyncio

    asyncio.run(app.start())
