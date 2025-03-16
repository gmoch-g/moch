from flask_sqlalchemy import SQLAlchemy

# إنشاء كائن db من SQLAlchemy
db = SQLAlchemy()

# نموذج بيانات المشروع
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    semester = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    project_type = db.Column(db.String(100), nullable=False)
    sequence = db.Column(db.String(100), nullable=False)
    project_name = db.Column(db.String(200), nullable=False)
    total_cost = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<Project {self.project_name}>"
