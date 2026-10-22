import tkinter as tk
from tkinter import ttk, messagebox

from utils.datetime_utils import to_display


class ProjectView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=10)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        self.sort_state = {}
        self._task_descriptions = {}
        self._on_date_edit_callback = None   # set by main_window

        self.project_detail = ttk.LabelFrame(self, text="Project Details")
        self.project_detail.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        self.project_detail.columnconfigure(1, weight=1)

        ttk.Label(self.project_detail, text="Status:").grid(row=0, column=0, sticky="nw", padx=6, pady=4)
        self.status_var = tk.StringVar(value="")
        ttk.Label(self.project_detail, textvariable=self.status_var).grid(row=0, column=1, sticky="w", padx=6, pady=4)

        ttk.Label(self.project_detail, text="Description:").grid(row=1, column=0, sticky="nw", padx=6, pady=4)
        self.description_text = tk.Text(self.project_detail, height=3, wrap="word")
        self.description_text.grid(row=1, column=1, sticky="ew", padx=6, pady=4)
        self.description_text.configure(state="disabled")

        self.stats_var = tk.StringVar(value="")
        ttk.Label(self, textvariable=self.stats_var, font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky="w", pady=(0, 8))

        # PanedWindow holds the task table (top) and description panel (bottom)
        # — drag the sash between them to resize
        self.rowconfigure(2, weight=1)
        self.paned = tk.PanedWindow(self, orient="vertical", sashrelief="flat",
                                    sashwidth=4, sashpad=0, bg="#e0e0e0")
        self.paned.grid(row=2, column=0, sticky="nsew")

        # ── Top pane: Tasks table ──────────────────────────────────────
        self.tasks_frame = ttk.LabelFrame(self.paned, text="Tasks")
        self.tasks_frame.columnconfigure(0, weight=1)
        self.tasks_frame.rowconfigure(1, weight=1)
        self._build_tasks(self.tasks_frame)
        self.paned.add(self.tasks_frame, stretch="always", minsize=120)

        # ── Bottom pane: Task Description ──────────────────────────────
        self.task_detail_frame = ttk.LabelFrame(self.paned, text="Task Description")
        self.task_detail_frame.columnconfigure(0, weight=1)
        self.task_detail_frame.rowconfigure(1, weight=1)
        self.paned.add(self.task_detail_frame, stretch="always", minsize=80)

        self.task_title_var = tk.StringVar(value="")
        ttk.Label(
            self.task_detail_frame,
            textvariable=self.task_title_var,
            font=("Segoe UI", 10, "bold"),
            foreground="#333333",
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=8, pady=(1, 0))

        self.task_desc_text = tk.Text(
            self.task_detail_frame,
            wrap="word",
            state="disabled",
            relief="sunken",
            font=("Segoe UI", 10),
            background="#f5f5f5",
            foreground="#222222",
            borderwidth=1,
        )
        self.task_desc_text.grid(row=1, column=0, sticky="nsew", padx=(8, 0), pady=(2, 6))

        desc_scroll = ttk.Scrollbar(self.task_detail_frame, orient="vertical",
                                    command=self.task_desc_text.yview)
        desc_scroll.grid(row=1, column=1, sticky="ns", padx=(0, 8), pady=(2, 6))
        self.task_desc_text.configure(yscrollcommand=desc_scroll.set)

        # Set default split: table gets 40% of space, description gets 60%
        # Done after the window is drawn so geometry is known
        self.paned.bind("<Map>", self._set_default_sash, add="+")

        self._show_task_desc_placeholder()

    def _set_default_sash(self, event=None):
        """Place the sash at 40% from top on first render."""
        self.paned.unbind("<Map>")
        self.paned.update_idletasks()
        total = self.paned.winfo_height()
        if total > 10:
            self.paned.sash_place(0, 0, int(total * 0.40))

    def _build_tasks(self, parent):
        toolbar = ttk.Frame(parent)
        toolbar.grid(row=0, column=0, sticky="ew", padx=6, pady=6)
        ttk.Label(toolbar, text="Status Filter").pack(side="left", padx=(0, 5))
        self.task_status_var = tk.StringVar(value="ACTIVE")
        self.task_status_combo = ttk.Combobox(toolbar, textvariable=self.task_status_var, state="readonly", width=18)
        self.task_status_combo.pack(side="left", padx=(0, 10))

        self.add_task_button      = ttk.Button(toolbar, text="Add Task")
        self.edit_task_button     = ttk.Button(toolbar, text="Edit Task")
        self.in_progress_task_button = ttk.Button(toolbar, text="In Progress")
        self.pending_task_button  = ttk.Button(toolbar, text="Pending")
        self.milestone_task_button = ttk.Button(toolbar, text="Milestone")
        self.complete_task_button = ttk.Button(toolbar, text="Mark Completed")
        self.cancel_task_button   = ttk.Button(toolbar, text="Cancelled")
        for btn in (self.add_task_button, self.edit_task_button,
                    self.in_progress_task_button, self.pending_task_button,
                    self.milestone_task_button, self.complete_task_button,
                    self.cancel_task_button):
            btn.pack(side="left", padx=3)

        table_frame = ttk.Frame(parent)
        table_frame.grid(row=1, column=0, sticky="nsew", padx=6, pady=6)
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        # Description removed from columns — shown in panel below
        columns = ("title", "status", "created_at", "updated_at", "completed_at")
        self.task_tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        self.task_tree.tag_configure("TO DO",       background="#FF8A80")   # soft coral-red
        self.task_tree.tag_configure("IN PROGRESS", background="#FFF9AA")   # soft pale yellow
        self.task_tree.tag_configure("PENDING",     background="#FFD8A8")   # soft peach-orange
        self.task_tree.tag_configure("COMPLETED",   background="#B6F5B6")   # soft mint green
        self.task_tree.tag_configure("CANCELLED",   background="#E6E6E6")   # light grey

        headings = {
            "title":        "Title",
            "status":       "Status",
            "created_at":   "Created",
            "updated_at":   "Updated",
            "completed_at": "Completed",
        }
        widths = {
            "title":        400,
            "status":       130,
            "created_at":   145,
            "updated_at":   145,
            "completed_at": 145,
        }
        for col in columns:
            self.task_tree.heading(col, text=headings[col], command=lambda c=col: self.sort_by_column(c))
            self.task_tree.column(col, width=widths[col], minwidth=60, stretch=True)

        self.task_tree.grid(row=0, column=0, sticky="nsew")
        y_scroll = ttk.Scrollbar(table_frame, orient="vertical",   command=self.task_tree.yview)
        x_scroll = ttk.Scrollbar(table_frame, orient="horizontal", command=self.task_tree.xview)
        self.task_tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")

        self.task_tree.bind("<<TreeviewSelect>>", self._on_task_select)
        self.task_tree.bind("<Double-1>", self._on_double_click)

    # ------------------------------------------------------------------ #
    #  Double-click → edit date if a date column was clicked              #
    # ------------------------------------------------------------------ #
    DATE_COLUMNS = ("created_at", "updated_at", "completed_at")

    def _on_double_click(self, event):
        region = self.task_tree.identify_region(event.x, event.y)
        if region != "cell":
            return
        col_id = self.task_tree.identify_column(event.x)       # e.g. "#3"
        col_index = int(col_id.lstrip("#")) - 1
        columns = ("title", "status", "created_at", "updated_at", "completed_at")
        if col_index < 0 or col_index >= len(columns):
            return
        col_name = columns[col_index]
        if col_name not in self.DATE_COLUMNS:
            # Not a date column — let main_window handle it as edit-task
            return
        row_id = self.task_tree.identify_row(event.y)
        if not row_id:
            return
        current_val = self.task_tree.set(row_id, col_name)
        self._open_date_editor(row_id, col_name, current_val, event.x_root, event.y_root)

    def _open_date_editor(self, task_id, col_name, current_val, x, y):
        popup = tk.Toplevel(self)
        popup.title("Edit Date")
        popup.resizable(False, False)
        popup.geometry(f"+{x}+{y}")
        popup.grab_set()

        label_text = {"created_at": "Created", "updated_at": "Updated", "completed_at": "Completed"}
        ttk.Label(popup, text=f"{label_text[col_name]}  (YYYY-MM-DD HH:MM)", padding=8).grid(
            row=0, column=0, columnspan=2, sticky="w")

        entry_var = tk.StringVar(value=current_val)
        entry = ttk.Entry(popup, textvariable=entry_var, width=20)
        entry.grid(row=1, column=0, padx=(8, 4), pady=4)
        entry.focus_set()
        entry.select_range(0, "end")

        def save():
            new_val = entry_var.get().strip()
            if self._on_date_edit_callback:
                try:
                    self._on_date_edit_callback(task_id, col_name, new_val)
                    popup.destroy()
                except ValueError as exc:
                    messagebox.showerror("Invalid date", str(exc), parent=popup)
            else:
                popup.destroy()

        ttk.Button(popup, text="Save", command=save).grid(row=1, column=1, padx=(0, 8), pady=4)
        popup.bind("<Return>", lambda e: save())
        popup.bind("<Escape>", lambda e: popup.destroy())

    # ------------------------------------------------------------------ #
    #  Row selection → description panel                                  #
    # ------------------------------------------------------------------ #
    def _on_task_select(self, event=None):
        selected = self.task_tree.selection()
        if not selected:
            self._show_task_desc_placeholder()
            return
        values = self.task_tree.item(selected[0]).get("values", [])
        title = values[0] if values else ""
        desc = self._task_descriptions.get(selected[0], "")
        self.task_title_var.set(title)
        self._set_task_desc(desc or "(no description)")

    def _show_task_desc_placeholder(self):
        self.task_title_var.set("")
        self._set_task_desc("Click a task to see its description here.")

    def _set_task_desc(self, value):
        self.task_desc_text.configure(state="normal")
        self.task_desc_text.delete("1.0", "end")
        self.task_desc_text.insert("1.0", value)
        self.task_desc_text.configure(state="disabled")

    def _set_text(self, widget, value):
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", value or "")
        widget.configure(state="disabled")

    # ------------------------------------------------------------------ #
    #  Public API used by main_window                                      #
    # ------------------------------------------------------------------ #
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
        self._task_descriptions = {}
        self._show_task_desc_placeholder()

    def add_task_row(self, task):
        task_id = task.get("task_id")
        status  = task.get("status", "")
        self._task_descriptions[task_id] = str(task.get("description", "") or "")
        self.task_tree.insert(
            "", "end",
            iid=task_id,
            values=(
                task.get("title", ""),
                status,
                to_display(task.get("created_at", "")),
                to_display(task.get("updated_at", "")),
                to_display(task.get("completed_at", "") or ""),
            ),
            tags=(status,),
        )

    def update_task_date_cell(self, task_id, col_name, display_value):
        """Refresh one date cell in the tree after a successful save."""
        self.task_tree.set(task_id, col_name, display_value)

    def show_task_detail(self, task):
        return

    def sort_by_column(self, column):
        items   = list(self.task_tree.get_children(""))
        reverse = self.sort_state.get(column, False)
        items.sort(key=lambda iid: str(self.task_tree.set(iid, column) or "").lower(), reverse=reverse)
        for index, item in enumerate(items):
            self.task_tree.move(item, "", index)
        self.sort_state[column] = not reverse
