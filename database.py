import sqlite3

# Create connection (SQLite auto-creates DB file)
conn = sqlite3.connect("user.db", check_same_thread=False)
cursor = conn.cursor()

# ================= USERS TABLE =================
def create_users_table():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()

def add_user(username, password):
    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # username already exists

def verify_user(username, password):
    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, password)
    )
    return cursor.fetchone() is not None

# ================= TIMETABLE TABLE =================
def create_timetable_table():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS timetable (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            day TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            subject TEXT NOT NULL
        )
    """)
    conn.commit()

def clear_day_timetable(username, day):
    cursor.execute(
        "DELETE FROM timetable WHERE username=? AND day=?",
        (username, day)
    )
    conn.commit()

def add_timetable_entry(username, day, start_time, end_time, subject):
    cursor.execute("""
        INSERT INTO timetable (username, day, start_time, end_time, subject)
        VALUES (?, ?, ?, ?, ?)
    """, (username, day, start_time, end_time, subject))
    conn.commit()

def get_user_timetable(username):
    cursor.execute("""
        SELECT day, start_time, end_time, subject
        FROM timetable
        WHERE username=?
        ORDER BY start_time
    """, (username,))
    
    rows = cursor.fetchall()
    timetable = {}

    for day, start, end, subject in rows:
        if day not in timetable:
            timetable[day] = []
        timetable[day].append({
            "start": start,
            "end": end,
            "subject": subject
        })

    return timetable