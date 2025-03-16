from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'secret123'  # مفتاح الجلسة لتأمين الكوكيز

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
                    الإعلان DATE,
                    دراسة_سيرة_ذاتية BOOLEAN,
                    الدعوات BOOLEAN,
                    الوثيقة_القياسية BOOLEAN,
                    التخويل BOOLEAN,
                    تاريخ_غلق_الدعوات DATE,
                    لجان_الفتح BOOLEAN,
                    لجنة_تحليل TEXT,
                    قرار_لجنة_التحليل_الى_دائرة_العقود DATE,
                    لجنة_المراجعة_والمصادقة TEXT,
                    الإحالة TEXT,
                    مسودة_العقد TEXT,
                    توقيع_العقد DATE,
                    ملاحظات TEXT
                )''')

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

# صفحة تسجيل الدخول
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('projects.db')
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

        conn = sqlite3.connect('projects.db')
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
    conn = sqlite3.connect('projects.db')
    conn.row_factory = sqlite3.Row
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
        try:
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
                'لجنة_المراجعة_والمصادقة': request.form.get('لجنة_المراجعة_والمصادقة', '').strip(),
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

            conn = sqlite3.connect('projects.db')
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
            conn.close()

            flash('تمت إضافة المشروع بنجاح!', 'success')
            return redirect(url_for('add_project'))

        except Exception as e:
            flash(f'حدث خطأ أثناء إضافة المشروع: {str(e)}', 'danger')

    return render_template('add_project.html')

# البحث عن المشاريع
@app.route('/search_reports', methods=['POST'])
def search_reports():
    if 'username' not in session:
        return jsonify([])

    try:
        data = request.get_json()
        project_name = data.get('project_name', '').replace('_', ' ').strip()  # إزالة المسافات
        print("Searching for project:", project_name)  # طباعة اسم المشروع الذي يتم البحث عنه

        conn = sqlite3.connect('projects.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM projects WHERE المشروع LIKE ?", ('%' + project_name + '%',))
        reports = [dict(row) for row in c.fetchall()]
        print("Reports found:", reports)  # طباعة التقارير التي تم العثور عليها
        conn.close()

        return jsonify(reports)
    except Exception as e:
        print("Error:", str(e))  # طباعة الخطأ إذا حدث
        return jsonify([])
@app.route('/edit_project', methods=['GET', 'POST'])
@app.route('/edit_project', methods=['GET', 'POST'])
def edit_project():
    if 'username' not in session:
        flash('يجب تسجيل الدخول أولاً!', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        project_name = request.form.get('المشروع', '').strip()
        التسلسل = request.form.get('التسلسل', '')
        الإعلان = request.form.get('الإعلان', '')
        تاريخ_غلق_الدعوات = request.form.get('تاريخ_غلق_الدعوات', '')
        ملاحظات = request.form.get('ملاحظات', '')

        # تأكد من وجود اسم المشروع
        if not project_name:
            flash('يجب تحديد المشروع!', 'danger')
            return redirect(url_for('edit_project'))

        conn = None
        try:
            # الاتصال بقاعدة البيانات
            conn = sqlite3.connect('projects.db')
            c = conn.cursor()

            # تحديث المشروع في قاعدة البيانات
            c.execute('''UPDATE projects SET 
                            التسلسل=?, 
                            الإعلان=?, 
                            تاريخ_غلق_الدعوات=?, 
                            ملاحظات=? 
                         WHERE المشروع=?''',
                      (التسلسل, الإعلان, تاريخ_غلق_الدعوات, ملاحظات, project_name))
            conn.commit()

            flash(f'تم تعديل بيانات المشروع "{project_name}" بنجاح!', 'success')
        except Exception as e:
            flash(f'حدث خطأ أثناء التعديل: {str(e)}', 'danger')
        finally:
            if conn:
                conn.close()

        return redirect(url_for('edit_project'))  # إعادة توجيه إلى نفس الصفحة بعد الحفظ

    # إذا كانت الطلب GET، جلب المشاريع
    projects = get_projects()  # تأكد من وجود دالة لجلب المشاريع من قاعدة البيانات
    return render_template('edit_project.html', projects=projects)

def get_projects():
    conn = sqlite3.connect('projects.db')
    c = conn.cursor()
    c.execute("SELECT * FROM projects")
    projects = c.fetchall()
    conn.close()
    return projects
@app.route('/reports1', methods=['GET', 'POST'])
def reports1():
    المشاريع = []
    if request.method == 'POST':
        province = request.form.get('المحافظة')
        conn = sqlite3.connect('projects.db')
        c = conn.cursor()
        c.execute('SELECT * FROM projects WHERE المحافظة = ?', (province,))
        المشاريع = c.fetchall()
        conn.close()

        # تحويل البيانات إلى قائمة من القواميس مع ترتيب المفاتيح
        المشاريع = [
            {
                'التسلسل': مشروع[0],
                'المحافظة': مشروع[1],
                'المشروع': مشروع[2],
                'مدرج في وزارة التخطيط': مشروع[3],
                'مؤشر لدى وزارة المالية': مشروع[4],
                'الكلفة الكلية': مشروع[5],
                'الاستثناء من أساليب التعاقد': مشروع[6],
                'استثناء': مشروع[7],
                'الإعلان': مشروع[8],
                'تاريخ غلق الدعوات': مشروع[9],
                'لجنة تحليل': مشروع[10],
                'قرار لجنة التحليل إلى دائرة العقود': مشروع[11],
                'لجنة المراجعة والمصادقة': مشروع[12],
                'الإحالة': مشروع[13],
                'مسودة العقد': مشروع[14],
                'توقيع العقد': مشروع[15],
                'ملاحظات': مشروع[16],
                'دراسة سيرة ذاتية': مشروع[17],
                'الدعوات': مشروع[18],
                'الوثيقة القياسية': مشروع[19],
                'التخويل': مشروع[20],
                'لجان الفتح': مشروع[21],
            }
            for مشروع in المشاريع
        ]

    return render_template('reports1.html', المشاريع=المشاريع)
# حذف مشروع
@app.route('/delete_project', methods=['GET', 'POST'])
def delete_project():
    if 'username' not in session:
        flash('يجب تسجيل الدخول أولاً!', 'warning')
        return redirect(url_for('login'))

    project = None

    if request.method == 'POST':
        project_name = request.form.get('project_name', '').strip()

        if 'search' in request.form:
            if project_name:
                conn = sqlite3.connect('projects.db')
                c = conn.cursor()
                c.execute("SELECT * FROM projects WHERE المشروع = ?", (project_name,))
                project = c.fetchone()
                conn.close()

                if not project:
                    flash(f'المشروع "{project_name}" غير موجود!', 'danger')
            else:
                flash('يرجى إدخال اسم المشروع!', 'danger')

        elif 'delete' in request.form:
            if project_name:
                conn = sqlite3.connect('projects.db')
                c = conn.cursor()
                c.execute("DELETE FROM projects WHERE المشروع = ?", (project_name,))
                conn.commit()
                conn.close()
                flash(f'تم حذف المشروع "{project_name}" بنجاح!', 'success')
                return redirect(url_for('delete_project'))
            else:
                flash('يرجى إدخال اسم المشروع!', 'danger')

    return render_template('delete_project.html', project=project)
@app.route('/reports', methods=['GET', 'POST'])
def reports():
    المشاريع = []
    if request.method == 'POST':
        project_name = request.form.get('project_name', '').strip()
        conn = sqlite3.connect('projects.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM projects WHERE المشروع LIKE ?", ('%' + project_name + '%',))
        المشاريع = c.fetchall()
        conn.close()

        # تحويل البيانات إلى قائمة من القواميس
        المشاريع = [
            {
                'التسلسل': مشروع[0],
                'المحافظة': مشروع[1],
                'المشروع': مشروع[2],
                'مدرج_في_وزارة_التخطيط': مشروع[3],
                'مؤشر_لدى_وزارة_المالية': مشروع[4],
                'الكلفة_الكلية': مشروع[5],
                'الاستثناء_من_أساليب_التعاقد': مشروع[6],
                'استثناء': مشروع[7],
                'الإعلان': مشروع[8],
                'تاريخ_غلق_الدعوات': مشروع[9],
                'لجنة_تحليل': مشروع[10],
                'قرار_لجنة_التحليل_الى_دائرة_العقود': مشروع[11],
                'لجنة_المراجعة_والمصادقة': مشروع[12],
                'الإحالة': مشروع[13],
                'مسودة_العقد': مشروع[14],
                'توقيع_العقد': مشروع[15],
                'ملاحظات': مشروع[16],
                'دراسة_سيرة_ذاتية': مشروع[17],
                'الدعوات': مشروع[18],
                'الوثيقة_القياسية': مشروع[19],
                'التخويل': مشروع[20],
                'لجان_الفتح': مشروع[21],
            }
            for مشروع in المشاريع
        ]

    return render_template('reports.html', المشاريع=المشاريع)
@app.route('/search_project', methods=['POST'])
def search_project():
    if 'username' not in session:
        return jsonify([])

    try:
        data = request.get_json()
        project_name = data.get('project_name', '').strip()

        conn = sqlite3.connect('projects.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM projects WHERE LOWER(المشروع) = LOWER(?)", (project_name,))
        project = c.fetchone()
        conn.close()

        return jsonify(dict(project)) if project else jsonify([])
    except Exception as e:
        flash(f'حدث خطأ أثناء البحث: {str(e)}', 'danger')
        return jsonify([])
# تشغيل التطبيق
if __name__ == '__main__':
    init_db()
    app.run(debug=True)