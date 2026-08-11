import tkinter as tk
from tkinter import ttk, messagebox

from repositories.excel_repository import ExcelRepository
from services.project_service import ProjectService
from services.task_service import TaskService
from utils.config import WORKBOOK_PATH
from utils.constants import PROJECT_STATUSES, TASK_STATUSES
from gui.dialogs import ProjectDialog, TaskDialog
from gui.project_view import ProjectView


class ProjectTrackerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("WeirdKittyZ's Project Tracker")
        self.geometry("1250x760")
        self.minsize(1050, 620)

        self.repo = ExcelRepository(WORKBOOK_PATH)
        self.project_service = ProjectService(self.repo)
        self.task_service = TaskService(self.repo)

        self.project_lookup = {}
        self.current_project_id = ""

        self._build_ui()
        self.refresh_project_dropdown()
        self.load_selected_project()

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        header = ttk.Frame(self, padding=10)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(1, weight=1)

        ttk.Label(header, text="WeirdKittyZ's Project Tracker", font=("Segoe UI", 18, "bold")).grid(row=0, column=0, columnspan=7, sticky="w")
        ttk.Label(header, text=f"Workbook: {WORKBOOK_PATH}").grid(row=1, column=0, columnspan=7, sticky="w", pady=(0, 8))

        ttk.Label(header, text="Project").grid(row=2, column=0, sticky="w", padx=(0, 6))
        self.project_var = tk.StringVar(value="")
        self.project_combo = ttk.Combobox(header, textvariable=self.project_var, state="readonly")
        self.project_combo.grid(row=2, column=1, sticky="ew", padx=(0, 8))
        self.project_combo.bind("<<ComboboxSelected>>", lambda event: self.load_selected_project())

        ttk.Button(header, text="New Project", command=self.create_project).grid(row=2, column=2, padx=3)
        ttk.Button(header, text="Edit Project", command=self.edit_project).grid(row=2, column=3, padx=3)
        ttk.Button(header, text="Mark Project Completed", command=self.complete_project).grid(row=2, column=4, padx=3)
        ttk.Button(header, text="Refresh", command=self.refresh_all).grid(row=2, column=5, padx=3)

        self.view = ProjectView(self)
        self.view.grid(row=1, column=0, sticky="nsew")
        
        footer = ttk.Frame(self, padding=(10, 4))
        footer.grid(row=2, column=0, sticky="ew")

        ttk.Label(
            footer,
            text="© 2026 WeirdKittyZ. Built with Microsoft Copilot. Version 4.1. All rights reserved.",
            font=("Segoe UI", 9),
            foreground="black"
        ).pack(anchor="center")
        
        self.view.task_status_combo["values"] = ["", "ACTIVE"] + TASK_STATUSES
        self.view.task_status_combo.bind("<<ComboboxSelected>>", lambda event: self.refresh_tasks())
        self.view.add_task_button.configure(command=self.add_task)
        self.view.edit_task_button.configure(command=self.edit_task)
        self.view.milestone_task_button.configure(command=lambda: self.change_task_status("MILESTONE"))
        self.view.pending_task_button.configure(command=lambda: self.change_task_status("PENDING"))
        self.view.in_progress_task_button.configure(command=lambda: self.change_task_status("IN PROGRESS"))
        self.view.complete_task_button.configure(command=lambda: self.change_task_status("COMPLETED"))
        self.view.cancel_task_button.configure(command=lambda: self.change_task_status("CANCELLED"))
        self.view.task_tree.bind("<Double-1>", lambda event: self.edit_task())

    def refresh_project_dropdown(self):
        projects = self.project_service.list_projects(include_completed=True)
        self.project_lookup = {f'{p["project_id"]} - {p["name"]} [{p.get("status", "")}]': p["project_id"] for p in projects}
        values = list(self.project_lookup.keys())
        self.project_combo["values"] = values
        if values and self.project_var.get() not in values:
            self.project_var.set(values[0])
        elif not values:
            self.project_var.set("")
            self.current_project_id = ""

    def get_selected_project_id(self):
        return self.project_lookup.get(self.project_var.get(), "")

    def refresh_all(self):
        previous_id = self.current_project_id
        self.refresh_project_dropdown()
        if previous_id:
            for label, project_id in self.project_lookup.items():
                if project_id == previous_id:
                    self.project_var.set(label)
                    break
        self.load_selected_project()

    def load_selected_project(self):
        self.current_project_id = self.get_selected_project_id()
        self.view.task_tree.selection_remove(self.view.task_tree.selection())
        if not self.current_project_id:
            self.view.show_project(None)
            self.view.clear_tasks()
            return
        project = self.project_service.get_project(self.current_project_id)
        self.view.show_project(project)
        self.refresh_tasks()
        self.refresh_stats()

    def refresh_stats(self):
        if not self.current_project_id:
            self.view.set_stats("")
            return
        tasks = self.task_service.list_tasks(project_id=self.current_project_id, status="")
        counts = {status: 0 for status in TASK_STATUSES}
        for task in tasks:
            status = task.get("status")
            if status in counts:
                counts[status] += 1
        stats = (
            f"Tasks: {len(tasks)} total | "
            f"TO DO: {counts['TO DO']} | "
            f"IN PROGRESS: {counts['IN PROGRESS']} | "
            f"PENDING: {counts['PENDING']} | "
            f"MILESTONE: {counts['MILESTONE']} | "
            f"COMPLETED: {counts['COMPLETED']} | "
            f"CANCELLED: {counts['CANCELLED']}"
        )
        self.view.set_stats(stats)

    def create_project(self):
        dialog = ProjectDialog(self, "Create Project", statuses=PROJECT_STATUSES)
        self.wait_window(dialog)
        if dialog.result:
            try:
                new_id = self.project_service.create_project(dialog.result["name"], dialog.result["description"])
                self.refresh_project_dropdown()
                for label, project_id in self.project_lookup.items():
                    if project_id == new_id:
                        self.project_var.set(label)
                        break
                self.load_selected_project()
            except Exception as exc:
                messagebox.showerror("Error", str(exc))

    def edit_project(self):
        if not self.current_project_id:
            messagebox.showwarning("Select Project", "Please select a project first.")
            return
        project = self.project_service.get_project(self.current_project_id)
        dialog = ProjectDialog(self, "Edit Project", project=project, statuses=PROJECT_STATUSES)
        self.wait_window(dialog)
        if dialog.result:
            try:
                self.project_service.update_project(
                    self.current_project_id,
                    dialog.result["name"],
                    dialog.result["description"],
                    dialog.result["status"],
                )
                self.refresh_all()
            except Exception as exc:
                messagebox.showerror("Error", str(exc))

    def complete_project(self):
        if not self.current_project_id:
            messagebox.showwarning("Select Project", "Please select a project first.")
            return
        if messagebox.askyesno("Complete Project", "Mark this project as completed? Records will be kept."):
            try:
                self.project_service.complete_project(self.current_project_id)
                self.refresh_all()
            except Exception as exc:
                messagebox.showerror("Error", str(exc))

    def refresh_tasks(self):
        self.view.clear_tasks()
        if not self.current_project_id:
            return
        tasks = self.task_service.list_tasks(
            project_id=self.current_project_id,
            status=self.view.task_status_var.get(),
        )
        for task in tasks:
            self.view.add_task_row(task)
        self.view.task_tree.selection_remove(self.view.task_tree.selection())
        self.refresh_stats()

    def get_selected_task_id(self):
        selected = self.view.task_tree.selection()
        return selected[0] if selected else ""

    def add_task(self):
        if not self.current_project_id:
            messagebox.showwarning("Select Project", "Please select or create a project first.")
            return
        dialog = TaskDialog(self, "Add Task", statuses=TASK_STATUSES)
        self.wait_window(dialog)
        if dialog.result:
            try:
                self.task_service.add_task(
                    self.current_project_id,
                    dialog.result["title"],
                    dialog.result["description"],
                    dialog.result["status"],
                )
                self.refresh_tasks()
            except Exception as exc:
                messagebox.showerror("Error", str(exc))

    def edit_task(self):
        task_id = self.get_selected_task_id()
        if not task_id:
            messagebox.showwarning("Select Task", "Please select a task first.")
            return
        task = self.task_service.get_task(task_id)
        if not task or task.get("project_id") != self.current_project_id:
            messagebox.showwarning("Select Task", "Please select a task from the current project.")
            self.refresh_tasks()
            return
        dialog = TaskDialog(self, "Edit Task", task=task, statuses=TASK_STATUSES)
        self.wait_window(dialog)
        if dialog.result:
            try:
                self.task_service.update_task(
                    task_id,
                    dialog.result["title"],
                    dialog.result["description"],
                    dialog.result["status"],
                )
                self.refresh_tasks()
            except Exception as exc:
                messagebox.showerror("Error", str(exc))

    def change_task_status(self, status):
        task_id = self.get_selected_task_id()
        if not task_id:
            messagebox.showwarning("Select Task", "Please select a task first.")
            return
        try:
            task = self.task_service.get_task(task_id)
            if not task or task.get("project_id") != self.current_project_id:
                messagebox.showwarning("Select Task", "Please select a task from the current project.")
                self.refresh_tasks()
                return
            self.task_service.change_status(task_id, status)
            self.refresh_tasks()
        except Exception as exc:
            messagebox.showerror("Error", str(exc))
