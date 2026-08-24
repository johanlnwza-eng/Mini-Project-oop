"""
task_manager.py

TaskManager เป็นตัวกลาง (business logic layer) ระหว่าง GUI กับ Task objects
- Encapsulation: เก็บ list ของ task เป็น private เข้าถึงผ่าน method เท่านั้น
- ใช้ Polymorphism ทางอ้อม: เวลาเรียก task.calculate_priority_score() หรือ
  task.get_info() ไม่ว่า task จะเป็น DeadlineTask หรือ RecurringTask ก็เรียก
  ได้แบบเดียวกัน (duck typing / interface เดียวกันจาก Task)
"""

import json
from category import Category
from task import Task, DeadlineTask, RecurringTask
from datetime import date


class TaskManager:
    def __init__(self):
        self.__tasks = []          # private: list[Task]
        self.__categories = {}     # private: name -> Category

    # ---------- จัดการ Category ----------
    def add_category(self, name, color_code="#888888"):
        if name not in self.__categories:
            self.__categories[name] = Category(name, color_code)
        return self.__categories[name]

    def get_categories(self):
        return list(self.__categories.values())

    # ---------- จัดการ Task (CRUD) ----------
    def add_task(self, task: Task):
        if not isinstance(task, Task):
            raise TypeError("add_task รับได้เฉพาะ instance ของ Task (หรือ subclass)")
        self.__tasks.append(task)
        return task

    def remove_task(self, task_id):
        before = len(self.__tasks)
        self.__tasks = [t for t in self.__tasks if t.id != task_id]
        return len(self.__tasks) < before

    def get_task(self, task_id):
        for t in self.__tasks:
            if t.id == task_id:
                return t
        return None

    def get_all_tasks(self):
        return list(self.__tasks)  # คืน copy กันโค้ดภายนอกแก้ list ตรงๆ

    def toggle_complete(self, task_id):
        task = self.get_task(task_id)
        if task is None:
            return False
        if task.is_completed:
            task.mark_incomplete()
        else:
            task.mark_complete()
        return True

    # ---------- เรียงลำดับ / ค้นหา / กรอง ----------
    def sort_by_priority(self):
        """เรียงตามคะแนนความสำคัญจากมากไปน้อย (ใช้ polymorphic method)"""
        return sorted(self.__tasks, key=lambda t: t.calculate_priority_score(), reverse=True)

    def search(self, keyword):
        keyword = keyword.lower().strip()
        return [t for t in self.__tasks
                if keyword in t.title.lower() or keyword in t.description.lower()]

    def filter_by_category(self, category: Category):
        return [t for t in self.__tasks if t.category == category]

    def filter_by_status(self, completed: bool):
        return [t for t in self.__tasks if t.is_completed == completed]

    def get_overdue_tasks(self):
        return [t for t in self.__tasks
                if t.due_date is not None and t.due_date < date.today() and not t.is_completed]

    # ---------- Persistence (บันทึก/โหลดเป็น JSON) ----------
    def save_to_file(self, filepath):
        data = []
        for t in self.__tasks:
            entry = {
                "type": t.__class__.__name__,
                "title": t.title,
                "description": t.description,
                "due_date": t.due_date.isoformat() if t.due_date else None,
                "priority": t.priority,
                "is_completed": t.is_completed,
                "category": t.category.name if t.category else None,
            }
            if isinstance(t, DeadlineTask):
                entry["penalty_weight"] = t.penalty_weight
            if isinstance(t, RecurringTask):
                entry["recurrence_interval"] = t.recurrence_interval
            data.append(entry)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_from_file(self, filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.__tasks.clear()
        for entry in data:
            category = None
            if entry.get("category"):
                category = self.add_category(entry["category"])

            due_date = date.fromisoformat(entry["due_date"]) if entry.get("due_date") else None

            if entry["type"] == "DeadlineTask":
                task = DeadlineTask(
                    title=entry["title"], description=entry.get("description", ""),
                    due_date=due_date, priority=entry.get("priority", 2),
                    category=category, penalty_weight=entry.get("penalty_weight", 5),
                )
            elif entry["type"] == "RecurringTask":
                task = RecurringTask(
                    title=entry["title"], description=entry.get("description", ""),
                    due_date=due_date, priority=entry.get("priority", 2),
                    category=category, recurrence_interval=entry.get("recurrence_interval", "daily"),
                )
            else:
                continue

            if entry.get("is_completed"):
                task.mark_complete()
            self.__tasks.append(task)
