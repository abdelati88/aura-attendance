import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from streamlit_option_menu import option_menu
import os

# ----------------- Page Configuration -----------------
st.set_page_config(page_title="نظام حضور وانصراف Aura QR", page_icon="🏢", layout="wide")

# ----------------- Professional Styling (CSS) -----------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');
    
    /* Apply Cairo font without forcing it on every single div/span to prevent breaking Streamlit's SVGs/Icons */
    html, body, .stApp { 
        direction: rtl; 
        background-color: #F8FAFC !important;
        font-family: 'Cairo', sans-serif !important;
    }
    
    p, label, li, table, input, button, select, .stMarkdown, .stText { 
        font-family: 'Cairo', sans-serif !important; 
    }
    
    /* Typography */
    h1, h2, h3, h4, h5, h6 { 
        font-family: 'Cairo', sans-serif !important;
        color: #1E3A8A !important; 
        font-weight: 800 !important; 
    }
    
    /* 🔴 Fix Icons and Arrows in Dropdowns and Expanders (Resolve RTL and keyboard_arrow_down issues) */
    .stSelectbox div[data-baseweb="select"] span[aria-hidden="true"], 
    .stSelectbox div[data-baseweb="select"] i,
    .stSelectbox div[data-baseweb="select"] svg,
    div[data-testid="stExpander"] details summary svg,
    div[data-testid="stExpander"] details summary i,
    span[class*="icon"], 
    span[class*="stIcon"],
    i, 
    svg,
    .material-icons,
    .material-symbols-rounded {
        font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important;
        direction: ltr !important;
    }
    
    hr {
        border-color: #EAB308 !important;
        opacity: 0.5;
    }
    
    /* 1. Cards styling for dataframes, metrics, and expanders */
    div[data-testid="stExpander"], div[data-testid="stDataFrame"], .metric-card {
        background-color: #FFFFFF !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
        border: none !important;
    }
    
    /* Top block adjustment */
    .block-container {
        padding-top: 2rem !important;
    }
    
    /* 2. Primary Buttons */
    div.stButton > button { 
        background-color: #1E3A8A !important;
        color: white !important; 
        border-radius: 12px !important; 
        border: none !important; 
        font-weight: 700 !important; 
        font-size: 16px !important; 
        transition: all 0.3s ease-in-out !important; 
        width: 100% !important; 
        padding: 12px 10px !important; 
    }
    div.stButton > button:hover { 
        background-color: #EAB308 !important;
        color: #1E3A8A !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* 3. Inputs & Selectboxes */
    .stTextInput input, .stNumberInput input, div[data-baseweb="select"] > div, .stDateInput input {
        border-radius: 10px !important;
        border: 1px solid #1E3A8A !important;
        transition: all 0.3s ease !important;
    }
    .stTextInput input:focus, .stNumberInput input:focus, .stDateInput input:focus {
        border-color: #EAB308 !important;
        box-shadow: 0 0 0 2px rgba(234, 179, 8, 0.3) !important;
    }
    
    /* Input Text alignment */
    input[type="text"], input[type="number"], .stDateInput {
        direction: ltr !important;
        text-align: center !important;
        font-weight: 700 !important;
    }
    
    /* 4. Quick Stats CSS (restled) */
    .metric-card {
        padding: 20px;
        text-align: center;
        border-top: 4px solid #1E3A8A !important;
        transition: transform 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        border-top-color: #EAB308 !important;
    }
    .metric-title {
        color: #1E3A8A;
        font-size: 15px;
        font-weight: 700;
        margin-bottom: 8px;
    }
    .metric-value {
        color: #1E3A8A;
        font-size: 32px;
        font-weight: 800;
    }
    .metric-icon {
        font-size: 28px;
        margin-bottom: 12px;
        color: #EAB308;
    }

    /* 5. Custom Success Alert Box */
    div[data-testid="stAlert"] {
        border-radius: 12px !important;
        border: none !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
        background-color: #FFFFFF !important;
        border-right: 5px solid #EAB308 !important; /* Gold accent line */
    }
    div[data-testid="stAlert"] p {
        color: #1E3A8A !important;
        font-weight: 600 !important;
    }
    </style>
""", unsafe_allow_html=True)

# ----------------- Database Setup -----------------
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

# ----------------- Page Header -----------------
col_logo, col_title = st.columns([1, 5])
with col_logo:
    if os.path.exists("assets/logo.png"):
        st.image("assets/logo.png", width=120)
    else:
        st.markdown("<h2 style='text-align: right; color: #1E3A8A; margin-top:15px;'>AURA</h2>", unsafe_allow_html=True)

with col_title:
    st.markdown("<h1 style='text-align: right; margin-top: 15px; font-size: 38px;'>نظام إدارة الحضور والانصراف</h1>", unsafe_allow_html=True)

st.markdown("---")

# ----------------- Professional Navigation Menu -----------------
selected = option_menu(
    menu_title=None, 
    options=["تسجيل اليومية", "إدارة الفريق", "تقارير المتابعة"], 
    icons=["calendar-check", "people-fill", "bar-chart-fill"], 
    menu_icon="cast", 
    default_index=0, 
    orientation="horizontal",
    styles={
        "container": {
            "padding": "0!important", 
            "background-color": "#F8FAFC", 
            "direction": "rtl",
            "border": "1px solid #1E3A8A",
            "border-radius": "12px"
        },
        "icon": {"color": "#EAB308", "font-size": "20px"},
        "nav-link": {
            "color": "#1E3A8A",
            "font-size": "18px", 
            "text-align": "center", 
            "margin": "0px", 
            "--hover-color": "#e2e8f0", 
            "font-family": "Cairo",
            "font-weight": "bold"
        },
        "nav-link-selected": {
            "background-color": "#1E3A8A", 
            "color": "white"
        },
    }
)
st.markdown("<br>", unsafe_allow_html=True)

# ----------------- Sections Content -----------------
if selected == "تسجيل اليومية":
    st.write("### 📈 إحصائيات اليوم")
    now_date_str = datetime.now().strftime("%Y-%m-%d")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Total Employees
    cursor.execute("SELECT COUNT(*) FROM employees")
    total_emp = cursor.fetchone()[0]
    
    # 2. Present Today
    cursor.execute("SELECT COUNT(DISTINCT employee_name) FROM attendance WHERE date=?", (now_date_str,))
    present_today = cursor.fetchone()[0]
    
    # 3. Late Today
    cursor.execute("SELECT COUNT(DISTINCT employee_name) FROM attendance WHERE date=? AND check_in > '09:00:00'", (now_date_str,))
    late_today = cursor.fetchone()[0]
    
    conn.close()
    
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">👥</div>
            <div class="metric-title">إجمالي الموظفين</div>
            <div class="metric-value">{total_emp}</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="metric-card" style="border-top-color: #10B981;">
            <div class="metric-icon">✅</div>
            <div class="metric-title">حضور اليوم</div>
            <div class="metric-value">{present_today}</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="metric-card" style="border-top-color: #EF4444;">
            <div class="metric-icon">⏰</div>
            <div class="metric-title">تأخير اليوم</div>
            <div class="metric-value">{late_today}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)

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
        
        # Split the row into 3 columns: Date, Hour, Minute
        col_date, col_hour, col_minute = st.columns([2, 1, 1])
        
        now = datetime.now()
        
        with col_date:
            manual_date = st.date_input("التاريخ:", now)
        with col_hour:
            # Dedicated field for the hour (24-hour format)
            hour = st.number_input("الساعة (0-23):", min_value=0, max_value=23, value=now.hour, step=1)
        with col_minute:
            # Dedicated field for the minute
            minute = st.number_input("الدقيقة (0-59):", min_value=0, max_value=59, value=now.minute, step=1)

        final_date = manual_date.strftime("%Y-%m-%d")
        # Combine hour and minute into a string format for the database
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