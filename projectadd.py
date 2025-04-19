from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import sqlite3

app = Flask(__name__)

# Route لإظهار نموذج إضافة المشروع
@app.route('/addproject', methods=['GET', 'POST'])
def addproject():
    if request.method == 'POST':
        # استخراج البيانات من النموذج
        المحافظة = request.form['المحافظة']
        اسم_المشروع = request.form['اسم_المشروع']
        الكلفة_الكلية = request.form['الكلفة_الكلية']
        نسبة_الانجاز_المخططة = request.form['نسبة_الانجاز_المخططة']
        نسبة_الانجاز_الفعلية = request.form['نسبة_الانجاز_الفعلية']
        تاريخ_المباشرة = request.form['تاريخ_المباشرة']
        مدة_المشروع = request.form['مدة_المشروع']
        الشركة_المنفذة = request.form['الشركة_المنفذة']
        اسم_الجهة_التعاقدية = request.form['اسم_الجهة_التعاقدية']
        الملاحظات = request.form['الملاحظات']

        # اتصال بقاعدة البيانات
        conn = sqlite3.connect('projects.db')
        cursor = conn.cursor()

        # إدخال البيانات في جدول "قيد_التنفيذ"
        cursor.execute('''
            INSERT INTO قيد_التنفيذ (المحافظة, اسم_المشروع, الكلفة_الكلية, نسبة_الانجاز_المخططة, 
            نسبة_الانجاز_الفعلية, تاريخ_المباشرة, مدة_المشروع, الشركة_المنفذة, 
            اسم_الجهة_التعاقدية, الملاحظات)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (المحافظة, اسم_المشروع, الكلفة_الكلية, نسبة_الانجاز_المخططة,
              نسبة_الانجاز_الفعلية, تاريخ_المباشرة, مدة_المشروع, الشركة_المنفذة,
              اسم_الجهة_التعاقدية, الملاحظات))

        # حفظ التغييرات وإغلاق الاتصال
        conn.commit()
        conn.close()

        # إعادة توجيه المستخدم إلى صفحة عرض المشاريع أو أي مكان آخر بعد الإضافة
        return redirect(url_for('home'))

    # عرض النموذج
    return render_template('addproject.html')

# صفحة رئيسية افتراضية
@app.route('/')
def home():
    return "مرحباً بك في الصفحة الرئيسية"

if __name__ == '__main__':
    app.run(debug=True)
