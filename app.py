import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from streamlit_option_menu import option_menu
import os

# إعدادات الصفحة
st.set_page_config(page_title="نظام حضور وانصراف Aura QR", page_icon="🏢", layout="wide")

# ----------------- تنسيق احترافي (CSS) -----------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif !important; }
    .stApp { direction: rtl; }
    h1 { color: #1E3A8A !important; text-align: center !important; font-weight: 700 !important; padding-bottom: 20px; }
    div.stButton > button:first-child { background-color: #2563EB; color: white; border-radius: 8px; border: none; font-weight: bold; font-size: 16px; transition: all 0.3s ease; width: 100%; padding: 10px; }
    div.stButton > button:hover { background-color: #1E3A8A; color: white; }
    
    /* تظبيط اتجاهات الخانات عشان الأرقام تتكتب مظبوط */
    input[type="text"], input[type="number"], .stDateInput {
        direction: ltr !important;
        text-align: center !important;
        font-weight: bold !important;
    }
    </style>
""", unsafe_allow_html=True)

# ----------------- تجهيز قاعدة البيانات -----------------
def init_db():
    if not os.path.exists('data'):
        os.makedirs('data')
    conn = sqlite3.connect('data/attendance.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS employees (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS attendance (id INTEGER PRIMARY KEY AUTOINCREMENT, employee_name TEXT, date TEXT, check_in TEXT, check_out TEXT, FOREIGN KEY (employee_name) REFERENCES employees (name))''')
    conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect('data/attendance.db')

init_db()

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

# ----------------- محتوى الأقسام -----------------
if selected == "تسجيل اليومية":
    st.subheader("📝 تسجيل حركات اليوم")
    conn = get_connection()
    employees_df = pd.read_sql_query("SELECT name FROM employees", conn)
    conn.close()

    if not employees_df.empty:
        emp_list = employees_df['name'].tolist()
        
        col_emp, _ = st.columns([1, 1])
        with col_emp:
            selected_emp = st.selectbox("اختار اسم الموظف من القائمة:", emp_list)

        st.markdown("##### ⏱️ تحديد وقت وتاريخ التسجيل:")
        
        # تقسيم السطر لـ 3 خانات: التاريخ، الساعة، الدقيقة
        col_date, col_hour, col_minute = st.columns([2, 1, 1])
        
        now = datetime.now()
        
        with col_date:
            manual_date = st.date_input("التاريخ:", now)
        with col_hour:
            # خانة مخصصة للساعة (بنظام 24 ساعة)
            hour = st.number_input("الساعة (0-23):", min_value=0, max_value=23, value=now.hour, step=1)
        with col_minute:
            # خانة مخصصة للدقيقة
            minute = st.number_input("الدقيقة (0-59):", min_value=0, max_value=59, value=now.minute, step=1)

        final_date = manual_date.strftime("%Y-%m-%d")
        # تجميع الساعة والدقيقة في شكل نصي لقاعدة البيانات
        final_time = f"{hour:02d}:{minute:02d}:00"

        st.write("") 
        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            if st.button("✅ تسجيل حضور"):
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM attendance WHERE employee_name=? AND date=?", (selected_emp, final_date))
                if cursor.fetchone():
                    st.warning(f"⚠️ الموظف **{selected_emp}** مسجل حضور بالفعل يوم {final_date}.")
                else:
                    cursor.execute("INSERT INTO attendance (employee_name, date, check_in) VALUES (?, ?, ?)", (selected_emp, final_date, final_time))
                    conn.commit()
                    st.success(f"🎉 تم تسجيل حضور **{selected_emp}** بنجاح الساعة {final_time}")
                conn.close()

        with col2:
            if st.button("❌ تسجيل انصراف"):
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM attendance WHERE employee_name=? AND date=?", (selected_emp, final_date))
                record = cursor.fetchone()
                if record:
                    if record[4]: 
                        st.info(f"ℹ️ الموظف مسجل انصراف بالفعل يوم {final_date}.")
                    else:
                        cursor.execute("UPDATE attendance SET check_out=? WHERE employee_name=? AND date=?", (final_time, selected_emp, final_date))
                        conn.commit()
                        st.success(f"👋 تم تسجيل انصراف **{selected_emp}** بنجاح الساعة {final_time}")
                else:
                    st.error("❗ لا يمكن تسجيل الانصراف، يجب تسجيل الحضور أولاً لهذا اليوم.")
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
    conn = get_connection()
    emp_df = pd.read_sql_query("SELECT name FROM employees", conn)
    emp_list = emp_df['name'].tolist() if not emp_df.empty else []
    conn.close()
    
    filter_option = st.radio("طريقة عرض التقرير:", ["عرض كل السجلات", "عرض يوم محدد", "تقرير موظف محدد", "ملخص تأخيرات الشهر"], horizontal=True)
    
    col_filter, _ = st.columns([1, 2])
    if filter_option == "ملخص تأخيرات الشهر":
        conn = get_connection()
        years_df = pd.read_sql_query("SELECT DISTINCT SUBSTR(date, 1, 4) AS year FROM attendance WHERE date IS NOT NULL ORDER BY year DESC", conn)
        now_dt = datetime.now()
        month_options = list(range(1, 13))
        default_month_index = now_dt.month - 1
        year_options = years_df['year'].dropna().astype(int).tolist() if not years_df.empty else []
        year_options = sorted(set(year_options), reverse=True)
        if not year_options:
            year_options = [now_dt.year]
        if now_dt.year in year_options:
            default_year_index = year_options.index(now_dt.year)
        else:
            year_options.insert(0, now_dt.year)
            default_year_index = 0

        with col_filter:
            selected_month = st.selectbox("اختر الشهر:", month_options, index=default_month_index)
            selected_year = st.selectbox("اختر السنة:", year_options, index=default_year_index)

        summary_df = pd.read_sql_query(
            """
            SELECT employee_name, check_in
            FROM attendance
            WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ?
            """,
            conn,
            params=(str(selected_year), f"{selected_month:02d}")
        )
        conn.close()

        if summary_df.empty:
            st.info("📭 لا توجد سجلات لهذا الشهر.")
        else:
            summary_df['check_in_dt'] = pd.to_datetime(summary_df['check_in'], format='%H:%M:%S', errors='coerce')
            start_time = pd.to_datetime('09:00:00', format='%H:%M:%S')

            def calc_delay_minutes(check_in_time):
                if pd.isna(check_in_time):
                    return 0
                delay_minutes = int((check_in_time - start_time).total_seconds() // 60)
                return delay_minutes if delay_minutes > 0 else 0

            summary_df['delay_minutes'] = summary_df['check_in_dt'].apply(calc_delay_minutes)
            aggregated = summary_df.groupby('employee_name', as_index=False)['delay_minutes'].sum()
            aggregated.rename(columns={'employee_name': 'اسم الموظف', 'delay_minutes': 'إجمالي التأخير بالدقائق'}, inplace=True)
            ALLOWANCE_MINUTES = 40
            aggregated['المسموح (40 دقيقة)'] = ALLOWANCE_MINUTES

            def balance_status(total_delay):
                if total_delay > ALLOWANCE_MINUTES:
                    diff = total_delay - ALLOWANCE_MINUTES
                    return f"🔴 تجاوز المسموح بـ {diff} دقيقة"
                remaining = ALLOWANCE_MINUTES - total_delay
                return f"🟢 متبقي {remaining} دقيقة"

            aggregated['حالة الرصيد'] = aggregated['إجمالي التأخير بالدقائق'].apply(balance_status)
            st.dataframe(aggregated, use_container_width=True, hide_index=True)
    else:
        query = ""
        selected_emp_report = ""
        date_str = ""

        with col_filter:
            if filter_option == "عرض يوم محدد":
                selected_date = st.date_input("اختر التاريخ للبحث:", datetime.now())
                date_str = selected_date.strftime("%Y-%m-%d")
                query = f"SELECT employee_name as 'اسم الموظف', date as 'التاريخ', check_in as 'وقت الحضور', check_out as 'وقت الانصراف' FROM attendance WHERE date = '{date_str}' ORDER BY check_in DESC"
            elif filter_option == "تقرير موظف محدد":
                if emp_list:
                    selected_emp_report = st.selectbox("اختر الموظف:", emp_list)
                    query = f"SELECT employee_name as 'اسم الموظف', date as 'التاريخ', check_in as 'وقت الحضور', check_out as 'وقت الانصراف' FROM attendance WHERE employee_name = '{selected_emp_report}' ORDER BY date DESC"
                else:
                    st.warning("لا يوجد موظفين مسجلين.")
                    query = "SELECT employee_name as 'اسم الموظف', date as 'التاريخ', check_in as 'وقت الحضور', check_out as 'وقت الانصراف' FROM attendance WHERE 1=0"
            else:
                query = "SELECT employee_name as 'اسم الموظف', date as 'التاريخ', check_in as 'وقت الحضور', check_out as 'وقت الانصراف' FROM attendance ORDER BY date DESC, check_in DESC"

        conn = get_connection()
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if not df.empty:
            df['check_in_dt'] = pd.to_datetime(df['وقت الحضور'], format='%H:%M:%S', errors='coerce')
            start_time = pd.to_datetime('09:00:00', format='%H:%M:%S')

            def calculate_delay(check_in_time):
                if pd.isna(check_in_time): return "-"
                if check_in_time > start_time:
                    delay = check_in_time - start_time
                    hours, remainder = divmod(int(delay.total_seconds()), 3600)
                    minutes, _ = divmod(remainder, 60)
                    if hours > 0: return f"🔴 متأخر {hours} س و {minutes} د"
                    else: return f"🟠 متأخر {minutes} دقيقة"
                return "🟢 في الميعاد"

            df['حالة الحضور (ميعاد 9 ص)'] = df['check_in_dt'].apply(calculate_delay)
            df = df.drop(columns=['check_in_dt'])
            df.fillna('لم ينصرف بعد', inplace=True)
            st.dataframe(df, use_container_width=True, hide_index=True)

            if filter_option == "تقرير موظف محدد":
                late_days = df['حالة الحضور (ميعاد 9 ص)'].str.contains('متأخر').sum()
                if late_days > 0: st.error(f"📌 تنبيه: الموظف **{selected_emp_report}** مسجل له {late_days} يوم تأخير.")
                else: st.success(f"📌 ممتاز: الموظف **{selected_emp_report}** لم يتأخر أي يوم.")
        else:
            st.write("📭 لا توجد بيانات مطابقة للبحث.")

    with st.expander("🗑️ حذف سجل حضور", expanded=False):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, employee_name, date, check_in FROM attendance ORDER BY date DESC, check_in DESC")
        records = cursor.fetchall()
        conn.close()

        if records:
            display_map = {}
            for rec_id, emp_name, rec_date, rec_check_in in records:
                check_in_display = rec_check_in if rec_check_in else "-"
                label = f"{emp_name} | {rec_date} | {check_in_display}"
                display_map[label] = rec_id

            selected_label = st.selectbox("اختر السجل المراد حذفه:", list(display_map.keys()))
            if st.button("🗑️ حذف السجل", key="delete_record_btn"):
                selected_id = display_map[selected_label]
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM attendance WHERE id = ?", (selected_id,))
                conn.commit()
                conn.close()
                st.success("✅ تم حذف السجل بنجاح.")
                st.rerun()
        else:
            st.info("لا توجد سجلات متاحة للحذف.")