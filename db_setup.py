import sqlite3

def create_db():
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_name TEXT,
            date TEXT,
            check_in TEXT,
            check_out TEXT,
            FOREIGN KEY (employee_name) REFERENCES employees (name)
        )
    ''')

    conn.commit()
    conn.close()
    print("تم إنشاء قاعدة البيانات بنجاح!")

if __name__ == '__main__':
    create_db()