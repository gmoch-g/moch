from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect("database.db")  # استبدل "database.db" بقاعدة بياناتك
    conn.row_factory = sqlite3.Row  # يسمح بالوصول إلى البيانات كقاموس
    return conn

@app.route('/get_columns')
def get_columns():
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("PRAGMA table_info(projects)")  # استبدل "projects" باسم الجدول الخاص بك
        columns = [col[1] for col in c.fetchall()]
        conn.close()
        return jsonify(columns)
    except sqlite3.Error as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
