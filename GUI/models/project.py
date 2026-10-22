from dataclasses import dataclass


@dataclass
class Project:
    project_id: str
    name: str
    description: str
    status: str
    created_at: str
    updated_at: str
