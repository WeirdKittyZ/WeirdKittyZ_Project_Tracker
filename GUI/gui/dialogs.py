import tkinter as tk
from tkinter import ttk
from utils.datetime_utils import to_display


class ProjectDialog(tk.Toplevel):
    def __init__(self, parent, title="Project", project=None, statuses=None):
        super().__init__(parent)
        self.title(title)
        self.result = None
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)
        statuses = statuses or ["ACTIVE", "COMPLETED"]

        ttk.Label(self, text="Name").grid(row=0, column=0, padx=10, pady=8, sticky="w")
        self.name_var = tk.StringVar(value=(project or {}).get("name", ""))
        ttk.Entry(self, textvariable=self.name_var, width=55).grid(row=0, column=1, padx=10, pady=8, sticky="ew")

        ttk.Label(self, text="Description").grid(row=1, column=0, padx=10, pady=8, sticky="nw")
        self.description = tk.Text(self, width=60, height=10, wrap="word")
        self.description.grid(row=1, column=1, padx=10, pady=8, sticky="nsew")
        self.description.insert("1.0", (project or {}).get("description", "") or "")

        ttk.Label(self, text="Status").grid(row=2, column=0, padx=10, pady=8, sticky="w")
        self.status_var = tk.StringVar(value=(project or {}).get("status", "ACTIVE"))
        ttk.Combobox(self, textvariable=self.status_var, values=statuses, state="readonly").grid(row=2, column=1, padx=10, pady=8, sticky="ew")

        buttons = ttk.Frame(self)
        buttons.grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Button(buttons, text="Save", command=self._save).pack(side="left", padx=5)
        ttk.Button(buttons, text="Cancel", command=self.destroy).pack(side="left", padx=5)

    def _save(self):
        self.result = {
            "name": self.name_var.get(),
            "description": self.description.get("1.0", "end").strip(),
            "status": self.status_var.get(),
        }
        self.destroy()


class TaskDialog(tk.Toplevel):
    def __init__(self, parent, title="Task", task=None, statuses=None):
        super().__init__(parent)
        self.title(title)
        self.result = None
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)
        statuses = statuses or ["TO DO", "IN MILESTONE", "MILESTONE", "PENDING", "COMPLETED", "CANCELLED"]
        t = task or {}

        ttk.Label(self, text="Title").grid(row=0, column=0, padx=10, pady=8, sticky="w")
        self.title_var = tk.StringVar(value=t.get("title", ""))
        ttk.Entry(self, textvariable=self.title_var, width=55).grid(row=0, column=1, padx=10, pady=8, sticky="ew")

        ttk.Label(self, text="Description").grid(row=1, column=0, padx=10, pady=8, sticky="nw")
        self.description = tk.Text(self, width=60, height=10, wrap="word")
        self.description.grid(row=1, column=1, padx=10, pady=8, sticky="nsew")
        self.description.insert("1.0", t.get("description", "") or "")

        ttk.Label(self, text="Status").grid(row=2, column=0, padx=10, pady=8, sticky="w")
        self.status_var = tk.StringVar(value=t.get("status", "TO DO"))
        ttk.Combobox(self, textvariable=self.status_var, values=statuses, state="readonly").grid(
            row=2, column=1, padx=10, pady=8, sticky="ew")

        # ── Date fields (shown only when editing an existing task) ──────
        self._is_edit = bool(task)
        if self._is_edit:
            sep = ttk.Separator(self, orient="horizontal")
            sep.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=(4, 0))

            ttk.Label(self, text="Dates", font=("Segoe UI", 9, "bold")).grid(
                row=4, column=0, columnspan=2, padx=10, pady=(6, 0), sticky="w")

            hint = ttk.Label(self, text="Format: YYYY-MM-DD HH:MM", foreground="grey",
                             font=("Segoe UI", 8))
            hint.grid(row=4, column=1, padx=10, pady=(6, 0), sticky="e")

            ttk.Label(self, text="Created").grid(row=5, column=0, padx=10, pady=4, sticky="w")
            self.created_var = tk.StringVar(value=to_display(t.get("created_at", "")))
            ttk.Entry(self, textvariable=self.created_var, width=20).grid(
                row=5, column=1, padx=10, pady=4, sticky="w")

            ttk.Label(self, text="Updated").grid(row=6, column=0, padx=10, pady=4, sticky="w")
            self.updated_var = tk.StringVar(value=to_display(t.get("updated_at", "")))
            ttk.Entry(self, textvariable=self.updated_var, width=20).grid(
                row=6, column=1, padx=10, pady=4, sticky="w")

            ttk.Label(self, text="Completed").grid(row=7, column=0, padx=10, pady=4, sticky="w")
            self.completed_var = tk.StringVar(value=to_display(t.get("completed_at", "") or ""))
            ttk.Entry(self, textvariable=self.completed_var, width=20).grid(
                row=7, column=1, padx=10, pady=4, sticky="w")

        buttons = ttk.Frame(self)
        buttons.grid(row=8, column=0, columnspan=2, pady=10)
        ttk.Button(buttons, text="Save", command=self._save).pack(side="left", padx=5)
        ttk.Button(buttons, text="Cancel", command=self.destroy).pack(side="left", padx=5)

    def _save(self):
        self.result = {
            "title":       self.title_var.get(),
            "description": self.description.get("1.0", "end").strip(),
            "status":      self.status_var.get(),
        }
        if self._is_edit:
            self.result["created_at"]   = self.created_var.get().strip()
            self.result["updated_at"]   = self.updated_var.get().strip()
            self.result["completed_at"] = self.completed_var.get().strip()
        self.destroy()


class ActivityDialog(tk.Toplevel):
    def __init__(self, parent, title="Milestone Update", default_date="", activity_types=None):
        super().__init__(parent)
        self.title(title)
        self.result = None
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()
        self.columnconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        activity_types = activity_types or ["MILESTONE", "NOTE", "MEETING", "MILESTONE"]

        ttk.Label(self, text="Date YYYY-MM-DD").grid(row=0, column=0, padx=10, pady=8, sticky="w")
        self.date_var = tk.StringVar(value=default_date)
        ttk.Entry(self, textvariable=self.date_var, width=55).grid(row=0, column=1, padx=10, pady=8, sticky="ew")

        ttk.Label(self, text="Type").grid(row=1, column=0, padx=10, pady=8, sticky="w")
        self.type_var = tk.StringVar(value="MILESTONE")
        ttk.Combobox(self, textvariable=self.type_var, values=activity_types, state="readonly").grid(row=1, column=1, padx=10, pady=8, sticky="ew")

        ttk.Label(self, text="Notes").grid(row=2, column=0, padx=10, pady=8, sticky="nw")
        self.notes = tk.Text(self, width=60, height=12, wrap="word")
        self.notes.grid(row=2, column=1, padx=10, pady=8, sticky="nsew")

        buttons = ttk.Frame(self)
        buttons.grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Button(buttons, text="Save", command=self._save).pack(side="left", padx=5)
        ttk.Button(buttons, text="Cancel", command=self.destroy).pack(side="left", padx=5)

    def _save(self):
        self.result = {
            "activity_date": self.date_var.get(),
            "activity_type": self.type_var.get(),
            "notes": self.notes.get("1.0", "end").strip(),
        }
        self.destroy()
