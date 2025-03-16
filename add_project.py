{% extends "layout.html" %}

{% block content %}
<h2 class="text-center my-4 text-primary">إضافة مشروع جديد</h2>

<div class="container">
    <form action="{{ url_for('add_project') }}" method="POST" class="row g-3 p-4 bg-light shadow rounded">

        {% set fields = [
            ('التسلسل', 'number'),
            ('المشروع', 'text'),
            ('الإعلان', 'date'),
            ('تاريخ_غلق_الدعوات', 'date'),
            ('لجنة_تحليل', 'text'),
            ('قرار_لجنة_التحليل_الى_دائرة_العقود', 'date'),
            ('لجنة_المراجعة_والمصادقة', 'text'),
            ('الإحالة', 'text'),
            ('مسودة_العقد', 'text'),
            ('توقيع_العقد', 'date')
        ] %}

        <!-- اختيار المحافظة -->
        <div class="col-md-6">
            <label class="form-label fw-bold">المحافظة:</label>
            <select name="المحافظة" class="form-select border-primary" required>
                <option value="" disabled selected>اختر المحافظة</option>
                {% set المحافظات = ['بغداد', 'البصرة', 'نينوى', 'الأنبار', 'كركوك', 'أربيل',
                                    'السليمانية', 'دهوك', 'كربلاء', 'النجف', 'واسط', 'ذي قار',
                                    'ميسان', 'المثنى', 'القادسية', 'بابل', 'ديالى', 'صلاح الدين'] %}
                {% for محافظة in المحافظات %}
                <option value="{{ محافظة }}">{{ محافظة }}</option>
                {% endfor %}
            </select>
        </div>

        <!-- الحقول الأخرى -->
        {% for label, type in fields %}
        <div class="col-md-6">
            <label class="form-label fw-bold">{{ label.replace('_', ' ') }}:</label>
            <input type="{{ type }}" name="{{ label }}" class="form-control border-primary" required>
        </div>
        {% endfor %}

        <!-- إصلاح حقل الكلفة الكلية -->
        <div class="col-md-6">
            <label class="form-label fw-bold">الكلفة الكلية (دينار عراقي):</label>
            <input type="number" name="الكلفة_الكلية" class="form-control border-primary" required>
        </div>

        <!-- مدرج في وزارة التخطيط -->
        <div class="col-md-6">
            <label class="form-label fw-bold">مدرج في وزارة التخطيط:</label>
            <select name="مدرج_في_وزارة_التخطيط" class="form-select border-info" required>
                <option value="مدرج">مدرج</option>
                <option value="قيد الإدراج">قيد الإدراج</option>
            </select>
        </div>

        <!-- مؤشر لدى وزارة المالية -->
        <div class="col-md-6">
            <label class="form-label fw-bold">مؤشر لدى وزارة المالية:</label>
            <select name="مؤشر_لدى_وزارة_المالية" class="form-select border-success" required>
                <option value="مؤشر">مؤشر</option>
                <option value="غير مؤشر">غير مؤشر</option>
            </select>
        </div>

        <!-- الاستثناء من أساليب التعاقد -->
        <div class="col-md-6">
            <label class="form-label fw-bold">الاستثناء من أساليب التعاقد:</label>
            <select name="الاستثناء_من_أساليب_التعاقد" class="form-select border-warning" required>
                <option value="دعوة">دعوة</option>
                <option value="إعلان">إعلان</option>
            </select>
        </div>

        <!-- استثناء تصميم وتنفيذ / جداول كميات -->
        <div class="col-md-6">
            <label class="form-label fw-bold">استثناء (تصميم وتنفيذ / جداول كميات):</label>
            <select name="استثناء" class="form-select border-danger" required>
                <option value="تصميم وتنفيذ">تصميم وتنفيذ</option>
                <option value="جداول كميات">جداول كميات</option>
            </select>
        </div>

        <!-- مربعات الاختيار (Checkboxes) -->
        {% set checkboxes = ['دراسة_سيرة_ذاتية', 'الدعوات', 'الوثيقة_القياسية', 'التخويل', 'لجان_الفتح'] %}
        {% for box in checkboxes %}
        <div class="col-md-6">
            <div class="form-check">
                <input class="form-check-input" type="checkbox" name="{{ box }}" value="صح" id="{{ box }}">
                <label class="form-check-label fw-bold" for="{{ box }}">{{ box.replace('_', ' ') }}</label>
            </div>
        </div>
        {% endfor %}

        <!-- ملاحظات -->
        <div class="col-md-12">
            <label class="form-label fw-bold">ملاحظات:</label>
            <textarea name="ملاحظات" class="form-control border-secondary" rows="3"></textarea>
        </div>

        <!-- زر الإرسال -->
        <div class="col-12 text-center">
            <button type="submit" class="btn btn-primary btn-lg">إضافة المشروع</button>
        </div>
    </form>
</div>

{% endblock %}
