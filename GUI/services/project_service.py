from typing import List, Dict, Any, Optional
from repositories.excel_repository import ExcelRepository
from utils.constants import SHEETS, PROJECT_STATUSES
from utils.datetime_utils import now_str


class ProjectService:
    def __init__(self, repo: ExcelRepository):
        self.repo = repo

    def create_project(self, name: str, description: str = "") -> str:
        name = name.strip()
        if not name:
            raise ValueError("Project name is required.")
        project_id = self.repo.next_id("project", "P")
        timestamp = now_str()
        self.repo.append_row(SHEETS["projects"], {
            "project_id": project_id,
            "name": name,
            "description": description.strip(),
            "status": "ACTIVE",
            "created_at": timestamp,
            "updated_at": timestamp,
        })
        return project_id

    def list_projects(self, search: str = "", include_completed: bool = True) -> List[Dict[str, Any]]:
        projects = self.repo.read_table(SHEETS["projects"])
        # Backward compatibility with older workbooks that used ARCHIVED or ON_HOLD.
        for project in projects:
            if project.get("status") == "ARCHIVED":
                project["status"] = "COMPLETED"
        if not include_completed:
            projects = [p for p in projects if p.get("status") != "COMPLETED"]
        search = search.strip().lower()
        if search:
            projects = [
                p for p in projects
                if search in str(p.get("name", "")).lower()
                or search in str(p.get("description", "")).lower()
            ]
        return sorted(projects, key=lambda p: str(p.get("name", "")).lower())

    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        project = self.repo.get_by_id(SHEETS["projects"], "project_id", project_id)
        if project and project.get("status") == "ARCHIVED":
            project["status"] = "COMPLETED"
        return project

    def update_project(self, project_id: str, name: str, description: str, status: str) -> None:
        if status == "ARCHIVED":
            status = "COMPLETED"
        if status not in PROJECT_STATUSES:
            raise ValueError("Invalid project status.")
        if not name.strip():
            raise ValueError("Project name is required.")
        updated = self.repo.update_row(SHEETS["projects"], "project_id", project_id, {
            "name": name.strip(),
            "description": description.strip(),
            "status": status,
            "updated_at": now_str(),
        })
        if not updated:
            raise ValueError("Project not found.")

    def complete_project(self, project_id: str) -> None:
        project = self.get_project(project_id)
        if not project:
            raise ValueError("Project not found.")
        self.update_project(
            project_id,
            project.get("name", ""),
            project.get("description", ""),
            "COMPLETED",
        )
