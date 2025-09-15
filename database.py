# database.py
import psycopg2
import streamlit as st
import random

# Lấy connection string từ Streamlit Secrets
# Bạn cần thêm vào Settings → Secrets của Streamlit Cloud:
# DATABASE_URL="postgresql://postgres:YOUR_PASSWORD@db.xxx.supabase.co:5432/postgres"
DATABASE_URL = st.secrets["DATABASE_URL"]

def get_connection():
    # Kết nối tới Supabase (bắt buộc SSL)
    return psycopg2.connect(DATABASE_URL, sslmode="require")

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # Bảng lưu đề toán
    cur.execute("""
        CREATE TABLE IF NOT EXISTS problems (
            id SERIAL PRIMARY KEY,
            question TEXT,
            image_path TEXT
        );
    """)

    # Bảng bookmark
    cur.execute("""
        CREATE TABLE IF NOT EXISTS bookmarks (
            id SERIAL PRIMARY KEY,
            username TEXT,
            problem_id INTEGER REFERENCES problems(id)
        );
    """)

    # Bảng lưu đáp án cache từ Wolfram
    cur.execute("""
        CREATE TABLE IF NOT EXISTS answers (
            id SERIAL PRIMARY KEY,
            problem_id INTEGER REFERENCES problems(id),
            variant_text TEXT,
            answer TEXT,
            UNIQUE(problem_id, variant_text)
        );
    """)

    conn.commit()
    cur.close()
    conn.close()

# ====== Các hàm cho problems ======
def add_problem(question, image_path=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO problems (question, image_path) VALUES (%s, %s)", (question, image_path))
    conn.commit()
    cur.close()
    conn.close()

def get_all_problems():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, question, image_path FROM problems")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def get_problem(problem_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, question, image_path FROM problems WHERE id=%s", (problem_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row

def get_random_problem():
    problems = get_all_problems()
    if not problems:
        return None
    return random.choice(problems)

# ====== Các hàm cho bookmarks ======
def add_bookmark(username, problem_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO bookmarks (username, problem_id) VALUES (%s, %s)", (username, problem_id))
    conn.commit()
    cur.close()
    conn.close()

def get_bookmarks(username):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT problems.id, problems.question, problems.image_path
        FROM problems JOIN bookmarks ON problems.id = bookmarks.problem_id
        WHERE bookmarks.username = %s
    """, (username,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

# ====== Các hàm cho answers (cache Wolfram) ======
def get_answer(problem_id, variant_text):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT answer FROM answers WHERE problem_id=%s AND variant_text=%s", (problem_id, variant_text))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row[0] if row else None

def save_answer(problem_id, variant_text, answer):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO answers (problem_id, variant_text, answer)
        VALUES (%s, %s, %s)
        ON CONFLICT (problem_id, variant_text) DO NOTHING
    """, (problem_id, variant_text, answer))
    conn.commit()
    cur.close()
    conn.close()

# Tạo bảng nếu chưa có
init_db()
