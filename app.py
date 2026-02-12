import streamlit as st
import pandas as pd
import os
from datetime import date, datetime

# --- 設定 ---
DATA_FILE = 's25u_rental_db.csv'
# 假設老闆你有 5 台手機 (可以自己增減)
PHONE_INVENTORY = ["S25U-01 (黑)", "S25U-02 (灰)", "S25U-03 (銀)", "S25U-04 (紫)", "S25U-05 (金)"]

st.set_page_config(page_title="S25U 租賃管理系統", layout="wide", page_icon="📱")

# --- 標題區 ---
st.title("📱 S25U 演唱會租賃管理系統 (專業版)")
st.caption("老闆專用後台 | 庫存監控 | 營收統計")

# --- 1. 左側邊欄：新增/登記訂單 ---
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

# --- 2. 邏輯處理：儲存資料 ---
if submit:
    # 處理日期格式
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
    st.toast(f"已新增訂單：{customer_name} ({selected_phone})", icon="🎉")

# --- 3. 主畫面顯示 ---

if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
    
    # 數據概況 (KPI)
    total_revenue = df[df['狀態'] != '取消']['租金'].sum()
    active_rentals = len(df[df['狀態'] == '已取機(租借中)'])
    pending_rentals = len(df[df['狀態'] == '預約確認'])
    
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("💰 總營收", f"${total_revenue:,.0f}")
    kpi2.metric("🚀 出租中", f"{active_rentals} 台")
    kpi3.metric("📅 預約中", f"{pending_rentals} 單")
    kpi4.metric("📈 總訂單數", len(df))

    st.divider()

    # --- 分頁檢視 ---
    tab1, tab2, tab3 = st.tabs(["📋 所有訂單管理", "🔍 庫存佔用表", "📊 客群分析"])

    with tab1:
        # 提供簡單的篩選器
        filter_status = st.multiselect("篩選狀態", df['狀態'].unique(), default=df['狀態'].unique())
        show_df = df[df['狀態'].isin(filter_status)]
        
        # 顯示可編輯的表格 (老闆可以直接在表格上改狀態，例如把 '預約' 改成 '已歸還')
        st.info("💡 提示：雖然這裡是唯讀檢視，若需修改建議下載 Excel 修改後重新上傳（進階功能需資料庫串接）")
        st.dataframe(
            show_df.sort_values(by="開始日期", ascending=False),
            use_container_width=True,
            column_config={
                "租金": st.column_config.NumberColumn(format="$%d"),
                "押金": st.column_config.NumberColumn(format="$%d"),
                "開始日期": st.column_config.DateColumn(format="YYYY-MM-DD"),
                "結束日期": st.column_config.DateColumn(format="YYYY-MM-DD"),
            }
        )
    
    with tab2:
        st.subheader("手機預約狀況")
        # 這裡簡單顯示哪些手機被借出去了 (針對還沒歸還的)
        occupied = df[df['狀態'].isin(['預約確認', '已取機(租借中)'])]
        if not occupied.empty:
            st.dataframe(occupied[['手機編號', '開始日期', '結束日期', '姓名', '狀態']], use_container_width=True)
        else:
            st.success("目前所有手機皆在庫，隨時可租！")

    with tab3:
        col_a, col_b = st.columns(2)
        with col_a:
            st.write("📍 **租客來自哪個縣市看演唱會？**")
            st.bar_chart(df['縣市'].value_counts())
        with col_b:
            st.write("👩 **租客性別比例**")
            st.bar_chart(df['性別'].value_counts())

else:
    st.info("👋 歡迎老闆！請從左側建立您的第一筆租借資料。")
