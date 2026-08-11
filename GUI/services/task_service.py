from typing import List, Dict, Any, Optional
from repositories.excel_repository import ExcelRepository
from utils.constants import SHEETS, TASK_STATUSES, ACTIVE_TASK_STATUSES, TASK_STATUS_ALIASES
from utils.datetime_utils import now_str


class TaskService:
    def __init__(self, repo: ExcelRepository):
        self.repo = repo

    def normalize_status(self, status: str) -> str:
        status = (status or "").strip()
        return TASK_STATUS_ALIASES.get(status, status)

    def add_task(self, project_id: str, title: str, description: str = "", status: str = "TO DO") -> str:
        if not project_id:
            raise ValueError("Project is required.")
        title = title or ""
        description = description or ""
        if not title.strip():
            raise ValueError("Task title is required.")
        status = self.normalize_status(status)
        if status not in TASK_STATUSES:
            raise ValueError("Invalid task status.")
        if not self.repo.get_by_id(SHEETS["projects"], "project_id", project_id):
            raise ValueError("Project not found.")
        task_id = self.repo.next_id("task", "T")
        timestamp = now_str()
        completed_at = timestamp if status in ["COMPLETED", "MILESTONE"] else ""
        self.repo.append_row(SHEETS["tasks"], {
            "task_id": task_id,
            "project_id": project_id,
            "title": title.strip(),
            "description": description.strip(),
            "status": status,
            "created_at": timestamp,
            "updated_at": timestamp,
            "completed_at": completed_at,
        })
        return task_id

    def list_tasks(self, project_id: str = "", status: str = "") -> List[Dict[str, Any]]:
        tasks = self.repo.read_table(SHEETS["tasks"])
        for task in tasks:
            task["status"] = self.normalize_status(task.get("status", ""))
            task["title"] = task.get("title") or ""
            task["description"] = task.get("description") or ""
        if project_id:
            tasks = [t for t in tasks if t.get("project_id") == project_id]
        status = self.normalize_status(status)
        if status == "ACTIVE":
            tasks = [t for t in tasks if t.get("status") in ACTIVE_TASK_STATUSES]
        elif status:
            tasks = [t for t in tasks if t.get("status") == status]
        return sorted(tasks, key=lambda t: str(t.get("created_at", "")), reverse=True)

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        task = self.repo.get_by_id(SHEETS["tasks"], "task_id", task_id)
        if task:
            task["status"] = self.normalize_status(task.get("status", ""))
            task["title"] = task.get("title") or ""
            task["description"] = task.get("description") or ""
        return task

    def update_task(self, task_id: str, title: str, description: str, status: str) -> None:
        task = self.get_task(task_id)
        if not task:
            raise ValueError("Task not found.")

        title = title if title is not None else task.get("title", "")
        description = description if description is not None else task.get("description", "")
        title = title or ""
        description = description or ""

        # Prevent the previous NoneType.strip bug while still keeping a usable row.
        if not title.strip():
            title = "Untitled Task"

        status = self.normalize_status(status)
        if status not in TASK_STATUSES:
            raise ValueError("Invalid task status.")
        old_status = self.normalize_status(task.get("status"))
        timestamp = now_str()
        created_at = task.get("created_at") or timestamp
        updates = {
            "title": title.strip(),
            "description": description.strip(),
            "status": status,
            "updated_at": timestamp,
        }
        if status in ["COMPLETED", "MILESTONE"]:
            updates["completed_at"] = created_at
        else:
            updates["completed_at"] = ""
        self.repo.update_row(SHEETS["tasks"], "task_id", task_id, updates)
        if old_status != status:
            self._record_status_change("TASK", task_id, old_status, status)

    def change_status(self, task_id: str, new_status: str) -> None:
        task = self.get_task(task_id)
        if not task:
            raise ValueError("Task not found.")
        self.update_task(task_id, task.get("title") or "", task.get("description") or "", new_status)

    def _record_status_change(self, entity_type: str, entity_id: str, old_status: str, new_status: str) -> None:
        history_id = self.repo.next_id("history", "H")
        self.repo.append_row(SHEETS["status_history"], {
            "history_id": history_id,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "old_status": old_status,
            "new_status": new_status,
            "changed_at": now_str(),
        })
