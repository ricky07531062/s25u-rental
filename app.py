import streamlit as st
import pandas as pd
import os
from datetime import date, datetime

# --- 設定 ---
DATA_FILE = 's25u_rental_db.csv'

# 🔥 最新手機庫存清單
PHONE_INVENTORY = [
    "S25U 白色",
    "S25U 綠色",
    "S25U 藍色",
    "S24U 藍色",
    "S23U 黑色",
    "iPhone 17 Pro 銀色"
]

st.set_page_config(page_title="手機租賃管理系統", layout="wide", page_icon="📱")

# --- 標題區 ---
st.title("📱 演唱會手機租賃管理系統")
st.caption("老闆專用後台 | 點擊表格即可直接修改 | 記得按儲存")

# --- 1. 左側邊欄：新增/登記訂老闆單 ---
with st.sidebar:
    st.header("📝 新增租借單")
    with st.form(key='rental_form'):
        col1, col2 = st.columns(2)
        with col1:
            customer_name = st.text_input("客戶姓名")
            gender = st.selectbox("性別", ["女", "男", "其他"])
        with col2:
            phone_number = st.text_input("聯絡電話")
            age = st.number_input("年齡", 15, 80, 25)

        st.markdown("---")
        target_city = st.selectbox("演唱會縣市", ["台北", "高雄", "桃園", "台中", "其他"])
        concert_name = st.text_input("演唱會名稱 (選填)")
        
        # 日期選擇
        date_range = st.date_input("租借日期區間", value=(date.today(), date.today()), format="YYYY/MM/DD")
        
        st.markdown("---")
        # 選擇哪一台手機
        selected_phone = st.selectbox("指派手機", PHONE_INVENTORY)
        
        rent_fee = st.number_input("租金收入 ($)", min_value=0, value=1200, step=100)
        deposit = st.number_input("收取押金 ($)", min_value=0, value=3000, step=500)
        
        # 狀態
        status = st.selectbox("訂單狀態", ["預約確認", "已取機(租借中)", "已歸還(結案)", "取消"])
        
        submit = st.form_submit_button("✅ 建立訂單")

# --- 2. 邏輯處理：儲存新訂單 ---
if submit:
    start_date = date_range[0]
    end_date = date_range[1] if len(date_range) > 1 else start_date
    
    new_data = {
        "建檔時間": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "狀態": status,
        "手機編號": selected_phone, 
        "開始日期": start_date,
        "結束日期": end_date,
        "姓名": customer_name,
        "電話": phone_number,
        "性別": gender,
        "年齡": age,
        "縣市": target
