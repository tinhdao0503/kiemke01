import streamlit as st
import pandas as pd
import os
from datetime import datetime
from pyzbar.pyzbar import decode
from PIL import Image
import cv2
import numpy as np
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase

# Kiểm tra file Excel
def check_excel_file():
    file_path = "D:/PYTHON CODE/taisan.xlsx"
    if not os.path.exists(file_path):
        st.error(f"Excel file {file_path} not found!")
        return False
    return True

# Tải dữ liệu từ Excel
try:
    file_path = "D:/PYTHON CODE/taisan.xlsx"
    df = pd.read_excel(file_path)
    if 'Check' not in df.columns:
        df['Check'] = 'Chưa kiểm tra'
except Exception as e:
    st.error(f"Error loading Excel file: {str(e)}")
    df = None

# Lưu lại file Excel
def save_to_excel():
    try:
        df.to_excel(file_path, index=False)
        st.success("Changes saved to Excel!")
    except Exception as e:
        st.error(f"Error saving Excel file: {str(e)}")

# Kiểm tra mã barcode
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

# Bộ xử lý video để quét barcode
class BarcodeScanner(VideoTransformerBase):
    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        barcodes = decode(img)
        for barcode in barcodes:
            x, y, w, h = barcode.rect
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            barcode_data = barcode.data.decode("utf-8")
            st.session_state["scanned_barcode"] = barcode_data
        return img

# Giao diện Streamlit
st.title("📱 Asset Inventory Scanner")

if check_excel_file():
    barcode_input = st.text_input("🔍 Nhập mã barcode:")
    uploaded_file = st.file_uploader("📷 Hoặc tải lên hình ảnh barcode", type=["png", "jpg", "jpeg"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        barcodes = decode(image)
        if barcodes:
            barcode_input = barcodes[0].data.decode("utf-8")
            st.success(f"✅ Scanned Barcode: {barcode_input}")
        else:
            st.error("❌ Không tìm thấy mã barcode trong ảnh!")
    
    # Quét barcode từ camera
    st.subheader("📸 Quét mã vạch bằng camera:")
    webrtc_streamer(key="barcode-scanner", video_transformer_factory=BarcodeScanner)
    
    if "scanned_barcode" in st.session_state:
        barcode_input = st.session_state["scanned_barcode"]
        st.success(f"📌 Đã quét: {barcode_input}")
    
    if st.button("🔍 Kiểm tra"):
        result = check_barcode(barcode_input)
        if result is not None:
            st.success(f"✅ Barcode {barcode_input} found!")
            st.dataframe(result)
        else:
            st.error("❌ Barcode not found!")
    
    # Hiển thị danh sách tài sản
    st.subheader("📋 Danh sách tài sản:")
    st.dataframe(df)
