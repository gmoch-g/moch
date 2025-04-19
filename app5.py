import sqlite3
import pandas as pd
from flask import Flask, render_template, request, session, send_file
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
app.secret_key = 'secret123'
# إنشاء قاعدة البيانات والجداول
def init_db():
    conn = sqlite3.connect('projects.db')
    c = conn.cursor()

    # جدول المشاريع
    c.execute('''CREATE TABLE IF NOT EXISTS projects (
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
                )''')
    import sqlite3
    # الاتصال بقاعدة البيانات
    conn = sqlite3.connect('projects.db')
    cursor = conn.cursor()
    # إنشاء جدول قيد_التنفيذ إذا لم يكن موجودًا
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS قيد_التنفيذ (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        المحافظة TEXT NOT NULL,
        اسم_المشروع TEXT NOT NULL,
        الكلفة_الكلية REAL NOT NULL,
        نسبة_الانجاز_المخططة REAL NOT NULL,
        نسبة_الانجاز_الفعلية REAL NOT NULL,
        تاريخ_المباشرة TEXT NOT NULL,
        مدة_المشروع INTEGER NOT NULL,
        الشركة_المنفذة TEXT NOT NULL,
        اسم_الجهة_التعاقدية TEXT NOT NULL,
        الملاحظات TEXT
    );
    ''')
    # إنشاء جدول قيد_التنفيذ
    c.execute('''
        CREATE TABLE IF NOT EXISTS قيد_التنفيذ (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            المحافظة TEXT NOT NULL,
            اسم_المشروع TEXT NOT NULL,
            الكلفة_الكلية REAL NOT NULL,
            نسبة_الانجاز_المخططة REAL NOT NULL,
            نسبة_الانجاز_الفعلية REAL NOT NULL,
            تاريخ_المباشرة TEXT NOT NULL,
            مدة_المشروع INTEGER NOT NULL,
            الشركة_المنفذة TEXT NOT NULL,
            اسم_الجهة_التعاقدية TEXT NOT NULL,
            الملاحظات TEXT
        );
        ''')
    # تأكيد التغييرات وإغلاق الاتصال
    conn.commit()
    conn.close()
# استدعاء الدالة لإنشاء الجداول
init_db()
    # جدول المستخدمين
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )''')

    # إضافة مستخدم افتراضي إذا لم يكن موجودًا
    c.execute("SELECT * FROM users WHERE username = 'admin'")
    if not c.fetchone():
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                  ('admin', generate_password_hash('admin123')))
    conn.commit()
    conn.close()
# دالة للاتصال بقاعدة البيانات
def get_db_connection():
    conn = sqlite3.connect('projects.db')
    conn.row_factory = sqlite3.Row
    return conn
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
# دالة النسخ الاحتياطي
@app.route('/backup_success')
def backup_success():
    return render_template('backup_success.html')
import os
import shutil
from flask import flash, redirect, url_for

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
@app.route('/restore_backup', methods=['POST'])
def restore_backup():
    file = request.files['backup_file']
    if file:
        file.save('db/project.db')  # مكان قاعدة البيانات
        flash("تم استرجاع النسخة الاحتياطية بنجاح", "success")
    return redirect(url_for('home'))
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
    if request.method == 'POST':
        project_id = request.form.get('project_id')

        اسم_المشروع = request.form.get('المشروع', '').strip()
        المحافظة = request.form.get('المحافظة', '').strip()
        مدرج_في_وزارة_التخطيط = request.form.get('مدرج_في_وزارة_التخطيط', '').strip()
        مؤشر_لدى_وزارة_المالية = request.form.get('مؤشر_لدى_وزارة_المالية', '').strip()
        الكلفة_الكلية = request.form.get('الكلفة_الكلية', '0').strip()
        الاستثناء_من_أساليب_التعاقد = request.form.get('الاستثناء_من_أساليب_التعاقد', '').strip()
        استثناء = request.form.get('استثناء', '').strip()
        الإعلان = request.form.get('الإعلان', '').strip()
        تاريخ_غلق_الدعوات = request.form.get('تاريخ_غلق_الدعوات', '').strip()
        لجنة_تحليل = request.form.get('لجنة_تحليل', '').strip()
        قرار_لجنة_التحليل_الى_دائرة_العقود = request.form.get('قرار_لجنة_التحليل_الى_دائرة_العقود', '').strip()
        لجنة_المراجعة_والمصادقة = request.form.get('لجنة_المراجعة_والمصادقة', '').strip()
        الإحالة = request.form.get('الإحالة', '').strip()
        مسودة_العقد = request.form.get('مسودة_العقد', '').strip()
        توقيع_العقد = request.form.get('توقيع_العقد', '').strip()
        ملاحظات = request.form.get('ملاحظات', '').strip()

        دراسة_سيرة_ذاتية = bool(request.form.get('دراسة_سيرة_ذاتية'))
        الدعوات = bool(request.form.get('الدعوات'))
        الوثيقة_القياسية = bool(request.form.get('الوثيقة_القياسية'))
        التخويل = bool(request.form.get('التخويل'))
        لجان_الفتح = bool(request.form.get('لجان_الفتح'))

        if project_id and اسم_المشروع and الكلفة_الكلية:
            conn = get_db_connection()
            try:
                c = conn.cursor()
                c.execute("""
                    UPDATE projects 
                    SET المشروع = ?, المحافظة = ?, مدرج_في_وزارة_التخطيط = ?, 
                        مؤشر_لدى_وزارة_المالية = ?, الكلفة_الكلية = ?, الاستثناء_من_أساليب_التعاقد = ?, 
                        استثناء = ?, الإعلان = ?, تاريخ_غلق_الدعوات = ?, لجنة_تحليل = ?, 
                        قرار_لجنة_التحليل_الى_دائرة_العقود = ?, لجنة_المراجعة_والمصادقة = ?, 
                        الإحالة = ?, مسودة_العقد = ?, توقيع_العقد = ?, ملاحظات = ?, 
                        دراسة_سيرة_ذاتية = ?, الدعوات = ?, الوثيقة_القياسية = ?, التخويل = ?, لجان_الفتح = ?
                    WHERE id = ?
                """, (اسم_المشروع, المحافظة, مدرج_في_وزارة_التخطيط,
                      مؤشر_لدى_وزارة_المالية, الكلفة_الكلية, الاستثناء_من_أساليب_التعاقد,
                      استثناء, الإعلان, تاريخ_غلق_الدعوات, لجنة_تحليل,
                      قرار_لجنة_التحليل_الى_دائرة_العقود, لجنة_المراجعة_والمصادقة,
                      الإحالة, مسودة_العقد, توقيع_العقد, ملاحظات,
                      دراسة_سيرة_ذاتية, الدعوات, الوثيقة_القياسية, التخويل, لجان_الفتح,
                      project_id))
                conn.commit()
                flash("تم تعديل المشروع بنجاح!", "success")
            except sqlite3.Error as e:
                flash(f"خطأ في تعديل المشروع: {e}", "danger")
            finally:
                conn.close()
        else:
            flash("يجب ملء جميع الحقول المطلوبة.", "warning")

    return redirect(url_for('edit_project'))


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


# دالة لتحميل ملف Excel
@app.route('/upload_excel', methods=['GET', 'POST'])
def upload_excel():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('ملف غير موجود', 'danger')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('يرجى اختيار ملف', 'danger')
            return redirect(request.url)

        try:
            df = pd.read_excel(file)
            المشاريع = df.to_dict(orient='records')
            return render_template('your_template.html', المشاريع=المشاريع)
        except Exception as e:
            flash(f'حدث خطأ: {e}', 'danger')
            return redirect(request.url)

    return render_template('your_template.html')


# تصدير البيانات إلى Excel
@app.route('/export_excel', methods=['GET'])
def export_excel():
    conn = sqlite3.connect('projects.db')
    df = pd.read_sql_query("SELECT * FROM projects", conn)
    conn.close()

    output_file = 'projects.xlsx'
    df.to_excel(output_file, index=False, engine='openpyxl')

    return send_file(output_file, as_attachment=True)


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
            c.execute("SELECT * FROM projects WHERE المشروع = ?", (اسم_المشروع,))
            المشاريع = c.fetchall()

            if not المشاريع:
                flash("لا توجد نتائج.", "warning")
        except sqlite3.Error as e:
            flash(f"خطأ في قاعدة البيانات: {e}", "danger")
        finally:
            conn.close()

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
@app.route('/addproject', methods=['POST'])
def addprject():
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

    conn = sqlite3.connect('projects.db')
    cursor = conn.cursor()

    # إدراج البيانات في جدول قيد_التنفيذ
    cursor.execute('''
    INSERT INTO قيد_التنفيذ (
        المحافظة, اسم_المشروع, الكلفة_الكلية, نسبة_الانجاز_المخططة,
        نسبة_الانجاز_الفعلية, تاريخ_المباشرة, مدة_المشروع,
        الشركة_المنفذة, اسم_الجهة_التعاقدية, الملاحظات
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (المحافظة, اسم_المشروع, الكلفة_الكلية, نسبة_الانجاز_المخططة,
          نسبة_الانجاز_الفعلية, تاريخ_المباشرة, مدة_المشروع,
          الشركة_المنفذة, اسم_الجهة_التعاقدية, الملاحظات))

    conn.commit()
    conn.close()

    return redirect(url_for('home'))
# تشغيل التطبيق
if __name__ == '__main__':
    init_db()
    app.run(debug=True)