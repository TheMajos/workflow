import json
from datetime import datetime


def save_jwt(jwt_data: str):
    save_to_file(jwt_data)


# Procedure
def save_to_file(x: str):
    with open("credentials.json", "w") as file:
        json.dump(x, file)


def grab_jwt():
    try:
        with open("credentials.json", "r") as f:
            data = json.load(f)
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def filter_non_expired_tasks(tasks: list[dict]) -> list[dict]:
    """Return only tasks with deadlines today or in the future."""
    today = datetime.today().date()
    filtered = []

    for task in tasks:
        due_str = task.get("deadline")
        try:
            due_date = datetime.strptime(due_str, "%Y-%m-%d").date()
            if due_date >= today:
                filtered.append(task)
        except (ValueError, TypeError):
            continue  # skip invalid or missing dates

    return filtered
