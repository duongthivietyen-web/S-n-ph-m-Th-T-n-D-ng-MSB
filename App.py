import streamlit as st
import pandas as pd
import os

# Cấu hình trang Streamlit
st.set_page_config(
    page_title="Hệ Thống Quản Lý Khách Hàng",
    page_icon="📋",
    layout="wide"
)

# Tên file lưu trữ dữ liệu Excel
DATA_FILE = "danh_sach_khach_hang.xlsx"

# Hàm khởi tạo hoặc đọc dữ liệu từ file Excel
def load_data():
    if not os.path.exists(DATA_FILE):
        # Tạo DataFrame trống nếu file chưa tồn tại
        df = pd.DataFrame(columns=[
            "Số điện thoại", 
            "Tên khách hàng", 
            "Địa chỉ", 
            "Thu nhập/tháng (VNĐ)", 
            "Ghi chú",
            "Thời gian tạo"
        ])
        df.to_excel(DATA_FILE, index=False)
        return df
    else:
        # Đọc dữ liệu từ file Excel, đảm bảo Số điện thoại đọc dưới dạng chuỗi (string)
        return pd.read_excel(DATA_FILE, dtype={"Số điện thoại": str})

# Hàm lưu dữ liệu mới vào file Excel
def save_customer_data(phone, name, address, income, note):
    df = load_data()
    
    new_data = {
        "Số điện thoại": str(phone),
        "Tên khách hàng": name,
        "Địa chỉ": address,
        "Thu nhập/tháng (VNĐ)": income,
        "Ghi chú": note,
        "Thời gian tạo": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Thêm dòng mới vào DataFrame
    df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
    
    # Ghi lại vào file Excel
    df.to_excel(DATA_FILE, index=False)

# Thanh điều hướng (Sidebar Menu)
st.sidebar.title("📌 Danh Mục")
page = st.sidebar.radio("Chọn chức năng:", ["Điền thông tin khách hàng", "Trang Admin"])

# ==========================================
# TRANG 1: ĐIỀN THÔNG TIN KHÁCH HÀNG
# ==========================================
if page == "Điền thông tin khách hàng":
    st.title("📝 Nhập Thông Tin Khách Hàng")
    st.write("Vui lòng điền đầy đủ các thông tin bên dưới:")

    with st.form(key="customer_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            phone = st.text_input("Số điện thoại (*)", placeholder="Ví dụ: 0901234567")
            name = st.text_input("Tên khách hàng (*)", placeholder="Ví dụ: Nguyễn Văn A")
            income = st.number_input("Thu nhập/tháng (VNĐ)", min_value=0, step=1000000, format="%d")
            
        with col2:
            address = st.text_input("Địa chỉ", placeholder="Ví dụ: Quận 1, TP. Hồ Chí Minh")
            note = st.text_area("Ghi chú", placeholder="Nhu cầu khách hàng, thời gian gọi lại...", height=108)

        submit_button = st.form_submit_button(label="💾 Lưu thông tin")

    if submit_button:
        # Kiểm tra tính hợp lệ cơ bản
        if not phone.strip() or not name.strip():
st.error("⚠️ Vui lòng nhập đầy đủ **Số điện thoại** và **Tên khách hàng**!")
        else:
            save_customer_data(phone, name, address, income, note)
            st.success(f"✅ Đã lưu thành công thông tin khách hàng **{name}**!")

# ==========================================
# TRANG 2: TRANG ADMIN (QUẢN LÝ)
# ==========================================
elif page == "Trang Admin":
    st.title("🔐 Trang Quản Lý (Admin)")

    # Xử lý xác thực đăng nhập đơn giản
    if "admin_logged_in" not in st.session_state:
        st.session_state["admin_logged_in"] = False

    if not st.session_state["admin_logged_in"]:
        st.subheader("Đăng nhập Admin")
        password = st.text_input("Mật khẩu truy cập", type="password")
        if st.button("Đăng nhập"):
            # Mật khẩu mặc định là 'admin123' (Bạn có thể đổi mật khẩu tại đây)
            if password == "admin123":
                st.session_state["admin_logged_in"] = True
                st.rerun()
            else:
                st.error("❌ Mật khẩu không chính xác!")
    else:
        # Nút đăng xuất
        if st.sidebar.button("Đăng xuất Admin"):
            st.session_state["admin_logged_in"] = False
            st.rerun()

        # Đọc dữ liệu hiện có
        df = load_data()

        st.subheader("📊 Danh sách khách hàng đã lưu")
        
        if df.empty:
            st.info("Chưa có dữ liệu khách hàng nào được lưu.")
        else:
            # Thống kê nhanh
            col_stat1, col_stat2 = st.columns(2)
            col_stat1.metric("Tổng số khách hàng", len(df))
            col_stat2.metric("Thu nhập trung bình", f"{df['Thu nhập/tháng (VNĐ)'].mean():,.0f} VNĐ")

            # Bộ lọc tìm kiếm
            search_term = st.text_input("🔍 Tìm kiếm theo Tên hoặc Số điện thoại:", "")
            if search_term:
                filtered_df = df[
                    df["Tên khách hàng"].astype(str).str.contains(search_term, case=False) |
                    df["Số điện thoại"].astype(str).str.contains(search_term, case=False)
                ]
            else:
                filtered_df = df

            # Hiển thị bảng dữ liệu
            st.dataframe(
                filtered_df.style.format({"Thu nhập/tháng (VNĐ)": "{:,.0f}"}),
                use_container_width=True
            )

            st.write("---")
            st.subheader("📥 Xuất Dữ Liệu Excel")

            # Chuyển đổi DataFrame thành file Excel để tải xuống
            import io
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='KhachHang')
            
            buffer.seek(0)

            # Nút Tải Xuất File Excel
            st.download_button(
label="📥 Tải xuống File Excel (.xlsx)",
                data=buffer,
                file_name=f"Danh_Sach_Khach_Hang_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
