import streamlit as st
import pandas as pd
import os

# Khởi tạo dữ liệu
if "data" not in st.session_state:
    st.session_state.data = []

st.title("📋 Quản lý thông tin khách hàng")

# Form nhập thông tin khách hàng
with st.form("customer_form"):
    phone = st.text_input("Số điện thoại")
    name = st.text_input("Tên khách hàng")
    address = st.text_input("Địa chỉ")
    income = st.number_input("Thu nhập/tháng", min_value=0, step=1000000)
    note = st.text_area("Ghi chú")

    submitted = st.form_submit_button("Lưu thông tin")

    if submitted:
        st.session_state.data.append({
            "Số điện thoại": phone,
            "Tên khách hàng": name,
            "Địa chỉ": address,
            "Thu nhập/tháng": income,
            "Ghi chú": note
        })
        st.success("✅ Thông tin khách hàng đã được lưu!")

# Trang admin hiển thị dữ liệu
st.subheader("📊 Danh sách khách hàng")
df = pd.DataFrame(st.session_state.data)
st.dataframe(df)

# Xuất file Excel
if not df.empty:
    excel_file = "khach_hang.xlsx"
    df.to_excel(excel_file, index=False)

    with open(excel_file, "rb") as f:
        st.download_button(
            label="📥 Tải xuống file Excel",
            data=f,
            file_name=excel_file,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
