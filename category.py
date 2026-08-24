"""
category.py

Category ใช้จัดกลุ่มงาน เช่น "งานเรียน", "งานบ้าน", "ส่วนตัว"
แสดงหลักการ Encapsulation อีกจุดหนึ่งของระบบ
"""


class Category:
    def __init__(self, name, color_code="#888888"):
        self.__name = name
        self.__color_code = color_code

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        if not value or not value.strip():
            raise ValueError("ชื่อหมวดหมู่ห้ามเป็นค่าว่าง")
        self.__name = value.strip()

    @property
    def color_code(self):
        return self.__color_code

    @color_code.setter
    def color_code(self, value):
        self.__color_code = value

    def __str__(self):
        return self.__name

    def __eq__(self, other):
        if not isinstance(other, Category):
            return False
        return self.__name == other.__name

    def __hash__(self):
        return hash(self.__name)
