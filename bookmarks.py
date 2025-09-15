import sqlite3

DB_FILE = "database.db"

def init_bookmarks_table():
    """Tạo bảng bookmarks nếu chưa có"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookmarks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            problem_id INTEGER NOT NULL,
            UNIQUE(user_id, problem_id)
        )
    """)
    conn.commit()
    conn.close()

def add_bookmark(user_id, problem_id):
    """Thêm bookmark cho user"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT OR IGNORE INTO bookmarks (user_id, problem_id) VALUES (?, ?)",
            (user_id, problem_id),
        )
        conn.commit()
    finally:
        conn.close()

def get_bookmarks(user_id):
    """Lấy danh sách bài đã bookmark theo user_id"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT problems.id, problems.question, problems.image_path
        FROM bookmarks
        JOIN problems ON problems.id = bookmarks.problem_id
        WHERE bookmarks.user_id = ?
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows
