from dataclasses import dataclass
from typing import Optional


@dataclass
class Task:
    task_id: str
    project_id: str
    title: str
    description: str
    status: str
    created_at: str
    updated_at: str
    completed_at: Optional[str] = None
