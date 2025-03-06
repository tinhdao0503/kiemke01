import pandas as pd
import streamlit as st
from datetime import datetime

# URL của file Excel trên GitHub
EXCEL_URL = "https://raw.githubusercontent.com/tinhdao0503/kiemke01/main/taisan.xlsx"

# Tải dữ liệu từ Excel
@st.cache_data
def load_data():
    try:
        df = pd.read_excel(EXCEL_URL)
        if 'Check' not in df.columns:
            df['Check'] = 'Chưa kiểm tra'
        return df
    except Exception as e:
        st.error(f"Lỗi khi tải dữ liệu từ Excel: {str(e)}")
        return None

def check_barcode(barcode_data, df):
    barcode_data = str(barcode_data).strip()
    if not barcode_data:
        return None
    try:
        df['Barcode'] = df['Barcode'].astype(str)
        mask = df['Barcode'].str.strip() == barcode_data
        if mask.any():
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            df.loc[mask, 'Check'] = f'Đã kiểm tra ({now})'
            return df[mask]
        else:
            return None
    except Exception as e:
        st.error(f"Lỗi xử lý barcode: {str(e)}")
        return None

# Giao diện Streamlit
st.title("🔍 Ứng dụng Kiểm Kê Tài Sản")

df = load_data()
if df is not None:
    barcode_input = st.text_input("Nhập mã barcode:")
    if st.button("Kiểm tra"):
        result = check_barcode(barcode_input, df)
        if result is not None:
            st.success(f"✅ Barcode {barcode_input} đã được kiểm tra!")
            st.dataframe(result)
        else:
            st.error("❌ Barcode không tồn tại!")
    st.write("### Dữ liệu kiểm kê:")
    st.dataframe(df)
