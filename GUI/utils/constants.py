PROJECT_STATUSES = ["ACTIVE", "COMPLETED"]

# Task statuses visible in the GUI. Values are deliberately user-friendly because
# they are also stored in Excel.
TASK_STATUSES = ["TO DO", "IN PROGRESS", "MILESTONE", "PENDING", "COMPLETED", "CANCELLED"]
ACTIVE_TASK_STATUSES = ["TO DO", "IN PROGRESS", "MILESTONE", "PENDING"]

# Backward compatibility with older V1/V2/V3 workbooks.
TASK_STATUS_ALIASES = {
    "TODO": "TO DO",
    "IN_PROGRESS": "IN PROGRESS",
    "PROGRESS": "MILESTONE",
}

# Kept only so old unused modules do not break if imported. No Activity_Log sheet
# is created by the repository in V4.
ACTIVITY_TYPES = ["NOTE", "MEETING", "MILESTONE"]

SHEETS = {
    "projects": "Projects",
    "tasks": "Tasks",
    "status_history": "Status_History",
    "counters": "Counters",
}

PROJECT_COLUMNS = [
    "project_id", "name", "description", "status", "created_at", "updated_at"
]

TASK_COLUMNS = [
    "task_id", "project_id", "title", "description", "status",
    "created_at", "updated_at", "completed_at"
]

STATUS_HISTORY_COLUMNS = [
    "history_id", "entity_type", "entity_id", "old_status", "new_status", "changed_at"
]

COUNTER_COLUMNS = ["name", "value"]
