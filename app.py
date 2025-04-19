import os
import shutil
import sqlite3
import pandas as pd
from urllib.parse import quote, unquote
from datetime import datetime
from flask import Flask, render_template, request, session, flash, redirect, url_for, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'secret123'
def create_table():
    conn = sqlite3.connect('projects.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS قيد_التنفيذ (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            اسم_المشروع TEXT NOT NULL,
            المحافظة TEXT NOT NULL,
            الشركة_المنفذة TEXT NOT NULL,
            الكلفة_الكلية REAL NOT NULL,
            تاريخ_بدء_المشروع DATE NOT NULL,
            تاريخ_الانتهاء_المتوقع DATE NOT NULL,
            نسبة_الانجاز_المخططة REAL NOT NULL,
            نسبة_الانجاز_الفعلية REAL NOT NULL,
            نسبة_الإحراف REAL,
            أسباب_الإحراف TEXT,
            مدير_المشروع TEXT,
            المهندس_القيم TEXT,
            البرنامج_الحكومي TEXT,
            تاريخ_التحديث DATE,
            الملاحظات TEXT
        )
    ''')
    conn.commit()
    conn.close()

create_table()  # التأكد من أن الجدول موجود
# إعدادات قاعدة البيانات
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///projects.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# تهيئة SQLAlchemy
db = SQLAlchemy(app)

# فلتر Jinja للاقتباس
@app.template_filter('quote')
def quote_filter(value):
    return quote(value)

# الاتصال بقاعدة البيانات (SQLite مباشرة)
def get_db_connection():
    conn = sqlite3.connect('projects.db')
    conn.row_factory = sqlite3.Row
    return conn

# تعريف نموذج جدول "قيد_التنفيذ" باستخدام SQLAlchemy
class قيد_التنفيذ(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    اسم_المشروع = db.Column(db.String(200), nullable=False)
    المحافظة = db.Column(db.String(100), nullable=False)
    الشركة_المنفذة = db.Column(db.String(100), nullable=False)
    الكلفة_الكلية = db.Column(db.Float, nullable=False)
    تاريخ_بدء_المشروع = db.Column(db.Date, nullable=False)
    تاريخ_الانتهاء_المتوقع = db.Column(db.Date, nullable=False)
    نسبة_الانجاز_المخططة = db.Column(db.Float, nullable=False)
    نسبة_الانجاز_الفعلية = db.Column(db.Float, nullable=False)
    نسبة_الإحراف = db.Column(db.Float, nullable=False)
    أسباب_الإحراف = db.Column(db.Text, nullable=True)
    مدير_المشروع = db.Column(db.String(100), nullable=False)
    المهندس_القيم = db.Column(db.String(100), nullable=False)
    البرنامج_الحكومي = db.Column(db.String(100), nullable=False)
    تاريخ_التحديث = db.Column(db.Date, nullable=False)
    الملاحظات = db.Column(db.Text, nullable=True)

# دالة لإنشاء قاعدة البيانات والجداول (باستخدام SQLite مباشرة)
def init_db():
    conn = sqlite3.connect('projects.db')
    c = conn.cursor()

    # جدول المستخدمين
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # جدول المشاريع
    c.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            التسلسل INTEGER,
            المحافظة TEXT,
            المشروع TEXT UNIQUE,
            مدرج_في_وزارة_التخطيط TEXT,
            مؤشر_لدى_وزارة_المالية TEXT,
            الكلفة_الكلية REAL,
            الاستثناء_من_أساليب_التعاقد TEXT,
            استثناء TEXT,
            الإعلان TEXT,
            دراسة_سيرة_ذاتية BOOLEAN,
            الدعوات BOOLEAN,
            الوثيقة_القياسية BOOLEAN,
            التخويل BOOLEAN,
            تاريخ_غلق_الدعوات DATE,
            لجان_الفتح BOOLEAN,
            لجنة_تحليل BOOLEAN,
            قرار_لجنة_التحليل_الى_دائرة_العقود BOOLEAN,
            لجنة_المراجعة والمصادقة BOOLEAN,
            الإحالة BOOLEAN,
            مسودة_العقد BOOLEAN,
            توقيع_العقد BOOLEAN,
            ملاحظات TEXT
        )
    ''')

    # إضافة مستخدم افتراضي
    c.execute("SELECT * FROM users WHERE username = 'admin'")
    if not c.fetchone():
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                  ('admin', generate_password_hash('admin123')))

    conn.commit()
    conn.close()

# إنشاء الجداول عبر SQLAlchemy
with app.app_context():
    db.create_all()

# إنشاء باقي الجداول وإضافة المستخدم الافتراضي
init_db()
# صفحة تسجيل الدخول
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            session['username'] = username
            flash('تم تسجيل الدخول بنجاح!', 'success')
            return redirect(url_for('home'))
        else:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة.', 'danger')
    return render_template('login.html')
@app.route('/mplanning')
def mplanning():
    return render_template('mplanning.html')
@app.route('/execution_projects')
def execution_projects():
    return render_template('execution_projects.html')

# صفحة تسجيل المستخدمين
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            flash('يرجى إدخال اسم مستخدم وكلمة مرور.', 'danger')
            return redirect(url_for('register'))

        conn = get_db_connection()
        c = conn.cursor()

        try:
            hashed_password = generate_password_hash(password)
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
            flash('تم إنشاء الحساب بنجاح! يمكنك الآن تسجيل الدخول.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('اسم المستخدم موجود بالفعل. اختر اسمًا آخر.', 'warning')
        finally:
            conn.close()

    return render_template('register.html')

# تسجيل الخروج
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('تم تسجيل الخروج.', 'info')
    return redirect(url_for('login'))
@app.route('/home', methods=['GET', 'POST'])
def home():
    if 'username' not in session:
        flash('يجب تسجيل الدخول أولاً!', 'warning')
        return redirect(url_for('login'))
    projects = get_projects()  # استرجاع المشاريع
    return render_template('home.html', projects=projects)  # تمرير المشاريع إلى القالب
# دالة لاسترجاع المشاريع من قاعدة البيانات
def get_projects():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM projects")
    projects = c.fetchall()
    conn.close()
    return projects

# إضافة مشروع
@app.route('/add_project', methods=['GET', 'POST'])
def add_project():
    if 'username' not in session:
        flash('يجب تسجيل الدخول أولاً!', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        البيانات = {
            'التسلسل': request.form.get('التسلسل', '').strip(),
            'المحافظة': request.form.get('المحافظة', '').strip(),
            'المشروع': request.form.get('المشروع', '').strip(),
            'مدرج_في_وزارة_التخطيط': request.form.get('مدرج_في_وزارة_التخطيط', '').strip(),
            'مؤشر_لدى_وزارة_المالية': request.form.get('مؤشر_لدى_وزارة_المالية', '').strip(),
            'الكلفة_الكلية': request.form.get('الكلفة_الكلية', '').strip(),
            'الاستثناء_من_أساليب_التعاقد': request.form.get('الاستثناء_من_أساليب_التعاقد', '').strip(),
            'استثناء': request.form.get('استثناء', '').strip(),
            'الإعلان': request.form.get('الإعلان', '').strip(),
            'تاريخ_غلق_الدعوات': request.form.get('تاريخ_غلق_الدعوات', '').strip(),
            'لجنة_تحليل': request.form.get('لجنة_تحليل', '').strip(),
            'قرار_لجنة_التحليل_الى_دائرة_العقود': request.form.get('قرار_لجنة_التحليل_الى_دائرة_العقود', '').strip(),
            'لجنة_المراجعة والمصادقة': request.form.get('لجنة_المراجعة والمصادقة', '').strip(),
            'الإحالة': request.form.get('الإحالة', '').strip(),
            'مسودة_العقد': request.form.get('مسودة_العقد', '').strip(),
            'توقيع_العقد': request.form.get('توقيع_العقد', '').strip(),
            'ملاحظات': request.form.get('ملاحظات', '').strip(),
            'دراسة_سيرة_ذاتية': 'صح' if request.form.get('دراسة_سيرة_ذاتية') else '',
            'الدعوات': 'صح' if request.form.get('الدعوات') else '',
            'الوثيقة_القياسية': 'صح' if request.form.get('الوثيقة_القياسية') else '',
            'التخويل': 'صح' if request.form.get('التخويل') else '',
            'لجان_الفتح': 'صح' if request.form.get('لجان_الفتح') else ''
        }

        try:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute('''INSERT INTO projects (
                            التسلسل, المحافظة, المشروع, مدرج_في_وزارة_التخطيط, مؤشر_لدى_وزارة_المالية, 
                            الكلفة_الكلية, الاستثناء_من_أساليب_التعاقد, استثناء, الإعلان, 
                            تاريخ_غلق_الدعوات, لجنة_تحليل, قرار_لجنة_التحليل_الى_دائرة_العقود, 
                            لجنة_المراجعة_والمصادقة, الإحالة, مسودة_العقد, توقيع_العقد, ملاحظات, 
                            دراسة_سيرة_ذاتية, الدعوات, الوثيقة_القياسية, التخويل, لجان_الفتح
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                      tuple(البيانات.values()))

            conn.commit()
            flash('تمت إضافة المشروع بنجاح!', 'success')
            return redirect(url_for('home'))
        except Exception as e:
            flash(f'حدث خطأ أثناء إضافة المشروع: {str(e)}', 'danger')
        finally:
            conn.close()

    return render_template('add_project.html')
# تعديل مشروع
@app.route('/edit_project', methods=['GET', 'POST'])
def edit_project():
    if 'username' not in session:
        flash('يجب تسجيل الدخول أولاً!', 'warning')
        return redirect(url_for('login'))

    مشاريع = []

    if request.method == 'POST':
        اسم_المشروع = request.form.get('اسم_المشروع', '').strip()

        if اسم_المشروع:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("SELECT * FROM projects WHERE المشروع = ?", (اسم_المشروع,))
            مشاريع = c.fetchall()
            conn.close()

            if not مشاريع:
                flash("لا توجد نتائج مطابقة للبحث.", "warning")
    return render_template('edit_project.html', مشاريع=مشاريع)
@app.route('/update_project', methods=['POST'])
def update_project():
    if 'username' not in session:
        flash('يجب تسجيل الدخول أولاً!', 'warning')
        return redirect(url_for('login'))

    project_id = request.form.get('project_id')
    if not project_id:
        flash('لم يتم تحديد المشروع.', 'danger')
        return redirect(url_for('home'))

    try:
        البيانات = {
            'المشروع': request.form.get('المشروع'),
            'المحافظة': request.form.get('المحافظة'),
            'مدرج_في_وزارة_التخطيط': request.form.get('مدرج_في_وزارة_التخطيط'),
            'مؤشر_لدى_وزارة_المالية': request.form.get('مؤشر_لدى_وزارة_المالية'),
            'الكلفة_الكلية': request.form.get('الكلفة_الكلية'),
            'الاستثناء_من_أساليب_التعاقد': request.form.get('الاستثناء_من_أساليب_التعاقد'),
            'استثناء': request.form.get('استثناء'),
            'الإعلان': request.form.get('الإعلان'),
            'تاريخ_غلق_الدعوات': request.form.get('تاريخ_غلق_الدعوات'),
            'لجنة_تحليل': request.form.get('لجنة_تحليل'),
            'قرار_لجنة_التحليل_الى_دائرة_العقود': request.form.get('قرار_لجنة_التحليل_الى_دائرة_العقود'),
            'لجنة_المراجعة_والمصادقة': request.form.get('لجنة_المراجعة_والمصادقة'),
            'الإحالة': request.form.get('الإحالة'),
            'مسودة_العقد': request.form.get('مسودة_العقد'),
            'توقيع_العقد': request.form.get('توقيع_العقد'),
            'ملاحظات': request.form.get('ملاحظات'),
            'دراسة_سيرة_ذاتية': 'صح' if request.form.get('دراسة_سيرة_ذاتية') else '',
            'الدعوات': 'صح' if request.form.get('الدعوات') else '',
            'الوثيقة_القياسية': 'صح' if request.form.get('الوثيقة_القياسية') else '',
            'التخويل': 'صح' if request.form.get('التخويل') else '',
            'لجان_الفتح': 'صح' if request.form.get('لجان_الفتح') else ''
        }
        conn = get_db_connection()
        c = conn.cursor()
        update_query = '''UPDATE projects SET 
            المشروع = ?, المحافظة = ?, مدرج_في_وزارة_التخطيط = ?, مؤشر_لدى_وزارة_المالية = ?, الكلفة_الكلية = ?,
            الاستثناء_من_أساليب_التعاقد = ?, استثناء = ?, الإعلان = ?, تاريخ_غلق_الدعوات = ?, لجنة_تحليل = ?,
            قرار_لجنة_التحليل_الى_دائرة_العقود = ?, لجنة_المراجعة_والمصادقة = ?, الإحالة = ?, مسودة_العقد = ?,
            توقيع_العقد = ?, ملاحظات = ?, دراسة_سيرة_ذاتية = ?, الدعوات = ?, الوثيقة_القياسية = ?, التخويل = ?, لجان_الفتح = ?
            WHERE id = ?
        '''
        c.execute(update_query, (*البيانات.values(), project_id))
        conn.commit()
        conn.close()
        flash('تم تحديث بيانات المشروع بنجاح!', 'success')
    except Exception as e:
        flash(f'حدث خطأ أثناء التحديث: {e}', 'danger')

    return redirect(url_for('home'))

# حذف مشروع
@app.route('/delete_project', methods=['GET', 'POST'])
def delete_project():
    if 'username' not in session:
        flash('يجب تسجيل الدخول أولاً!', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        project_name = request.form.get('project_name', '').strip()

        if project_name:
            try:
                conn = get_db_connection()
                c = conn.cursor()
                c.execute("SELECT * FROM projects WHERE المشروع = ?", (project_name,))
                project = c.fetchone()

                if project:
                    c.execute("DELETE FROM projects WHERE المشروع = ?", (project_name,))
                    conn.commit()
                    flash(f'تم حذف المشروع "{project_name}" بنجاح!', 'success')
                    return redirect(url_for('delete_project'))
                else:
                    flash(f'المشروع "{project_name}" غير موجود!', 'danger')
            except Exception as e:
                flash(f'حدث خطأ أثناء الحذف: {str(e)}', 'danger')
            finally:
                conn.close()
        else:
            flash('يرجى إدخال اسم المشروع!', 'danger')

    return render_template('delete_project.html')

# عرض جميع المشاريع
@app.route('/reportall', methods=['GET'])
def reportall():
    المشاريع = []
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM projects")
        النتائج = c.fetchall()
        المشاريع = [dict(row) for row in النتائج]
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()
    return render_template('reportall.html', المشاريع=المشاريع)
@app.route('/reports', methods=['GET', 'POST'])
def reports():
    المشاريع = []

    if request.method == 'POST':
        اسم_المشروع = request.form.get('اسم_المشروع', '').strip()

        try:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("SELECT * FROM projects WHERE المشروع LIKE ?", ('%' + اسم_المشروع + '%',))
            المشاريع = c.fetchall()
            conn.close()
            if not المشاريع:
                flash("لا توجد نتائج مطابقة للبحث.", "warning")
        except sqlite3.Error as e:
            flash(f"خطأ في قاعدة البيانات: {e}", "danger")

    return render_template('reports.html', المشاريع=المشاريع)
@app.route('/reports1', methods=['GET', 'POST'])
def reports1():
    المشاريع = []
    if request.method == 'POST':
        المحافظة = request.form.get('المحافظة', '').strip()

        if المحافظة:
            try:
                conn = get_db_connection()
                c = conn.cursor()
                c.execute("SELECT * FROM projects WHERE المحافظة = ?", (المحافظة,))
                المشاريع = c.fetchall()

                if not المشاريع:
                    flash("لا توجد نتائج.", "warning")
            except sqlite3.Error as e:
                flash(f"خطأ في قاعدة البيانات: {e}", "danger")
            finally:
                conn.close()

    return render_template('reports1.html', المشاريع=المشاريع)
@app.route('/backup', methods=['POST'])
def backup():
    db_file = 'projects.db'
    backup_folder = r'C:\project_backups'  # ضع هنا المسار الكامل على C
    backup_file = os.path.join(backup_folder, 'backup_projects.db')

    try:
        os.makedirs(backup_folder, exist_ok=True)  # إنشاء المجلد إذا ما كان موجود
        shutil.copy(db_file, backup_file)  # نسخ قاعدة البيانات إلى المجلد
        flash(f'تم إنشاء النسخة الاحتياطية بنجاح في: {backup_file}', 'success')
    except Exception as e:
        flash(f'حدث خطأ أثناء إنشاء النسخة الاحتياطية: {e}', 'danger')
    return redirect(url_for('home'))  # رجوع للصفحة الرئيسية أو غيرها حسب رغبتك
@app.route('/addproject', methods=['GET', 'POST'])
def addproject():

    if request.method == 'POST':
        البيانات = {
            'اسم_المشروع': request.form.get('اسم_المشروع', '').strip(),
            'المحافظة': request.form.get('المحافظة', '').strip(),
            'الشركة_المنفذة': request.form.get('الشركة_المنفذة', '').strip(),
            'الكلفة_الكلية': request.form.get('الكلفة_الكلية', '').strip(),
            'تاريخ_بدء_المشروع': request.form.get('تاريخ_بدء_المشروع', '').strip(),
            'تاريخ_الانتهاء_المتوقع': request.form.get('تاريخ_الانتهاء_المتوقع', '').strip(),
            'نسبة_الانجاز_المخططة': request.form.get('نسبة_الانجاز_المخططة', '').strip(),
            'نسبة_الانجاز_الفعلية': request.form.get('نسبة_الانجاز_الفعلية', '').strip(),
            'نسبة_الإحراف': request.form.get('نسبة_الإحراف', '').strip(),
            'أسباب_الإحراف': request.form.get('أسباب_الإحراف', '').strip(),
            'مدير_المشروع': request.form.get('مدير_المشروع', '').strip(),
            'المهندس_القيم': request.form.get('المهندس_القيم', '').strip(),
            'البرنامج_الحكومي': request.form.get('البرنامج_الحكومي', '').strip(),
            'تاريخ_التحديث': request.form.get('تاريخ_التحديث', '').strip(),
            'الملاحظات': request.form.get('الملاحظات', '').strip()
        }

        try:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute('''INSERT INTO قيد_التنفيذ (
                            اسم_المشروع, المحافظة, الشركة_المنفذة, الكلفة_الكلية, تاريخ_بدء_المشروع, 
                            تاريخ_الانتهاء_المتوقع, نسبة_الانجاز_المخططة, نسبة_الانجاز_الفعلية, 
                            نسبة_الإحراف, أسباب_الإحراف, مدير_المشروع, المهندس_القيم, البرنامج_الحكومي, 
                            تاريخ_التحديث, الملاحظات
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                      tuple(البيانات.values()))
            conn.commit()
            flash('تمت إضافة المشروع قيد التنفيذ بنجاح!', 'success')
            return redirect(url_for('home'))
        except Exception as e:
            flash(f'حدث خطأ أثناء إضافة المشروع قيد التنفيذ: {str(e)}', 'danger')
        finally:
            conn.close()
    return render_template('addproject.html')


@app.route('/export_excel', methods=['GET'])
def export_excel():
    # الاتصال بقاعدة البيانات
    conn = sqlite3.connect('projects.db')

    # قراءة البيانات من الجدول projects إلى DataFrame
    df = pd.read_sql_query("SELECT * FROM projects", conn)

    # غلق الاتصال بقاعدة البيانات
    conn.close()

    # تحديد اسم ملف Excel
    output_file = 'projects.xlsx'

    # تصدير البيانات إلى ملف Excel
    df.to_excel(output_file, index=False, engine='openpyxl')

    # إرسال الملف للمستخدم
    return send_file(output_file, as_attachment=True)
@app.route('/edit_projectadd', methods=['GET', 'POST'])
def edit_projectadd():
    المشروع = None
    if request.method == 'POST':
        اسم_المشروع = request.form['اسم_المشروع']
        conn = sqlite3.connect('projects.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM 'قيد_التنفيذ' WHERE اسم_المشروع = ?", (اسم_المشروع,))
        المشروع = c.fetchone()
        conn.close()
        if not المشروع:
            flash('لم يتم العثور على مشروع بهذا الاسم.', 'warning')
    return render_template('edit_projectadd.html', المشروع=المشروع)


@app.route('/update_projectadd', methods=['POST'])
def update_projectadd():
    id = request.form['id']
    البيانات = (
        request.form['اسم_المشروع'],
        request.form['المحافظة'],
        request.form['الشركة_المنفذة'],
        request.form['الكلفة_الكلية'],
        request.form['تاريخ_بدء_المشروع'],
        request.form['تاريخ_الانتهاء_المتوقع'],
        request.form['نسبة_الانجاز_المخططة'],
        request.form['نسبة_الانجاز_الفعلية'],
        request.form['نسبة_الإحراف'],
        request.form['أسباب_الإحراف'],
        request.form['مدير_المشروع'],
        request.form['المهندس_القيم'],
        request.form['البرنامج_الحكومي'],
        request.form['تاريخ_التحديث'],
        request.form['الملاحظات'],
        id
    )
    conn = sqlite3.connect('projects.db')
    c = conn.cursor()
    c.execute('''
        UPDATE "قيد_التنفيذ" SET 
            اسم_المشروع=?, المحافظة=?, الشركة_المنفذة=?, الكلفة_الكلية=?, 
            تاريخ_بدء_المشروع=?, تاريخ_الانتهاء_المتوقع=?, نسبة_الانجاز_المخططة=?, 
            نسبة_الانجاز_الفعلية=?, نسبة_الإحراف=?, أسباب_الإحراف=?, مدير_المشروع=?, 
            المهندس_القيم=?, البرنامج_الحكومي=?, تاريخ_التحديث=?, الملاحظات=?
        WHERE id=?
    ''', البيانات)
    conn.commit()
    conn.close()
    flash("تم تحديث المشروع بنجاح", "success")
    return redirect(url_for('edit_projectadd'))
@app.route('/report_projectadd')
def report_projectadd():
    conn = sqlite3.connect('projects.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM 'قيد_التنفيذ'")
    المشاريع = c.fetchall()
    conn.close()
    # إرسال البيانات إلى القالب
    return render_template('report_projectadd.html', المشاريع=المشاريع)
# تشغيل التطبيق
if __name__ == '__main__':
    init_db()
    app.run(debug=True)