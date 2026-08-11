import tkinter as tk
from tkinter import ttk


class ProjectView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=10)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        self.sort_state = {}

        self.project_detail = ttk.LabelFrame(self, text="Project Details")
        self.project_detail.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        self.project_detail.columnconfigure(1, weight=1)

        ttk.Label(self.project_detail, text="Status:").grid(row=0, column=0, sticky="nw", padx=6, pady=4)
        self.status_var = tk.StringVar(value="")
        ttk.Label(self.project_detail, textvariable=self.status_var).grid(row=0, column=1, sticky="w", padx=6, pady=4)

        ttk.Label(self.project_detail, text="Description:").grid(row=1, column=0, sticky="nw", padx=6, pady=4)
        self.description_text = tk.Text(self.project_detail, height=5, wrap="word")
        self.description_text.grid(row=1, column=1, sticky="ew", padx=6, pady=4)
        self.description_text.configure(state="disabled")

        self.stats_var = tk.StringVar(value="")
        ttk.Label(self, textvariable=self.stats_var, font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky="w", pady=(0, 8))

        self.tasks_frame = ttk.LabelFrame(self, text="Tasks")
        self.tasks_frame.grid(row=2, column=0, sticky="nsew")
        self._build_tasks(self.tasks_frame)

    def _build_tasks(self, parent):
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)

        toolbar = ttk.Frame(parent)
        toolbar.grid(row=0, column=0, sticky="ew", padx=6, pady=6)
        ttk.Label(toolbar, text="Status Filter").pack(side="left", padx=(0, 5))
        self.task_status_var = tk.StringVar(value="ACTIVE")
        self.task_status_combo = ttk.Combobox(toolbar, textvariable=self.task_status_var, state="readonly", width=18)
        self.task_status_combo.pack(side="left", padx=(0, 10))

        self.add_task_button = ttk.Button(toolbar, text="Add Task")
        self.add_task_button.pack(side="left", padx=3)
        self.edit_task_button = ttk.Button(toolbar, text="Edit Task")
        self.edit_task_button.pack(side="left", padx=3)
        self.in_progress_task_button = ttk.Button(toolbar, text="In Progress")
        self.in_progress_task_button.pack(side="left", padx=3)
        self.pending_task_button = ttk.Button(toolbar, text="Pending")
        self.pending_task_button.pack(side="left", padx=3)
        self.milestone_task_button = ttk.Button(toolbar, text="Milestone")
        self.milestone_task_button.pack(side="left", padx=3)
        self.complete_task_button = ttk.Button(toolbar, text="Mark Completed")
        self.complete_task_button.pack(side="left", padx=3)
        self.cancel_task_button = ttk.Button(toolbar, text="Cancelled")
        self.cancel_task_button.pack(side="left", padx=3)

        table_frame = ttk.Frame(parent)
        table_frame.grid(row=1, column=0, sticky="nsew", padx=6, pady=6)
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        columns = ("title", "status", "description", "created_at", "updated_at", "completed_at")
        self.task_tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        # Soft color coding by status. TO DO is intentionally red as requested.
        #self.task_tree.tag_configure("TO DO", background="#FFDADA")
        self.task_tree.tag_configure("TO DO", background="#ff5454")
        self.task_tree.tag_configure("IN PROGRESS", background="#f7fc5b")
        self.task_tree.tag_configure("PENDING", background="#ed7002")
        self.task_tree.tag_configure("COMPLETED", background="#6bfa6b")
        self.task_tree.tag_configure("CANCELLED", background="#E6E6E6")
        # MILESTONE has no extra color.

        headings = {
            "title": "Title",
            "status": "Status",
            "description": "Description",
            "created_at": "Created",
            "updated_at": "Updated",
            "completed_at": "Completed",
        }
        widths = {
            "title": 260,
            "status": 120,
            "description": 520,
            "created_at": 160,
            "updated_at": 160,
            "completed_at": 160,
        }
        for col in columns:
            self.task_tree.heading(col, text=headings[col], command=lambda c=col: self.sort_by_column(c))
            self.task_tree.column(col, width=widths[col], minwidth=80, stretch=True)

        self.task_tree.grid(row=0, column=0, sticky="nsew")
        y_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.task_tree.yview)
        x_scroll = ttk.Scrollbar(table_frame, orient="horizontal", command=self.task_tree.xview)
        self.task_tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")

    def _set_text(self, widget, value):
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", value or "")
        widget.configure(state="disabled")

    def show_project(self, project):
        if not project:
            self.status_var.set("")
            self._set_text(self.description_text, "Select or create a project to begin.")
            self.stats_var.set("")
            return
        self.status_var.set(project.get("status", ""))
        self._set_text(self.description_text, project.get("description", ""))

    def set_stats(self, stats_text):
        self.stats_var.set(stats_text or "")

    def clear_tasks(self):
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)

    def add_task_row(self, task):
        status = task.get("status", "")
        description = str(task.get("description", "") or "")
        self.task_tree.insert(
            "",
            "end",
            iid=task.get("task_id"),
            values=(
                task.get("title", ""),
                status,
                description,
                task.get("created_at", ""),
                task.get("updated_at", ""),
                task.get("completed_at", "") or "",
            ),
            tags=(status,),
        )

    def show_task_detail(self, task):
        # Kept as a no-op for compatibility with main_window event bindings.
        return

    def sort_by_column(self, column):
        items = list(self.task_tree.get_children(""))
        reverse = self.sort_state.get(column, False)

        def value_for(item_id):
            value = self.task_tree.set(item_id, column)
            return str(value or "").lower()

        items.sort(key=value_for, reverse=reverse)
        for index, item in enumerate(items):
            self.task_tree.move(item, "", index)
        self.sort_state[column] = not reverse
