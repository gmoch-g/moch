from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'secret123'  # مفتاح الجلسة لتأمين الكوكيز

# 🛠️ إنشاء قاعدة البيانات والجداول
def init_db():
    conn = sqlite3.connect('projects.db')
    c = conn.cursor()

    # جدول المشاريع
    c.execute('''CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    التسلسل INTEGER,
                    المحافظة TEXT,
                    المشروع TEXT UNIQUE,
                    الكلفة_الكلية REAL,
                    الإعلان DATE,
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


# 🏠 صفحة تسجيل الدخول
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        conn = sqlite3.connect('projects.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            session['username'] = username
            return redirect(url_for('home'))
        else:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة!', 'danger')

    return render_template('login.html')


# 📝 صفحة التسجيل
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


# 🏠 الصفحة الرئيسية
@app.route('/home', methods=['GET'])
def home():
    if 'username' not in session:
        flash('يجب تسجيل الدخول أولاً!', 'warning')
        return redirect(url_for('login'))
    return render_template('home.html')


# ➕ إضافة مشروع
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
                'الكلفة_الكلية': request.form.get('الكلفة_الكلية', '').strip(),
                'الإعلان': request.form.get('الإعلان', '').strip(),
                'ملاحظات': request.form.get('ملاحظات', '').strip()
            }

            conn = sqlite3.connect('projects.db')
            c = conn.cursor()
            c.execute('''INSERT INTO projects (التسلسل, المحافظة, المشروع, الكلفة_الكلية, الإعلان, ملاحظات)
                         VALUES (?, ?, ?, ?, ?, ?)''', tuple(البيانات.values()))
            conn.commit()
            conn.close()

            flash('تمت إضافة المشروع بنجاح!', 'success')
            return redirect(url_for('add_project'))

        except Exception as e:
            flash(f'حدث خطأ أثناء إضافة المشروع: {str(e)}', 'danger')

    return render_template('add_project.html')
# 📋 عرض المشاريع
@app.route('/reports', methods=['GET'])
def reports():
    if 'username' not in session:
        flash('يجب تسجيل الدخول أولاً!', 'warning')
        return redirect(url_for('login'))

    conn = sqlite3.connect('projects.db')
    c = conn.cursor()
    c.execute("SELECT * FROM projects")
    المشاريع = c.fetchall()
    conn.close()
    return render_template('reports.html', المشاريع=المشاريع)


# 📌 عرض المشاريع حسب المحافظة
@app.route('/reports1', methods=['GET', 'POST'])
def reports1():
    المشاريع = []

    if request.method == 'POST':
        province = request.form.get('المحافظة', '').strip()

        if province:
            try:
                conn = sqlite3.connect('projects.db')
                conn.row_factory = sqlite3.Row
                c = conn.cursor()
                c.execute('SELECT * FROM projects WHERE المحافظة = ?', (province,))
                المشاريع = [dict(row) for row in c.fetchall()]
                conn.close()

                if not المشاريع:
                    flash('لا توجد مشاريع في هذه المحافظة.', 'warning')
            except Exception as e:
                flash(f'حدث خطأ أثناء جلب البيانات: {str(e)}', 'danger')

    return render_template('reports1.html', المشاريع=المشاريع)
@app.route('/edit_project/<int:project_id>', methods=['GET', 'POST'])
def edit_project(project_id):
    if 'username' not in session:
        flash('يجب تسجيل الدخول أولاً!', 'warning')
        return redirect(url_for('login'))
    conn = sqlite3.connect('projects.db')
    c = conn.cursor()

    if request.method == 'POST':
        # استلام البيانات الجديدة من النموذج
        التسلسل = request.form.get('التسلسل', '').strip()
        المحافظة = request.form.get('المحافظة', '').strip()
        المشروع = request.form.get('المشروع', '').strip()
        الكلفة_الكلية = request.form.get('الكلفة_الكلية', '').strip()
        الإعلان = request.form.get('الإعلان', '').strip()
        ملاحظات = request.form.get('ملاحظات', '').strip()
        # تحديث المشروع في قاعدة البيانات
        c.execute('''UPDATE projects 
                     SET التسلسل=?, المحافظة=?, المشروع=?, الكلفة_الكلية=?, الإعلان=?, ملاحظات=? 
                     WHERE id=?''',
                  (التسلسل, المحافظة, المشروع, الكلفة_الكلية, الإعلان, ملاحظات, project_id))
        conn.commit()
        conn.close()

        flash('تم تحديث المشروع بنجاح!', 'success')
        return redirect(url_for('reports'))  # إعادة التوجيه إلى صفحة التقارير

    # جلب بيانات المشروع الحالي
    c.execute("SELECT * FROM projects WHERE id=?", (project_id,))
    project = c.fetchone()
    conn.close()

    if project is None:
        flash('المشروع غير موجود!', 'danger')
        return redirect(url_for('reports'))

    return render_template('edit_project.html', project=project)
if __name__ == '__main__':
    app.run(debug=True)
# 🔥 تشغيل التطبيق
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
