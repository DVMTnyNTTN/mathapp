import streamlit as st
import random
import database
import bookmarks

# Khởi tạo DB
database.init_db()
bookmarks.init_bookmarks_table()

# Tài khoản admin
ADMIN_USER = "tribilielish"
ADMIN_PASS = "151008"

def main():
    st.set_page_config(page_title="Math Practice App", layout="centered")

    # -------------------------
    # Đăng nhập
    # -------------------------
    if "user" not in st.session_state:
        st.session_state["user"] = None
        st.session_state["is_admin"] = False

    if not st.session_state["user"]:
        st.title("🔑 Đăng nhập")
        username = st.text_input("Tên đăng nhập")
        password = st.text_input("Mật khẩu", type="password")

        if st.button("Vào App"):
            if username == ADMIN_USER and password == ADMIN_PASS:
                st.session_state["user"] = username
                st.session_state["is_admin"] = True
                st.success("✅ Đăng nhập admin thành công!")
                st.rerun()
            elif username.strip() != "" and password.strip() != "":
                st.session_state["user"] = username.strip()
                st.session_state["is_admin"] = False
                st.success(f"✅ Chào mừng, {st.session_state['user']}!")
                st.rerun()
            else:
                st.warning("❌ Sai thông tin đăng nhập!")
        return

    # -------------------------
    # Sau khi login
    # -------------------------
    st.sidebar.title("📚 Menu")
    st.sidebar.write(f"👤 Đang đăng nhập: {st.session_state['user']}")

    if st.sidebar.button("🚪 Đăng xuất"):
        st.session_state["user"] = None
        st.session_state["is_admin"] = False
        st.rerun()

    # Menu phân quyền
    if st.session_state["is_admin"]:
        page = st.sidebar.selectbox("Chọn chức năng", [
            "➕ Thêm bài toán",
            "📝 Quản lý bài toán",
            "🎲 Làm bài ngẫu nhiên",
            "📌 Bookmark của tôi"
        ])
    else:
        page = st.sidebar.selectbox("Chọn chức năng", [
            "🎲 Làm bài ngẫu nhiên",
            "📌 Bookmark của tôi"
        ])

    # -------------------------
    # Trang thêm bài toán (admin only)
    # -------------------------
    if page == "➕ Thêm bài toán" and st.session_state["is_admin"]:
        st.title("➕ Thêm bài toán mới")

        question = st.text_area("Nhập đề toán")
        image = st.file_uploader("Tải ảnh minh họa (tùy chọn)", type=["png", "jpg", "jpeg"])

        if st.button("Lưu bài toán"):
            image_path = None
            if image:
                image_path = f"uploads/{image.name}"
                with open(image_path, "wb") as f:
                    f.write(image.getbuffer())

            database.add_problem(question, image_path)
            st.success("✅ Đã lưu bài toán!")

    # -------------------------
    # Trang quản lý bài toán (admin only)
    # -------------------------
    elif page == "📝 Quản lý bài toán" and st.session_state["is_admin"]:
        st.title("📝 Quản lý bài toán")

        problems = database.get_all_problems()
        if not problems:
            st.info("Chưa có bài toán nào.")
        else:
            for pid, question, image_path in problems:
                st.subheader(f"Bài {pid}")
                st.write(question)
                if image_path:
                    st.image(image_path, width=200)

                with st.expander("✏️ Sửa bài này"):
                    new_question = st.text_area("Sửa đề toán", value=question, key=f"q_{pid}")
                    new_image = st.file_uploader("Đổi ảnh minh họa (tùy chọn)", type=["png", "jpg", "jpeg"], key=f"img_{pid}")
                    if st.button("Cập nhật", key=f"update_{pid}"):
                        image_path_new = image_path
                        if new_image:
                            image_path_new = f"uploads/{new_image.name}"
                            with open(image_path_new, "wb") as f:
                                f.write(new_image.getbuffer())
                        database.update_problem(pid, new_question, image_path_new)
                        st.success("✅ Đã cập nhật!")
                        st.rerun()

                if st.button("🗑️ Xóa bài này", key=f"delete_{pid}"):
                    database.delete_problem(pid)
                    st.warning("❌ Đã xóa bài toán!")
                    st.rerun()

    # -------------------------
    # Trang làm bài random
    # -------------------------
    elif page == "🎲 Làm bài ngẫu nhiên":
        st.title("🎲 Làm bài ngẫu nhiên")

        problem = database.get_random_problem()
        if not problem:
            st.info("Chưa có bài toán nào, hãy thêm trước!")
        else:
            pid, question, image_path = problem
            st.subheader(f"Bài {pid}")
            st.write(question)
            if image_path:
                st.image(image_path, width=300)

            if st.button("📌 Bookmark bài này"):
                bookmarks.add_bookmark(st.session_state["user"], pid)
                st.success("Đã bookmark!")

    # -------------------------
    # Trang bookmark
    # -------------------------
    elif page == "📌 Bookmark của tôi":
        st.title(f"📌 Bookmark của {st.session_state['user']}")

        user_id = st.session_state["user"]
        data = bookmarks.get_bookmarks(user_id)

        if not data:
            st.info("Bạn chưa bookmark bài nào.")
        else:
            for pid, question, image_path in data:
                st.subheader(f"Bài {pid}")
                st.write(question)
                if image_path:
                    st.image(image_path, width=300)

if __name__ == "__main__":
    main()
