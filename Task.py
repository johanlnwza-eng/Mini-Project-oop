from abc import ABC, abstractmethod
from datetime import date, datetime
import itertools

_id_counter = itertools.count(1)

class Task(ABC):
    """Abstract base class สำหรับงานทุกประเภทในระบบ"""

    def __init__(self, title, description="", due_date=None, priority=2,
                 category=None, score=0):
        # --- Encapsulation: attribute เป็น private ทั้งหมด ---
        self.__id = next(_id_counter)
        self.__title = title
        self.__description = description
        self.__due_date = due_date          # datetime.date หรือ None
        self.__priority = priority          # 1 = สูง, 2 = กลาง, 3 = ต่ำ
        self.__is_completed = False
        self.__category = category          # instance ของ Category (อาจเป็น None)
        self.__score = score                # คะแนนที่ผู้ใช้กรอกเอง (ไม่มีการคำนวณ)
        self.__created_at = datetime.now()

    # ---------- Getter / Setter (เข้าถึง private attribute) ----------
    @property
    def id(self):
        return self.__id

    @property
    def title(self):
        return self.__title

    @title.setter
    def title(self, value):
        if not value or not value.strip():
            raise ValueError("ชื่องาน (title) ห้ามเป็นค่าว่าง")
        self.__title = value.strip()

    @property
    def description(self):
        return self.__description

    @description.setter
    def description(self, value):
        self.__description = value

    @property
    def due_date(self):
        return self.__due_date

    @due_date.setter
    def due_date(self, value):
        self.__due_date = value

    @property
    def priority(self):
        return self.__priority

    @priority.setter
    def priority(self, value):
        if value not in (1, 2, 3):
            raise ValueError("priority ต้องเป็น 1 (สูง), 2 (กลาง) หรือ 3 (ต่ำ)")
        self.__priority = value

    @property
    def is_completed(self):
        return self.__is_completed

    @property
    def category(self):
        return self.__category

    @category.setter
    def category(self, value):
        self.__category = value

    @property
    def score(self):
        return self.__score

    @score.setter
    def score(self, value):
        if not isinstance(value, int):
            raise ValueError("คะแนนต้องเป็นจำนวนเต็ม")
        self.__score = value

    @property
    def created_at(self):
        return self.__created_at

    # ---------- Method ปกติ ----------
    def mark_complete(self):
        """เปลี่ยนสถานะงานเป็นเสร็จแล้ว"""
        self.__is_completed = True

    def mark_incomplete(self):
        """ยกเลิกสถานะเสร็จ (เผื่อกดผิด)"""
        self.__is_completed = False

    def days_until_due(self):
        """จำนวนวันที่เหลือก่อนถึง due_date (ติดลบ = เลยกำหนดแล้ว)"""
        if self.__due_date is None:
            return None
        return (self.__due_date - date.today()).days

    def get_info(self):
        """คืนค่า dict สรุปข้อมูลงาน สำหรับแสดงผลใน GUI"""
        return {
            "id": self.__id,
            "title": self.__title,
            "description": self.__description,
            "due_date": self.__due_date.isoformat() if self.__due_date else "-",
            "priority": self.__priority,
            "is_completed": self.__is_completed,
            "category": self.__category.name if self.__category else "-",
            "type": self.get_type_label(),
            "score": self.__score,
        }

    # ---------- Abstraction: ทุก subclass ต้อง implement เอง ----------
    @abstractmethod
    def get_type_label(self):
        """ชื่อประเภทงานสำหรับแสดงผล -> Polymorphism (แต่ละ subclass คืนค่าต่างกัน)"""
        raise NotImplementedError

    def __str__(self):
        status = "เสร็จแล้ว" if self.__is_completed else "ยังไม่เสร็จ"
        return f"[{self.get_type_label()}] {self.__title} ({status})"


class DeadlineTask(Task):
    """งานที่มีกำหนดส่งชัดเจน -> Inheritance: สืบทอดจาก Task"""

    def get_type_label(self):
        return "งานมีกำหนดส่ง"

    def __str__(self):
        days_left = self.days_until_due()
        due_text = f"เหลือ {days_left} วัน" if days_left is not None and days_left >= 0 else "เลยกำหนดแล้ว"
        return f"{super().__str__()} - กำหนดส่ง: {due_text}"


class RecurringTask(Task):
    """งานที่ทำซ้ำเป็นรอบ เช่น รายวัน/รายสัปดาห์ -> Inheritance: สืบทอดจาก Task"""

    VALID_INTERVALS = ("daily", "weekly", "monthly")

    def __init__(self, title, description="", due_date=None, priority=2,
                 category=None, recurrence_interval="daily", score=0):
        super().__init__(title, description, due_date, priority, category, score)
        if recurrence_interval not in self.VALID_INTERVALS:
            raise ValueError(f"recurrence_interval ต้องเป็นหนึ่งใน {self.VALID_INTERVALS}")
        self.__recurrence_interval = recurrence_interval
        self.__times_completed = 0

    @property
    def recurrence_interval(self):
        return self.__recurrence_interval

    @property
    def times_completed(self):
        return self.__times_completed

    def get_type_label(self):
        return "งานทำซ้ำ"

    def mark_complete(self):
        """
        override method ปกติ: งานซ้ำเมื่อทำเสร็จรอบนี้ ให้เพิ่มตัวนับ
        แล้วคงสถานะ "ยังไม่เสร็จ" เพื่อรอรอบถัดไป
        """
        self.__times_completed += 1

    def generate_next_instance(self):
        """สร้าง RecurringTask รอบถัดไป (คืน object ใหม่)"""
        return RecurringTask(
            title=self.title,
            description=self.description,
            due_date=self.due_date,
            priority=self.priority,
            category=self.category,
            recurrence_interval=self.__recurrence_interval,
            score=self.score,
        )

    def __str__(self):
        return f"{super().__str__()} - ทำซ้ำ: {self.__recurrence_interval} (ทำไปแล้ว {self.__times_completed} ครั้ง)"
