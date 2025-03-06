import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Check required packages
try:
    from pyzbar.pyzbar import decode
    from PIL import Image
except ImportError:
    st.error("""
    Missing required packages. Please install them using:
    ```
    pip install pyzbar pillow
    ```
    Note: On Windows, you might also need to install the Visual C++ Redistributable package.
    """)
    st.stop()

def check_excel_file():
    file_path = "D:/PYTHON CODE/taisan.xlsx"
    if not os.path.exists(file_path):
        st.error(f"Excel file {file_path} not found!")
        return False
    return True

# Load data from Excel
try:
    file_path = "D:/PYTHON CODE/taisan.xlsx"
    df = pd.read_excel(file_path)
    if 'Check' not in df.columns:
        df['Check'] = 'Chưa kiểm tra'
except Exception as e:
    st.error(f"Error loading Excel file: {str(e)}")
    df = None

def save_to_excel():
    try:
        df.to_excel(file_path, index=False)
        st.success("Changes saved to Excel!")
    except Exception as e:
        st.error(f"Error saving Excel file: {str(e)}")

def check_barcode(barcode_data):
    if df is None:
        st.error("Excel data not loaded!")
        return None
    
    barcode_data = str(barcode_data).strip()
    if not barcode_data:
        return None
    
    try:
        df['Barcode'] = df['Barcode'].astype(str)
        mask = df['Barcode'].str.strip() == barcode_data
        
        if mask.any():
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            df.loc[mask, 'Check'] = f'Đã kiểm tra ({now})'
            save_to_excel()
            return df[mask]
        else:
            return None
    except Exception as e:
        st.error(f"Error processing barcode: {str(e)}")
        return None

# Streamlit UI
st.title("Asset Inventory Scanner")

if check_excel_file():
    barcode_input = st.text_input("Nhập mã barcode:")
    uploaded_file = st.file_uploader("Hoặc tải lên hình ảnh barcode", type=["png", "jpg", "jpeg"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        barcodes = decode(image)
        if barcodes:
            barcode_input = barcodes[0].data.decode("utf-8")
            st.success(f"Scanned Barcode: {barcode_input}")
        else:
            st.error("Không tìm thấy mã barcode trong ảnh!")
    
    if st.button("Kiểm tra"):
        result = check_barcode(barcode_input)
        if result is not None:
            st.success(f"✅ Barcode {barcode_input} found!")
            st.dataframe(result)
        else:
            st.error("❌ Barcode not found!")
    
    # Display full data table
    st.subheader("Danh sách tài sản:")
    st.dataframe(df)
