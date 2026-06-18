import streamlit as st
import sqlite3
import pandas as pd
import urllib.parse
from datetime import datetime
import os

# 1. إعدادات الصفحة الافتراضية للموقع
st.set_page_config(page_title="سيستم الأستاذة إيناس معتمد", page_icon="📚", layout="wide")

# إعدادات الحماية والتواصل الخاصة بالبشمهندس محمد أحمد
SYSTEM_PASSWORD = "123"
ENG_PHONE = "01096196849"

# 2. تأسيس قاعدة البيانات المحلية للموقع وتحديث الجداول
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

# --- 3. الهيدر الرئيسي الملكي للموقع بتصميم البشمهندس محمد أحمد ---
st.markdown(f"""
    <div style="background-color:#1e3799; padding:20px; border-radius:12px; text-align:center; color:white; direction:rtl; margin-bottom:25px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <h2 style="margin:0; font-family:Arial; font-weight:bold;">✨ نظام إدارة السنتر والمراقبة الأمنية المتكاملة - الأستاذة إيناس معتمد ✨</h2>
        <h4 style="margin:10px 0 0 0; font-family:Arial; color:#f5f6fa; font-weight:normal;">👨‍💻 تصميم وتطوير البشمهندس: محمد أحمد محمد علي | للتواصل والدعم الفني: {ENG_PHONE}</h4>
    </div>
""", unsafe_allow_html=True)

# --- 4. نظام حماية وجدار الحماية للموقع بكلمة سر ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.markdown("<div style='direction:rtl; text-align:right;'>", unsafe_allow_html=True)
    st.subheader("🔐 نظام الأمان: برجاء تسجيل الدخول لفتح لوحة تحكم السنتر:")
    password_input = st.text_input("أدخل كلمة المرور الفعالة للسيستم:", type="password")
    
    if st.button("تأكيد صلاحية الدخول للموقع"):
        if password_input == SYSTEM_PASSWORD:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("❌ خرق أمني: كلمة السر غير صحيحة! لا يمكن فتح الموقع.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- 5. تبويبات وتفرعات الموقع لسهولة التنقل الفوري ---
st.markdown("<div style='direction:rtl; text-align:right;'>", unsafe_allow_html=True)
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🛡️ بوابات الحضور الذكية والإنذار", 
    "👤 تسجيل الطلاب وتوليد الباركود", 
    "💰 إدارة الخزنة والإيصالات الحية", 
    "📊 التقارير المالية والإحصائيات الإجمالية", 
    "📋 كشف حسابات الطلاب والتحكم الأمني"
])
st.markdown("</div>", unsafe_allow_html=True)

# --- [تبويب 1]: بوابات الحضور والإنذار المالي الفوري ---
with tab1:
    st.markdown("<div style='direction:rtl; text-align:right;'>", unsafe_allow_html=True)
    st.header("🎯 رصد حضور الطلاب الفوري بالباركود")
    
    barcode = st.text_input("اضغط داخل الخانة أولاً، ثم امسح كارت الباركود بالليزر:", key="attendance_barcode", value="")
    
    if barcode:
        conn = sqlite3.connect('ar_teacher_website.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT name, parent_phone, group_name FROM students WHERE barcode = ?", (barcode,))
        student = cursor.fetchone()
        
        if student:
            name, parent_phone, group_name = student
            
            # فحص الحالة المالية المباشرة للطالب في الخزنة
            cursor.execute("SELECT COUNT(*) FROM payments WHERE student_barcode = ? AND pay_type = 'اشتراك شهري'", (barcode,))
            has_paid = cursor.fetchone()
            
            now = datetime.now()
            cursor.execute("INSERT INTO attendance (student_barcode, date, time) VALUES (?, ?, ?)", 
                           (barcode, now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")))
            conn.commit()
            
            if has_paid[0] > 0:
                st.success(f"✅ حضور معتمد وآمن: {name} | المجموعة: {group_name} | (الحالة المالية: سدد الاشتراك بالكامل 👍)")
            else:
                st.warning(f"⚠️ حضور مؤقت للمراجعة: {name} | المجموعة: {group_name} | 🛑 إنذار مالي: لم يسدد الاشتراك الشهري الحالي! 🛑")
            
            # تنظيف رقم الهاتف ليتوافق مع صيغة واتساب العالمية
            clean_phone = str(parent_phone).strip().replace(" ", "").replace("+", "")
            if not clean_phone.startswith("20"):
                if clean_phone.startswith("01"):
                    clean_phone = "2" + clean_phone
                else:
                    clean_phone = "20" + clean_phone
            
            # آلية توليد رابط الواتساب المحدث
            message = f"تحية طيبة من مكتب الأستاذة إيناس معتمد (مدرسة اللغة العربية).\nنحيطكم علماً بأن الطالب(ة): {name} قد حضر الحصة اليوم في موعده تماماً وصعد إلى القاعة التعليمية.\n[السيستم الذكي من تصميم م. محمد أحمد - ت: {ENG_PHONE}]"
            encoded_message = urllib.parse.quote(message)
            whatsapp_url = f"https://wa.me{clean_phone}?text={encoded_message}"
            
            st.markdown(f'<br><a href="{whatsapp_url}" target="_blank" style="background-color:#25D366; color:white; padding:15px 30px; text-decoration:none; border-radius:8px; font-weight:bold; font-size:16px; display:inline-block; box-shadow: 0 4px 6px rgba(0,0,0,0.15); border: 2px solid #fff;">📱 اضغط هنا لإرسال رسالة الواتساب الفورية لولي الأمر</a>', unsafe_allow_html=True)
        else:
            st.error(f"❌ خرق أمني: كارت باركود غير معروف أو مفقود البيانات من السجلات ({barcode})!")
        conn.close()
    st.markdown("</div>", unsafe_allow_html=True)

# --- [تبويب 2]: تسجيل الطلاب الجدد وتوليد الباركود ---
with tab2:
    st.markdown("<div style='direction:rtl; text-align:right;'>", unsafe_allow_html=True)
    st.header("👤 إضافة وتكويد طالب جديد في المجموعات")
    with st.form("add_student_form", clear_on_submit=True):
        new_barcode = st.text_input("كود الباركود للطالب (امسح الكارت بالليزر أو اكتبه):")
        new_name = st.text_input("اسم الطالب رباعي بالكامل:")
        new_phone = st.text_input("رقم هاتف ولي الأمر (اكتبه عادي مثل 01096196849 والسيستم هيعدله تلقائي):")
        new_group = st.text_input("المجموعة والميعاد التعليمي المحدد للطالب:")
        submit_btn = st.form_submit_button("💾 حفظ وتأكيد بيانات الطالب وتفعيل الكارت بالخلفية")
        
        if submit_btn:
            if new_barcode and new_name and new_phone:
                conn = sqlite3.connect('ar_teacher_website.db')
                cursor = conn.cursor()
                try:
                    cursor.execute("INSERT INTO students VALUES (?, ?, ?, ?)", (new_barcode, new_name, new_phone, new_group))
                    conn.commit()
                    st.success(f"🎉 تم تسجيل الطالب {new_name} بنجاح وتأمين كارت الباركود الخاص به للرصد الافتراضي!")
                except sqlite3.IntegrityError:
                    st.error("🛑 خطأ تكرار أمني: هذا الباركود مسجل ومربوط بطالب آخر مسبقاً!")
                conn.close()
            else:
                st.error("⚠️ برجاء كتابة البيانات الحيوية والأساسية أولاً!")
    st.markdown("</div>", unsafe_allow_html=True)

# --- [تبويب 3]: إدارة الخزنة والإيصالات الحية ---
with tab3:
    st.markdown("<div style='direction:rtl; text-align:right;'>", unsafe_allow_html=True)
    st.header("💰 إدارة المدفوعات والقيود المالية المودعة")
    pay_barcode = st.text_input("امسح باركود الطالب لتسديد الفلوس الحالية:", key="pay_barcode")
    pay_amount = st.number_input("المبلغ المالي المستلم نقداً (جنيه مصري):", min_value=0.0, step=50.0)
    pay_type = st.selectbox("نوع وبند الدفع المعين بالخزينة:", ["اشتراك شهري", "حساب بالحصة", "ثمن مذكرة / كتاب"])
    
    if st.button("💵 تأكيد الإيداع في الخزنة وتوليد الإيصال البنكي"):
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
                
                st.success("📝 تم قيد وتحصين الفلوس بالخزنة المركزية بنجاح!")
                st.code(f"""
=================================================
         إيصال استلام نقدية معتمد وتوثيق مالي       
=================================================
المكتب التعليمي للأستاذة: إيناس معتمد
اسم الطالب الثلاثي: {name}
المجموعة الدراسية المربوطة: {group}
المبلغ المسدد نقداً: {pay_amount} جنيهاً مصرياً لا غير
نوع وبند المعاملة المودعة: {pay_type}
تاريخ ونظام التوثيق: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
تطوير وهندسة البرمجيات: م. محمد أحمد محمد علي
=================================================
                """)
            else:
                st.error("❌ كود الطالب غير صحيح أو لا يوجد سجل بهذا الباركود!")
            conn.close()
        else:
            st.error("⚠️ برجاء ملء خانة الباركود والقيمة المالية المستلمة بالشكل الصحيح!")
    st.markdown("</div>", unsafe_allow_html=True)

# --- [تبويب 4]: التقارير والإحصائيات المالية الإجمالية ---
with tab4:
    st.markdown("<div style='direction:rtl; text-align:right;'>", unsafe_allow_html=True)
    st.header("📊 التقارير والإحصائيات الإجمالية المقيدة بالسنتر")
