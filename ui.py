# ui.py (các hàm trang)
import streamlit as st
import os
from db import add_problem, get_random_problem, get_all_problems, update_problem, delete_problem
from db import create_user_request, list_user_requests, mark_request_processed
from db import save_for_client, get_saved_for_client

# ADMIN PASSWORD (bạn có thể thay đổi ở đây hoặc đọc từ env)
ADMIN_PASSWORD = os.getenv("MATHAPP_ADMIN_PW", "mypassword123")  # đổi mật khẩu mặc định

def is_admin():
    if "admin_auth" not in st.session_state:
        st.session_state.admin_auth = False
    # Sidebar input để đăng nhập admin (1 lần per session)
    with st.sidebar.expander("🔒 Admin login", expanded=False):
        pw = st.text_input("Mật khẩu admin", type="password", key="admin_pw_input")
        if st.button("Đăng nhập", key="admin_login_btn"):
            if pw == ADMIN_PASSWORD:
                st.session_state.admin_auth = True
                st.success("Bạn đã đăng nhập admin.")
            else:
                st.error("Sai mật khẩu.")
    return st.session_state.admin_auth

def show_add_problem():
    admin = is_admin()
    if not admin:
        st.warning("Chỉ admin mới có quyền thêm bài. Hãy đăng nhập ở phần 'Admin login' bên trái.")
        return

    st.header("➕ Thêm bài mới (Admin)")
    text = st.text_area("Nhập đề toán")
    image = st.file_uploader("Chọn hình minh họa (tùy chọn)", type=["png", "jpg", "jpeg"], key="add_img")
    if st.button("Lưu (Admin)"):
        image_path = None
        if image:
            folder = "images"
            os.makedirs(folder, exist_ok=True)
            image_path = os.path.join(folder, image.name)
            with open(image_path, "wb") as f:
                f.write(image.getbuffer())
        add_problem(text, image_path)
        st.success("✅ Đã lưu bài toán (Admin).")

def show_random_problem():
    st.header("🎲 Làm bài ngẫu nhiên")
    problem = get_random_problem()
    if problem:
        st.subheader("Đề toán")
        st.write(problem[1])
        if problem[2]:
            st.image(problem[2], width=400)
        st.info(f"📊 Bài này đã xuất hiện {problem[3]} lần.")

        st.markdown("---")
        st.subheader("Nếu bạn là người dùng (không admin), bạn có thể:")
        reporter = st.text_input("Tên/Email của bạn (để lưu/khôi phục):", key="reporter_name")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("⭐ Lưu vào danh sách cá nhân"):
                if reporter.strip()=="":
                    st.warning("Nhập tên/email (client key) để lưu.")
                else:
                    save_for_client(reporter, problem[0], problem[1])
                    st.success("Đã lưu vào bộ sưu tập của bạn.")
        with col2:
            note = st.text_area("Ghi chú / Tại sao bạn thấy khó? (tùy chọn)", height=80, key="user_note")
        with col3:
            if st.button("⚑ Gửi yêu cầu cho owner (báo bài khó)"):
                # lưu yêu cầu: reporter + note hoặc nguyên đề
                create_user_request(reporter if reporter else "Khách", note if note.strip() else problem[1], None)
                st.success("Đã gửi yêu cầu cho owner. Owner sẽ kiểm tra và xử lý.")
    else:
        st.warning("Chưa có bài nào trong DB.")

def show_manage_problems():
    admin = is_admin()
    if not admin:
        st.warning("Chỉ admin mới được xem/quản lý danh sách (để tránh xóa nhầm).")
        return

    st.header("📂 Danh sách bài (Admin)")
    problems = get_all_problems()
    if not problems:
        st.info("Chưa có bài nào!")
    else:
        for p in problems:
            st.markdown(f"**ID {p[0]}** | Xuất hiện: {p[3]} lần | Ngày: {p[4]}")
            st.write(p[1])
            if p[2]:
                st.image(p[2], width=200)
            with st.expander("✏️ Sửa / ❌ Xóa"):
                new_text = st.text_area("Chỉnh sửa đề", value=p[1], key=f"edit_{p[0]}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Lưu sửa", key=f"save_{p[0]}"):
                        update_problem(p[0], new_text)
                        st.success("Đã cập nhật.")
                with col2:
                    if st.button("Xóa", key=f"delete_{p[0]}"):
                        delete_problem(p[0])
                        st.warning("Đã xóa.")

    # Hiển thị user requests (báo bài khó) để owner xử lý
    st.markdown("---")
    st.subheader("📨 Yêu cầu từ người dùng (chưa xử lý)")
    requests = list_user_requests(unprocessed_only=True)
    if not requests:
        st.info("Không có yêu cầu mới.")
    else:
        for r in requests:
            st.markdown(f"**ID req {r[0]}** | Người báo: {r[1]} | {r[4]}")
            st.write(r[2])
            if r[3]:
                st.image(r[3], width=200)
            if st.button("Đánh dấu đã xử lý", key=f"proc_{r[0]}"):
                mark_request_processed(r[0])
                st.success("Đã đánh dấu xử lý.")

def show_my_saved():
    st.header("📥 Bộ sưu tập cá nhân")
    client = st.text_input("Nhập tên/email bạn đã dùng để lưu:", key="client_view")
    if st.button("Xem bộ sưu tập"):
        if client.strip()=="":
            st.warning("Nhập tên/email để xem.")
        else:
            saved = get_saved_for_client(client)
            if not saved:
                st.info("Bạn chưa lưu bài nào.")
            else:
                for s in saved:
                    st.markdown(f"**Saved ID {s[0]}** | Lưu lúc: {s[4]}")
                    if s[2]:
                        st.markdown(f"- Gốc bài ID: {s[2]}")
                    st.write(s[3])
                    st.markdown("---")
