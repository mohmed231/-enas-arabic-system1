import streamlit as st
import sqlite3
import pandas as pd
import urllib.parse
import webbrowser
from datetime import datetime
import os

# إعدادات الصفحة الافتراضية للموقع
st.set_page_config(page_title="سيستم الأستاذة إيناس معتمد", page_icon="📚", layout="wide")

# إعدادات الحماية والتواصل
SYSTEM_PASSWORD = "123"
ENG_PHONE = "01096196849"

# تأسيس قاعدة البيانات المحلية للموقع
def init_db():
    conn = sqlite3.connect('ar_teacher_website.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            barcode TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            parent_phone TEXT NOT NULL,
            group_name TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_barcode TEXT,
            date TEXT,
            time TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_barcode TEXT,
            amount REAL,
            pay_type TEXT,
            date TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- الهيدر الرئيسي للموقع ---
    <div style="background-color:#1e3799;padding:15px;border-radius:10px;text-align:center;color:white;direction:rtl;">
        <h2>✨ نظام إدارة السنتر والمراقبة الأمنية المتكاملة - الأستاذة إيناس معتمد ✨</h2>
        <h4>👨‍💻 تصميم وتطوير البشمهندس: محمد أحمد محمد علي | للتواصل والدعم الفني: {ENG_PHONE}</h4>
    </div>
""", unsafe_allow_color=True, unsafe_allow_html=True)

# --- نظام قفل الموقع بكلمة سر ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.subheader("🔐 برجاء تسجيل الدخول لحماية بيانات السنتر:")
    password_input = st.text_input("أدخل كلمة المرور:", type="password")
    if st.button("تأكيد الهوية ودخول الموقع"):
        if password_input == SYSTEM_PASSWORD:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("❌ كلمة السر غير صحيحة! لا يمكن فتح الموقع.")
    st.stop()

# --- تبويبات الموقع الرئيسي ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🛡️ بوابات الحضور الذكية والإنذار", 
    "👤 تسجيل الطلاب وتوليد الباركود", 
    "💰 إدارة الخزنة والإيصالات الحية", 
    "📊 التقارير المالية والإحصائيات الإجمالية", 
    "📋 كشف حسابات الطلاب والتحكم الأمني"
])

# --- 1. بوابات الحضور والإنذار المالي ---
with tab1:
    st.header("🎯 رصد حضور الطلاب بالباركود")
    
    # حيلة برمجية لجعل التركيز على خانة الباركود دائماً
    barcode = st.text_input("اضغط هنا ثم امسح كارت الباركود بالليزر:", key="attendance_barcode", value="")
    
    if barcode:
        conn = sqlite3.connect('ar_teacher_website.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT name, parent_phone, group_name FROM students WHERE barcode = ?", (barcode,))
        student = cursor.fetchone()
        
        if student:
            name, parent_phone, group_name = student
            
            # فحص الدفع المالي
            cursor.execute("SELECT COUNT(*) FROM payments WHERE student_barcode = ? AND pay_type = 'اشتراك شهري'", (barcode,))
            has_paid = cursor.fetchone()[0]
            
            now = datetime.now()
            cursor.execute("INSERT INTO attendance (student_barcode, date, time) VALUES (?, ?, ?)", 
                           (barcode, now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")))
            conn.commit()
            
            if has_paid > 0:
                st.success(f"✅ حضور معتمد: {name} | {group_name} | (الحالة المالية: سدد الاشتراك بالكامل 👍)")
            else:
                st.warning(f"⚠️ حضور مؤقت: {name} | {group_name} | 🛑 إنذار مالي: لم يسدد الاشتراك الشهري الحالي! 🛑")
            
            # إنشاء رابط الواتساب التلقائي لولي الأمر
            message = f"تحية طيبة من مكتب الأستاذة إيناس معتمد (مدرسة اللغة العربية).\nنحيطكم علماً بأن الطالب(ة): {name} قد حضر الحصة اليوم في موعده تماماً وصعد إلى القاعة التعليمية.\n[السيستم الذكي من تصميم م. محمد أحمد - ت: {ENG_PHONE}]"
            encoded_message = urllib.parse.quote(message)
            whatsapp_url = f"https://whatsapp.com{parent_phone}&text={encoded_message}"
            
            st.markdown(f'<a href="{whatsapp_url}" target="_blank" style="background-color:#25D366;color:white;padding:10px 20px;text-decoration:none;border-radius:5px;font-weight:bold;">📱 اضغط هنا لإرسال رسالة الواتساب الفورية لولي الأمر</a>', unsafe_allow_html=True)
        else:
            st.error(f"❌ خرق أمني: كارت باركود غير معروف أو مفقود البيانات ({barcode})!")
        conn.close()

# --- 2. تسجيل الطلاب الجدد ---
with tab2:
    st.header("👤 إضافة طالب جديد في المجموعات")
    with st.form("add_student_form", clear_on_submit=True):
        new_barcode = st.text_input("كود الباركود للطالب:")
        new_name = st.text_input("اسم الطالب رباعي بالكامل:")
        new_phone = st.text_input("رقم هاتف ولي الأمر (مثال يبدأ بمفتاح الدولة: 201096196849):")
        new_group = st.text_input("المجموعة والميعاد التعليمي المحدد:")
        submit_btn = st.form_submit_button("💾 حفظ وتأكيد بيانات الطالب وتفعيل الكارت")
        
        if submit_btn:
            if new_barcode and new_name and new_phone:
                conn = sqlite3.connect('ar_teacher_website.db')
                cursor = conn.cursor()
                try:
                    cursor.execute("INSERT INTO students VALUES (?, ?, ?, ?)", (new_barcode, new_name, new_phone, new_group))
                    conn.commit()
                    st.success(f"🎉 تم تسجيل الطالب {new_name} بنجاح وتأمين كارت الباركود!")
                except sqlite3.IntegrityError:
                    st.error("🛑 خطأ تكرار أمني: هذا الباركود مسجل لطالب آخر بالفعل!")
                conn.close()
            else:
                st.error("⚠️ برجاء كتابة البيانات الأساسية أولاً!")

# --- 3. إدارة الخزنة والإيصالات ---
with tab3:
    st.header("💰 إدارة المدفوعات والخزنة")
    pay_barcode = st.text_input("امسح باركود الطالب لتسجيل الدفع:", key="pay_barcode")
    pay_amount = st.number_input("المبلغ المالي المستلم (جنيه مصري):", min_value=0.0, step=50.0)
    pay_type = st.selectbox("نوع وبند الدفع المعين:", ["اشتراك شهري", "حساب بالحصة", "ثمن مذكرة / كتاب"])
    
    if st.button("💵 تأكيد الإيداع في الخزنة وتوليد الإيصال المالي"):
        if pay_barcode and pay_amount > 0:
            conn = sqlite3.connect('ar_teacher_website.db')
            cursor = conn.cursor()
            cursor.execute("SELECT name, group_name FROM students WHERE barcode = ?", (pay_barcode,))
            student = cursor.fetchone()
            
            if student:
                name, group = student
                now_date = datetime.now().strftime("%Y-%m-%d")
                cursor.execute("INSERT INTO payments (student_barcode, amount, pay_type, date) VALUES (?, ?, ?, ?)", 
                               (pay_barcode, pay_amount, pay_type, now_date))
                conn.commit()
                
                st.success("📝 تم قيد الفلوس بالخزنة بنجاح!")
                st.code(f"""
=========================================
         إيصال استلام نقدية معتمد        
=========================================
المكتب التعليمي للأستاذة: إيناس معتمد
اسم الطالب الثلاثي: {name}
المجموعة الدراسية: {group}
المبلغ المسدد نقداً: {pay_amount} جنيهاً مصرياً لا غير
نوع وبند المعاملة المودعة: {pay_type}
تاريخ ونظام التوثيق: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
تطوير البرمجيات: م. محمد أحمد محمد علي
=========================================
                """)
            else:
                st.error("❌ كود الطالب غير صحيح أو لا يوجد سجل بهذا الباركود!")
            conn.close()
        else:
            st.error("⚠️ برجاء ملء خانة الباركود والقيمة المالية المستلمة!")

# --- 4. التقارير والإحصائيات المالية ---
with tab4:
    st.header("📊 التقارير والإحصائيات الإجمالية")
    conn = sqlite3.connect('ar_teacher_website.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]
    
    cursor.execute("SELECT SUM(amount) FROM payments")
    res = cursor.fetchone()[0]
    total_money = res if res is not None else 0.0
    
    cursor.execute("SELECT COUNT(*) FROM attendance")
    total_attendance = cursor.fetchone()[0]
    conn.close()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("📊 عدد الطلاب المسجلين", f"{total_students} طالب")
    col2.metric("💰 دخل الخزنة الفعلي", f"{total_money:.2f} جنيه")
    col3.metric("📝 عدد عمليات تسجيل الحضور", f"{total_attendance} عملية")

# --- 5. كشف حسابات الطلاب والتحكم والـ Excel ---
with tab5:
    st.header("📋 لوحة المراقبة الإدارية واستخراج التقارير")
    conn = sqlite3.connect('ar_teacher_website.db')
    df_students = pd.read_sql_query("SELECT barcode AS [الباركود], name AS [اسم الطالب], parent_phone AS [رقم ولي الأمر], group_name AS [المجموعة] FROM students", conn)
    conn.close()
    
    st.subheader("👥 كشف الطلاب المسجلين حالياً:")
    st.dataframe(df_students, use_container_width=True)
    
    # زر استخراج لـ Excel مباشرة من المتصفح
    st.subheader("📥 تحميل الكشوفات")
    if not df_students.empty:
        # تحويل البيانات بصيغة مخصصة للتحميل من الموقع
        @st.cache_data
        def convert_df(df):
            return df.to_csv(index=False).encode('utf-8-sig')
        
        csv = convert_df(df_students)
        st.download_button(
            label="📥 اضغط هنا لتحميل كشف الطلاب بصيغة Excel (CSV)",
            data=csv,
            file_name='كشف_طلاب_الأستاذة_إيناس.csv',
            mime='text/csv',
        )
