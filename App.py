import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date, datetime

from task_manager import TaskManager
from task import DeadlineTask, RecurringTask

PRIORITY_LABEL = {1: "สูง", 2: "กลาง", 3: "ต่ำ"}


class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Priority To-Do Manager")
        self.root.geometry("880x560")

        self.manager = TaskManager()  # composition: TodoApp "มี" TaskManager

        self.__build_layout()
        self.__seed_demo_data()
        self.refresh_view()

    # ---------- Layout ----------
    def __build_layout(self):
        top_frame = ttk.Frame(self.root, padding=10)
        top_frame.pack(fill="x")

        ttk.Button(top_frame, text="+ เพิ่มงานใหม่", command=self.open_add_task_dialog).pack(side="left")
        ttk.Button(top_frame, text="ทำเครื่องหมายเสร็จ/ยกเลิก", command=self.toggle_selected).pack(side="left", padx=5)
        ttk.Button(top_frame, text="ลบงาน", command=self.delete_selected).pack(side="left", padx=5)
        ttk.Button(top_frame, text="บันทึกไฟล์", command=self.save_file).pack(side="left", padx=5)
        ttk.Button(top_frame, text="โหลดไฟล์", command=self.load_file).pack(side="left", padx=5)

        search_frame = ttk.Frame(self.root, padding=(10, 0))
        search_frame.pack(fill="x")
        ttk.Label(search_frame, text="ค้นหา:").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.refresh_view())
        ttk.Entry(search_frame, textvariable=self.search_var, width=30).pack(side="left", padx=5)

        columns = ("title", "type", "priority", "due", "category", "status", "score")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", height=18)
        headings = {
            "title": "ชื่องาน", "type": "ประเภท", "priority": "ระดับ",
            "due": "กำหนด/รอบ", "category": "หมวดหมู่", "status": "สถานะ",
            "score": "คะแนนความสำคัญ",
        }
        widths = {"title": 220, "type": 110, "priority": 60, "due": 140,
                  "category": 100, "status": 90, "score": 110}
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="w")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.status_label = ttk.Label(self.root, text="", padding=10)
        self.status_label.pack(fill="x")

    def __seed_demo_data(self):
        work = self.manager.add_category("งานเรียน", "#3B8BD4")
        home = self.manager.add_category("งานบ้าน", "#63C25B")

        self.manager.add_task(DeadlineTask(
            "ส่งการบ้าน OOP", "ทำ mini project ระบบ To-Do",
            due_date=date.today(), priority=1, category=work, score=90))
        self.manager.add_task(DeadlineTask(
            "อ่านหนังสือสอบ", "เตรียมสอบ midterm",
            due_date=date.today(), priority=2, category=work, score=70))
        self.manager.add_task(RecurringTask(
            "ล้างจาน", "หลังมื้อเย็น", priority=3, category=home,
            recurrence_interval="daily", score=25))

    # ---------- Actions ----------
    def refresh_view(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        keyword = self.search_var.get()
        tasks = self.manager.search(keyword) if keyword else self.manager.get_all_tasks()

        # เรียงตามคะแนนที่กรอก (มากไปน้อย)
        tasks = sorted(tasks, key=lambda t: t.score, reverse=True)

        for t in tasks:
            info = t.get_info()
            due_text = self.__format_due(t)
            status_text = "เสร็จแล้ว" if info["is_completed"] else "ยังไม่เสร็จ"
            self.tree.insert("", "end", iid=str(t.id), values=(
                info["title"], info["type"], PRIORITY_LABEL[info["priority"]],
                due_text, info["category"], status_text, info["score"],
            ))

        overdue = len(self.manager.get_overdue_tasks())
        total = len(self.manager.get_all_tasks())
        self.status_label.config(
            text=f"งานทั้งหมด: {total}   |   เลยกำหนด: {overdue}")

    def __format_due(self, t):
        if isinstance(t, DeadlineTask):
            return t.due_date.isoformat() if t.due_date else "-"
        if isinstance(t, RecurringTask):
            return f"ทำซ้ำ: {t.recurrence_interval}"
        return "-"

    def __selected_task_id(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("แจ้งเตือน", "กรุณาเลือกงานก่อน")
            return None
        return int(selection[0])

    def toggle_selected(self):
        task_id = self.__selected_task_id()
        if task_id is None:
            return
        self.manager.toggle_complete(task_id)
        self.refresh_view()

    def delete_selected(self):
        task_id = self.__selected_task_id()
        if task_id is None:
            return
        if messagebox.askyesno("ยืนยัน", "ต้องการลบงานนี้หรือไม่?"):
            self.manager.remove_task(task_id)
            self.refresh_view()

    def save_file(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".json",
                                                  filetypes=[("JSON", "*.json")])
        if filepath:
            self.manager.save_to_file(filepath)
            messagebox.showinfo("สำเร็จ", "บันทึกไฟล์เรียบร้อยแล้ว")

    def load_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if filepath:
            try:
                self.manager.load_from_file(filepath)
                self.refresh_view()
                messagebox.showinfo("สำเร็จ", "โหลดไฟล์เรียบร้อยแล้ว")
            except Exception as e:
                messagebox.showerror("เกิดข้อผิดพลาด", str(e))

    # ---------- Add Task Dialog ----------
    def open_add_task_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("เพิ่มงานใหม่")
        dialog.geometry("340x470")
        dialog.transient(self.root)
        dialog.grab_set()

        def label(parent, text):
            ttk.Label(parent, text=text).pack(anchor="w", padx=10, pady=(10, 0))

        label(dialog, "ชื่องาน:")
        title_entry = ttk.Entry(dialog, width=40)
        title_entry.pack(padx=10)

        label(dialog, "รายละเอียด:")
        desc_entry = ttk.Entry(dialog, width=40)
        desc_entry.pack(padx=10)

        label(dialog, "ประเภทงาน:")
        type_combo = ttk.Combobox(dialog, state="readonly",
                                   values=["งานมีกำหนดส่ง", "งานทำซ้ำ"])
        type_combo.set("งานมีกำหนดส่ง")
        type_combo.pack(padx=10)

        label(dialog, "ระดับความสำคัญ:")
        priority_combo = ttk.Combobox(dialog, state="readonly",
                                       values=list(PRIORITY_LABEL.values()))
        priority_combo.set(PRIORITY_LABEL[2])
        priority_combo.pack(padx=10)

        # ช่องที่เปลี่ยนตามประเภทงาน (แสดงทีละแบบ)
        extra = ttk.Frame(dialog)
        extra.pack(fill="x")
        due_frame = ttk.Frame(extra)
        label(due_frame, "กำหนดส่ง (YYYY-MM-DD):")
        due_entry = ttk.Entry(due_frame, width=40)
        due_entry.pack(padx=10)
        interval_frame = ttk.Frame(extra)
        label(interval_frame, "รอบทำซ้ำ:")
        interval_combo = ttk.Combobox(interval_frame, state="readonly",
                                       values=["daily", "weekly", "monthly"])
        interval_combo.set("daily")
        interval_combo.pack(padx=10)

        def update_fields(*_):
            due_frame.pack_forget()
            interval_frame.pack_forget()
            (due_frame if type_combo.get() == "งานมีกำหนดส่ง" else interval_frame).pack(fill="x")

        type_combo.bind("<<ComboboxSelected>>", update_fields)
        update_fields()

        label(dialog, "หมวดหมู่ (ไม่บังคับ):")
        category_entry = ttk.Entry(dialog, width=40)
        category_entry.pack(padx=10)

        label(dialog, "คะแนนความสำคัญ (จำนวนเต็ม):")
        score_entry = ttk.Entry(dialog, width=40)
        score_entry.insert(0, "0")
        score_entry.pack(padx=10)

        def on_submit():
            title = title_entry.get().strip()
            if not title:
                messagebox.showerror("ผิดพลาด", "กรุณากรอกชื่องาน")
                return

            priority = {v: k for k, v in PRIORITY_LABEL.items()}[priority_combo.get()]
            category = None
            if category_entry.get().strip():
                category = self.manager.add_category(category_entry.get().strip())

            try:
                if type_combo.get() == "งานมีกำหนดส่ง":
                    due_text = due_entry.get().strip()
                    due_date = datetime.strptime(due_text, "%Y-%m-%d").date() if due_text else None
                    task = DeadlineTask(title, desc_entry.get(), due_date, priority, category)
                else:
                    task = RecurringTask(title, desc_entry.get(), None, priority,
                                          category, interval_combo.get())
            except ValueError as e:
                messagebox.showerror("ผิดพลาด", str(e))
                return

            score_text = score_entry.get().strip()
            try:
                task.score = int(score_text) if score_text else 0
            except ValueError:
                messagebox.showerror("ผิดพลาด", "คะแนนต้องเป็นจำนวนเต็ม")
                return

            self.manager.add_task(task)
            self.refresh_view()
            dialog.destroy()

        ttk.Button(dialog, text="เพิ่มงาน", command=on_submit).pack(pady=20)


def run_app():
    root = tk.Tk()
    TodoApp(root)
    root.mainloop()
