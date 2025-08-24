import os
import sys
import time
from pydantic import ValidationError
from src.auth.auth import Authentication
from src.exc.auth import (
    RateLimitError,
    UserDoesNotExists,
    UserExists,
    PasswordTooShort,
    InvalidEmail,
    PasswordTooLong,
    EmailTooLong,
)
from src.workflow.manager import TaskService
from src.db.db import TaskRepository
from src.auth.jwt import JWTManager


class TaskManagerApp:
    def __init__(self):
        self.auth = Authentication()
        self.jwt_manager = JWTManager()
        self.task_repo = TaskRepository()
        self.task_service = TaskService(self.task_repo, self.jwt_manager)

    def clear_screen(self):
        os.system("cls" if os.name == "nt" else "clear")

    def exit_program(self):
        self.clear_screen()
        print("\nGoodbye.")
        time.sleep(1.5)
        sys.exit()

    async def start(self):
        while True:
            choice = input("[1]: Login\n[2]: Register\n[3]: Exit\n\nChoose: ").strip()

            if choice == "1":
                self.clear_screen()
                await self.login_screen()
            elif choice == "2":
                self.clear_screen()
                await self.register_screen()
            elif choice == "3":
                self.exit_program()
            else:
                self.clear_screen()

    async def login_screen(self):

        while True:
            print("--- Login ---")
            email = input("Enter your email: ").strip()
            password = input("Enter your password: ").strip()

            try:
                success = await self.auth.login(email, password)

                if success:
                    print("\nSuccessful Login")
                    time.sleep(1)
                    self.clear_screen()
                    await self.menu()
                    return

                retries += 1
                print("\nPassword is incorrect")
                time.sleep(1)
                self.clear_screen()

            except RateLimitError:
                print("\nYou are being rate-limited. Try again later.")
                time.sleep(1.5)
                self.clear_screen()
                return

            except UserDoesNotExists:
                retries += 1
                print("\nUser does not exist")
                time.sleep(1)
                self.clear_screen()

            except ValidationError as e:
                retries += 1
                print(f"\nValidation Error: {e}")
                time.sleep(1)
                self.clear_screen()

    async def register_screen(self):
        retries = 0

        while True:
            print("--- Register ---")
            email = input("Enter your email: ").strip()
            password = input("Enter your password: ").strip()

            try:
                await self.auth.register(email, password)
                print("\nRegistered successfully!")
                time.sleep(1)
                self.clear_screen()
                print("\nRedirecting to Login...")
                time.sleep(1)
                self.clear_screen()
                await self.login_screen()
                return

            except RateLimitError:
                print("\nYou are being rate-limited. Try again later.")
                time.sleep(1.5)
                self.clear_screen()
                return

            except UserExists:
                retries += 1
                print("\nUser already exists.")
                time.sleep(1)
                self.clear_screen()

            except PasswordTooShort:
                retries += 1
                print("\nPassword must be 8 characters or longer.")
                time.sleep(1)
                self.clear_screen()

            except InvalidEmail:
                retries += 1
                print("\nInvalid email format.")
                time.sleep(1)
                self.clear_screen()

            except PasswordTooLong:
                retries += 1
                print("\nPassword must be under 255 characters.")
                time.sleep(1)
                self.clear_screen()

            except EmailTooLong:
                retries += 1
                print("\nEmail must be under 255 characters.")
                time.sleep(1)
                self.clear_screen()

            except ValidationError as e:
                retries += 1
                print(f"\nValidation Error: {e}")
                time.sleep(1)
                self.clear_screen()

    async def menu(self):
        while True:
            print("--- Main Menu ---")
            print("[1]: List Tasks")
            print("[2]: Create Task")
            print("[3]: Delete Task")
            print("[4]: Update Task")
            print("[5]: Check Task Content")
            print("[6]: Exit")
            choice = input("\nChoose an option: ").strip()

            if choice == "1":
                await self.list_tasks()

            if choice == "2":
                await self.create_task()

            if choice == "3":
                await self.delete_task()

            if choice == "4":
                await self.update_task()

            if choice == "5":
                await self.get_task_content()

            if choice == "6":
                self.exit_program()

            else:
                self.clear_screen()

    async def list_tasks(self):
        self.clear_screen()
        tasks = await self.task_service.list_tasks()
        print("--- Your Tasks ---\n")
        if tasks:
            for task in tasks:
                print(task)
        else:
            print("No tasks found.")
        input("\nPress Enter to return to menu...")
        self.clear_screen()

    async def create_task(self):
        self.clear_screen()
        print("--- Create Task ---\n")

        task_name = input("Task Name: ").strip()
        info = input("Information: ").strip()
        deadline = input("Deadline (YYYY-MM-DD): ").strip()

        try:
            await self.task_service.add_task(
                {"task": task_name, "info": info, "deadline": deadline}
            )
        except ValidationError:
            print("\nSomething must be wrong, try again.")
            time.sleep(1)
            self.clear_screen()
            return
        print("\nAdded Task")
        input("\nPress Enter to return to menu...")
        self.clear_screen()

    async def delete_task(self):
        self.clear_screen()
        print("--- Delete Task ---\n")
        task_id = input("Task ID: ").strip()

        deletion = await self.task_service.delete_task(task_id)
        print(f"\n{deletion}")
        input("\nPress Enter to return to menu...")
        self.clear_screen()

    async def update_task(self):
        self.clear_screen()
        print("--- Update Task ---\n")

        task_id = input("Task ID: ").strip()
        task_name = input("Task Name: ").strip()
        info = input("Information: ").strip()
        deadline = input("Deadline (YYYY-MM-DD): ").strip()

        try:
            updated = await self.task_service.update_task(
                task_id, {"task": task_name, "info": info, "deadline": deadline}
            )
            print(f"\n{updated}")
        except ValidationError:
            print("\nSomething must be wrong, try again.")
            time.sleep(1)
            self.clear_screen()
            return
        input("\nPress Enter to return to menu...")
        self.clear_screen()

    async def get_task_content(self):
        self.clear_screen()
        print("--- Get Task Content ---\n")
        task_id = input("Task ID: ")

        content = await self.task_service.get_task_info(task_id)

        print(f"\n{content}")
        input("\nPress Enter to return to menu...")
        self.clear_screen()
