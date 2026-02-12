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
        "縣市": target_city,
        "演唱會": concert_name,
        "租金": rent_fee,
        "押金": deposit
    }
    
    df_new = pd.DataFrame([new_data])
    
    if not os.path.exists(DATA_FILE):
        df_new.to_csv(DATA_FILE, index=False)
    else:
        df_new.to_csv(DATA_FILE, mode='a', header=False, index=False)
    st.toast(f"已新增訂單：{customer_name}", icon="🎉")

# --- 3. 主畫面顯示 ---

if os.path.exists(DATA_FILE):
    # 讀取資料
    df = pd.read_csv(DATA_FILE)
    
    # 💡【防呆 1】：確保欄位名稱一致
    if '手機編號' not in df.columns:
        if '手機型號' in df.columns:
            df['手機編號'] = df['手機型號']
        else:
            df['手機編號'] = "未知型號"

    # 💡【防呆 2】：這裡就是修復紅色畫面的關鍵！強制轉換日期格式
    # 把文字轉成真正的 Date 物件，如果轉換失敗就留空，避免程式崩潰
    df['開始日期'] = pd.to_datetime(df['開始日期'], errors='coerce').dt.date
    df['結束日期'] = pd.to_datetime(df['結束日期'], errors='coerce').dt.date

    # KPI 計算
    total_revenue = df[df['狀態'] != '取消']['租金'].sum()
    active_rentals = len(df[df['狀態'] == '已取機(租借中)'])
    
    occupied_phones = df[df['狀態'].isin(['預約確認', '已取機(租借中)'])]['手機編號'].tolist()
    available_count = len(PHONE_INVENTORY) - len(set(occupied_phones))
    
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("💰 總營收", f"${total_revenue:,.0f}")
    kpi2.metric("🚀 出租中", f"{active_rentals} 台")
    kpi3.metric("📦 庫存剩餘", f"約 {available_count} 台")
    kpi4.metric("📈 總訂單數", len(df))

    st.divider()

    # --- 分頁管理 ---
    tab1, tab2, tab3 = st.tabs(["✏️ 訂單管理與編輯", "🔍 庫存佔用表", "📊 客群分析"])

    with tab1:
        st.info("💡 操作教學：直接點擊下方表格的內容進行修改，改完後請務必按下「💾 儲存修改」按鈕！")
        
        # 🔥🔥🔥 可編輯表格 🔥🔥🔥
        edited_df = st.data_editor(
            df.sort_values(by="開始日期", ascending=False), 
            use_container_width=True,
            num_rows="dynamic",
            column_config={
                "狀態": st.column_config.SelectboxColumn(
                    "狀態",
                    options=["預約確認", "已取機(租借中)", "已歸還(結案)", "取消"],
                    required=True
                ),
                "手機編號": st.column_config.SelectboxColumn(
                    "手機型號",
                    options=PHONE_INVENTORY,
                    required=True
                ),
                "租金": st.column_config.NumberColumn(format="$%d"),
                "押金": st.column_config.NumberColumn(format="$%d"),
                "開始日期": st.column_config.DateColumn(format="YYYY-MM-DD"),
                "結束日期": st.column_config.DateColumn(format="YYYY-MM-DD"),
            }
        )

        # 儲存按鈕
        col_save, col_info = st.columns([1, 4])
        with col_save:
            if st.button("💾 儲存修改", type="primary"):
                # 將修改後的資料寫回 CSV
                edited_df.to_csv(DATA_FILE, index=False)
                st.success("✅ 資料已更新！")
                st.rerun()
        
        st.divider()
        
        with st.expander("🗑️ 刪除訂單 (進階選項)", expanded=False):
            st.warning("注意：建議直接在上方表格將狀態改為「取消」即可。若堅持刪除，請由下方操作。")
            # 這裡也要防呆，轉成字串顯示避免報錯
            delete_options = [f"{i}: {row['姓名']} - {row['手機編號']} ({row['開始日期']})" for i, row in df.iterrows()]
            if delete_options:
                selected_to_delete = st.selectbox("選擇要永久刪除的訂單：", delete_options)
                if st.button("確認刪除 ❌"):
                    index_to_drop = int(selected_to_delete.split(":")[0])
                    df.drop(index_to_drop).to_csv(DATA_FILE, index=False)
                    st.success("訂單已刪除！")
                    st.rerun()

    with tab2:
        st.subheader("手機預約狀況")
        occupied = df[df['狀態'].isin(['預約確認', '已取機(租借中)'])]
        if not occupied.empty:
            display_cols = occupied[['手機編號', '開始日期', '結束日期', '姓名', '狀態']]
            st.dataframe(display_cols, use_container_width=True)
        else:
            st.success("目前所有手機皆在庫，隨時可租！")

    with tab3:
        col_a, col_b = st.columns(2)
        with col_a:
            st.write("📍 **租客來自哪個縣市？**")
            if '縣市' in df.columns and not df['縣市'].empty:
                 st.bar_chart(df['縣市'].value_counts())
        with col_b:
            st.write("👩 **租客性別比例**")
            if '性別' in df.columns and not df['性別'].empty:
                st.bar_chart(df['性別'].value_counts())

else:
    st.info("👋 歡迎老闆！請從左側建立您的第一筆租借資料。")
