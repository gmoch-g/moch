import sqlite3

# الاتصال بقاعدة البيانات
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# إنشاء جدول المشاريع إذا لم يكن موجودًا
cursor.execute('''
    CREATE TABLE IF
