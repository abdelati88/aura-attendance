import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from streamlit_option_menu import option_menu

# إعدادات الصفحة
st.set_page_config(page_title="نظام حضور وانصراف Aura QR", page_icon="🏢", layout="wide")

# ----------------- تنسيق احترافي (CSS) -----------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif !important;
    }
    
    .stApp {
        direction: rtl;
    }
    
    h1 {
        color: #1E3A8A !important;
        text-align: center !important;
        font-weight: 700 !important;
        padding-bottom: 20px;
    }
    
    div.stButton > button:first-child {
        background-color: #2563EB;
        color: white;
        border-radius: 8px;
        border: none;
        font-weight: bold;
        font-size: 16px;
        transition: all 0.3s ease;
        width: 100%;
        padding: 10px;
    }
    div.stButton > button:hover {
        background-color: #1E3A8A;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# ----------------- دوال قاعدة البيانات -----------------
def get_connection():
    return sqlite3.connect('attendance.db')

# ----------------- رأس الصفحة -----------------
st.markdown("<h1>🏢 نظام إدارة الحضور والانصراف - Aura QR</h1>", unsafe_allow_html=True)
st.markdown("---")

# ----------------- شريط التنقل الاحترافي (Menu) -----------------
selected = option_menu(
    menu_title=None, 
    options=["تسجيل اليومية", "إدارة الفريق", "تقارير المتابعة"], 
    icons=["calendar-check", "people-fill", "bar-chart-fill"], 
    menu_icon="cast", 
    default_index=0, 
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#f8f9fa", "direction": "rtl"},
        "icon": {"color": "#2563EB", "font-size": "20px"}, 
        "nav-link": {"font-size": "18px", "text-align": "center", "margin":"0px", "--hover-color": "#e2e8f0", "font-family": "Cairo"},
        "nav-link-selected": {"background-color": "#1E3A8A", "color": "white"},
    }
)

st.markdown("<br>", unsafe_allow_html=True)

# ----------------- محتوى الأقسام بناءً على الاختيار -----------------

if selected == "تسجيل اليومية":
    st.subheader("📝 تسجيل حركات اليوم")
    
    conn = get_connection()
    employees_df = pd.read_sql_query("SELECT name FROM employees", conn)
    conn.close()

    if not employees_df.empty:
        emp_list = employees_df['name'].tolist()
        
        col_main, col_space = st.columns([1, 1])
        with col_main:
            selected_emp = st.selectbox("اختار اسم الموظف من القائمة:", emp_list)

        today_date = datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%H:%M:%S")

        st.write("") 
        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            if st.button("✅ تسجيل حضور الآن"):
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM attendance WHERE employee_name=? AND date=?", (selected_emp, today_date))
                if cursor.fetchone():
                    st.warning(f"⚠️ الموظف **{selected_emp}** مسجل حضور بالفعل اليوم.")
                else:
                    cursor.execute("INSERT INTO attendance (employee_name, date, check_in) VALUES (?, ?, ?)", (selected_emp, today_date, current_time))
                    conn.commit()
                    st.success(f"🎉 تم تسجيل حضور **{selected_emp}** بنجاح الساعة {current_time}")
                conn.close()

        with col2:
            if st.button("❌ تسجيل انصراف الآن"):
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM attendance WHERE employee_name=? AND date=?", (selected_emp, today_date))
                record = cursor.fetchone()
                
                if record:
                    if record[4]: 
                        st.info("ℹ️ الموظف مسجل انصراف بالفعل اليوم.")
                    else:
                        cursor.execute("UPDATE attendance SET check_out=? WHERE employee_name=? AND date=?", (current_time, selected_emp, today_date))
                        conn.commit()
                        st.success(f"👋 تم تسجيل انصراف **{selected_emp}** بنجاح الساعة {current_time}")
                else:
                    st.error("❗ لا يمكن تسجيل الانصراف، يجب تسجيل الحضور أولاً.")
                conn.close()
    else:
        st.info("💡 النظام فارغ حالياً. قم بإضافة أعضاء الفريق من تبويب 'إدارة الفريق' للبدء.")

elif selected == "إدارة الفريق":
    st.subheader("👥 إضافة عضو جديد للفريق")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        new_emp = st.text_input("أدخل اسم الموظف ثلاثي:")
        if st.button("➕ إضافة للفريق"):
            if new_emp:
                conn = get_connection()
                cursor = conn.cursor()
                try:
                    cursor.execute("INSERT INTO employees (name) VALUES (?)", (new_emp,))
                    conn.commit()
                    st.success(f"✅ تم إضافة **{new_emp}** لقاعدة البيانات بنجاح!")
                except sqlite3.IntegrityError:
                    st.error("⚠️ هذا الاسم مسجل مسبقاً في النظام.")
                conn.close()
            else:
                st.warning("الرجاء كتابة الاسم أولاً.")

elif selected == "تقارير المتابعة":
    st.subheader("📊 سجل الحركات والتأخيرات")
    
    # قائمة بأسماء الموظفين للفلترة
    conn = get_connection()
    emp_df = pd.read_sql_query("SELECT name FROM employees", conn)
    emp_list = emp_df['name'].tolist() if not emp_df.empty else []
    
    # خيارات الفلترة
    filter_option = st.radio("طريقة عرض التقرير:", ["عرض كل السجلات", "عرض يوم محدد", "تقرير موظف محدد"], horizontal=True)
    
    query = ""
    selected_emp_report = ""
    date_str = ""

    col_filter, _ = st.columns([1, 2])
    with col_filter:
        if filter_option == "عرض يوم محدد":
            selected_date = st.date_input("اختر التاريخ:", datetime.now())
            date_str = selected_date.strftime("%Y-%m-%d")
            query = f"SELECT employee_name as 'اسم الموظف', date as 'التاريخ', check_in as 'وقت الحضور', check_out as 'وقت الانصراف' FROM attendance WHERE date = '{date_str}' ORDER BY check_in DESC"
        
        elif filter_option == "تقرير موظف محدد":
            if emp_list:
                selected_emp_report = st.selectbox("اختر الموظف:", emp_list)
                query = f"SELECT employee_name as 'اسم الموظف', date as 'التاريخ', check_in as 'وقت الحضور', check_out as 'وقت الانصراف' FROM attendance WHERE employee_name = '{selected_emp_report}' ORDER BY date DESC"
            else:
                st.warning("لا يوجد موظفين مسجلين.")
                query = "SELECT employee_name as 'اسم الموظف', date as 'التاريخ', check_in as 'وقت الحضور', check_out as 'وقت الانصراف' FROM attendance WHERE 1=0"
        
        else: # عرض كل السجلات
            query = "SELECT employee_name as 'اسم الموظف', date as 'التاريخ', check_in as 'وقت الحضور', check_out as 'وقت الانصراف' FROM attendance ORDER BY date DESC, check_in DESC"

    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if not df.empty:
        # ----------------- حساب التأخير -----------------
        df['check_in_dt'] = pd.to_datetime(df['وقت الحضور'], format='%H:%M:%S', errors='coerce')
        start_time = pd.to_datetime('09:00:00', format='%H:%M:%S')

        def calculate_delay(check_in_time):
            if pd.isna(check_in_time):
                return "-"
            if check_in_time > start_time:
                delay = check_in_time - start_time
                total_seconds = int(delay.total_seconds())
                hours, remainder = divmod(total_seconds, 3600)
                minutes, _ = divmod(remainder, 60)
                
                if hours > 0:
                    return f"🔴 متأخر {hours} س و {minutes} د"
                else:
                    return f"🟠 متأخر {minutes} دقيقة"
            return "🟢 في الميعاد"

        df['حالة الحضور (ميعاد 9 ص)'] = df['check_in_dt'].apply(calculate_delay)
        df = df.drop(columns=['check_in_dt'])
        # ------------------------------------------------
        
        df.fillna('لم ينصرف بعد', inplace=True)
        st.dataframe(df, use_container_width=True, hide_index=True)

        # ملخص للموظف
        if filter_option == "تقرير موظف محدد":
            late_days = df['حالة الحضور (ميعاد 9 ص)'].str.contains('متأخر').sum()
            if late_days > 0:
                st.error(f"📌 تنبيه: الموظف **{selected_emp_report}** مسجل له {late_days} يوم تأخير.")
            else:
                st.success(f"📌 ممتاز: الموظف **{selected_emp_report}** لم يتأخر أي يوم.")

    else:
        st.write("📭 لا توجد بيانات مطابقة للبحث.")