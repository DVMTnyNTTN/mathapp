# db.py (các hàm phụ trợ DB)
import sqlite3
import datetime
import os

DB_PATH = "math_problems.db"
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
c = conn.cursor()

# Tạo bảng problems nếu chưa có (nếu bạn đã có, giữ nguyên)
c.execute("""
CREATE TABLE IF NOT EXISTS problems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    image_path TEXT,
    times_shown INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# Bảng lưu request từ user (friend) -> admin kiểm duyệt
c.execute("""
CREATE TABLE IF NOT EXISTS user_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reporter TEXT,          -- nickname/email người báo
    problem_text TEXT,      -- nội dung hoặc note họ nhập
    image_path TEXT,        -- nếu họ upload ảnh (tùy chọn)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed INTEGER DEFAULT 0  -- 0 = chưa xử lý, 1 = đã xử lý
)
""")

# Bảng lưu bộ sưu tập cá nhân (user saved problems)
c.execute("""
CREATE TABLE IF NOT EXISTS saved_problems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_key TEXT,        -- nickname/email do user nhập (để nhận dạng)
    problem_id INTEGER,     -- id từ problems (có thể NULL nếu user lưu 1 đề tự nhập)
    problem_text TEXT,      -- bản sao nội dung lúc họ lưu (dễ trace)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()

# Hàm sẵn có: add_problem, get_random_problem, get_all_problems, update_problem, delete_problem
def add_problem(text, image_path=None):
    c.execute("INSERT INTO problems (text, image_path) VALUES (?, ?)", (text, image_path))
    conn.commit()

def get_random_problem():
    import random
    c.execute("SELECT id, text, image_path, times_shown FROM problems")
    rows = c.fetchall()
    if not rows:
        return None
    weights = [1 / (1 + r[3]) for r in rows]
    chosen = random.choices(rows, weights=weights, k=1)[0]
    c.execute("UPDATE problems SET times_shown = times_shown + 1 WHERE id=?", (chosen[0],))
    conn.commit()
    return chosen

def get_all_problems():
    c.execute("SELECT id, text, image_path, times_shown, created_at FROM problems ORDER BY id DESC")
    return c.fetchall()

def update_problem(problem_id, new_text):
    c.execute("UPDATE problems SET text=? WHERE id=?", (new_text, problem_id))
    conn.commit()

def delete_problem(problem_id):
    c.execute("DELETE FROM problems WHERE id=?", (problem_id,))
    conn.commit()

# --- Hàm cho user requests ---
def create_user_request(reporter, problem_text, image_path=None):
    c.execute("INSERT INTO user_requests (reporter, problem_text, image_path) VALUES (?, ?, ?)",
              (reporter, problem_text, image_path))
    conn.commit()

def list_user_requests(unprocessed_only=True):
    if unprocessed_only:
        c.execute("SELECT id, reporter, problem_text, image_path, created_at FROM user_requests WHERE processed=0 ORDER BY created_at DESC")
    else:
        c.execute("SELECT id, reporter, problem_text, image_path, created_at, processed FROM user_requests ORDER BY created_at DESC")
    return c.fetchall()

def mark_request_processed(req_id):
    c.execute("UPDATE user_requests SET processed=1 WHERE id=?", (req_id,))
    conn.commit()

# --- Hàm cho saved_problems ---
def save_for_client(client_key, problem_id, problem_text):
    c.execute("INSERT INTO saved_problems (client_key, problem_id, problem_text) VALUES (?, ?, ?)",
              (client_key, problem_id, problem_text))
    conn.commit()

def get_saved_for_client(client_key):
    c.execute("SELECT id, client_key, problem_id, problem_text, created_at FROM saved_problems WHERE client_key=? ORDER BY created_at DESC", (client_key,))
    return c.fetchall()
