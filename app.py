import streamlit as st
import pandas as pd
import os
from datetime import date, datetime

# --- 設定 ---
DATA_FILE = 's25u_rental_db.csv'

# 🔥 手機庫存清單
PHONE_INVENTORY = [
    "S25U 白色",
    "S25U 綠色",
    "S25U 藍色",
    "S24U 藍色",
    "S23U 黑色",
    "iPhone 17 Pro 銀色"
]

# 🌍 國家選項
COUNTRY_OPTIONS = ["台灣", "南韓", "日本", "菲律賓", "其他"]

# 🏙️ 台灣縣市完整清單 (依照你提供的區域分類排序)
CITY_OPTIONS = [
    # 北部
    "臺北市", "新北市", "基隆市", "桃園市", "新竹市", "新竹縣", "宜蘭縣",
    # 中部
    "臺中市", "苗栗縣", "彰化縣", "南投縣", "雲林縣",
    # 南部
    "高雄市", "臺南市", "嘉義市", "嘉義縣", "屏東縣",
    # 東部
    "花蓮縣", "臺東縣",
    # 離島
    "澎湖縣", "金門縣", "連江縣",
    # 其他
    "國外/其他"
]

st.set_page_config(page_title="手機租賃管理系統", layout="wide", page_icon="📱")

# --- 標題區 ---
st.title("📱 演唱會手機租賃管理系統")
st.caption("老闆專用後台 | 支援跨國租賃 | 月份分類管理")

# --- 1. 左側邊欄：新增訂單 ---
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
        
        # 🔥 新增：國家選擇
        target_country = st.selectbox("前往國家", COUNTRY_OPTIONS)
        
        # 縣市選擇 (如果是國外，老闆可以選 '國外/其他'，或是照選不誤)
        target_city = st.selectbox("演唱會縣市", CITY_OPTIONS)
        
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

    # --- 資料保險箱 ---
    st.markdown("---")
    st.header("📂 資料保險箱")
    
    if os.path.exists(DATA_FILE):
        current_df = pd.read_csv(DATA_FILE)
        csv_export = current_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 下載 Excel 備份 (修正亂碼版)",
            data=csv_export,
            file_name=f"backup_rentals_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    uploaded_file = st.file_uploader("📤 上傳舊檔以還原資料", type=['csv'])
    if uploaded_file is not None:
        try:
            uploaded_df = pd.read_csv(uploaded_file)
            uploaded_df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')
            st.success("✅ 資料還原成功！")
            st.rerun()
        except Exception as e:
            st.error(f"還原失敗：{e}")

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
        "國家": target_country, # 🔥 新欄位
        "縣市": target_city,
        "演唱會": concert_name,
        "租金": rent_fee,
        "押金": deposit
    }
    
    df_new = pd.DataFrame([new_data])
    
    if not os.path.exists(DATA_FILE):
        df_new.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')
    else:
        existing_df = pd.read_csv(DATA_FILE)
        updated_df = pd.concat([existing_df, df_new], ignore_index=True)
        updated_df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')
        
    st.toast(f"已新增訂單：{customer_name}", icon="🎉")

# --- 3. 主畫面顯示 ---

if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
    
    # --- 防呆處理區 ---
    # 1. 手機欄位舊換新
    if '手機編號' not in df.columns:
        if '手機型號' in df.columns:
            df['手機編號'] = df['手機型號']
        else:
            df['手機編號'] = "未知型號"

    # 2. 🔥 國家欄位補全 (舊資料沒有這個欄位，預設填入 '台灣')
    if '國家' not in df.columns:
        df['國家'] = '台灣'

    # 3. 日期格式轉換
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
        st.info("💡 操作教學：上方選擇月份，編輯後請務必按下「💾 儲存修改」！")
        
        # 月份篩選器
        temp_df = df.copy()
        temp_df['日期物件'] = pd.to_datetime(temp_df['開始日期'])
        temp_df['月份'] = temp_df['日期物件'].dt.strftime('%Y-%m')
        available_months = sorted(temp_df['月份'].dropna().unique().tolist(), reverse=True)
        
        col_filter, col_dummy = st.columns([1, 3])
        with col_filter:
            selected_month = st.selectbox("📅 請選擇月份過濾：", ["全部顯示"] + available_months)

        if selected_month == "全部顯示":
            display_df = df.copy()
            display_df = display_df.sort_values(by="開始日期", ascending=False)
        else:
            display_df = df[temp_df['月份'] == selected_month].copy()

        # 🔥 可編輯表格 (加入國家與完整縣市選單)
        edited_df = st.data_editor(
            display_df, 
            use_container_width=True,
            num_rows="dynamic",
            column_config={
                "狀態": st.column_config.SelectboxColumn("狀態", options=["預約確認", "已取機(租借中)", "已歸還(結案)", "取消"], required=True),
                "手機編號": st.column_config.SelectboxColumn("手機型號", options=PHONE_INVENTORY, required=True),
                "國家": st.column_config.SelectboxColumn("國家", options=COUNTRY_OPTIONS, required=True), # 🔥 國家也可編輯
                "縣市": st.column_config.SelectboxColumn("縣市", options=CITY_OPTIONS, required=True), # 🔥 縣市也可編輯
                "租金": st.column_config.NumberColumn(format="$%d"),
                "押金": st.column_config.NumberColumn(format="$%d"),
                "開始日期": st.column_config.DateColumn(format="YYYY-MM-DD"),
                "結束日期": st.column_config.DateColumn(format="YYYY-MM-DD"),
            }
        )

        col_save, col_info = st.columns([1, 4])
        with col_save:
            if st.button("💾 儲存修改", type="primary"):
                if selected_month == "全部顯示":
                    final_df = edited_df
                else:
                    df.update(edited_df)
                    final_df = df
                
                final_df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')
                st.success(f"✅ {selected_month} 的資料已更新！")
                st.rerun()
        
        st.divider()
        
        with st.expander("🗑️ 刪除訂單 (進階選項)", expanded=False):
            st.warning("⚠️ 這裡可以刪除任意訂單")
            delete_options = [f"{i}: {row['姓名']} - {row['手機編號']} ({row['開始日期']})" for i, row in df.iterrows()]
            if delete_options:
                selected_to_delete = st.selectbox("選擇要永久刪除的訂單：", delete_options)
                if st.button("確認刪除 ❌"):
                    index_to_drop = int(selected_to_delete.split(":")[0])
                    df.drop(index_to_drop).to_csv(DATA_FILE, index=False, encoding='utf-8-sig')
                    st.success("訂單已刪除！")
                    st.rerun()

    with tab2:
        st.subheader("手機預約狀況")
        occupied = df[df['狀態'].isin(['預約確認', '已取機(租借中)'])]
        if not occupied.empty:
            st.dataframe(occupied[['手機編號', '開始日期', '結束日期', '姓名', '國家', '狀態']], use_container_width=True)
        else:
            st.success("目前所有手機皆在庫，隨時可租！")

    with tab3:
        col_a, col_b = st.columns(2)
        with col_a:
            st.write("🌏 **租客前往國家比例**")
            if '國家' in df.columns and not df['國家'].empty:
                 st.bar_chart(df['國家'].value_counts())
        with col_b:
            st.write("📍 **台灣熱門演唱會縣市**")
            # 這裡我們簡單過濾掉 '國外' 只看台灣的縣市分佈
            if '縣市' in df.columns and not df['縣市'].empty:
                tw_data = df[df['國家'] == '台灣']
                if not tw_data.empty:
                    st.bar_chart(tw_data['縣市'].value_counts())
                else:
                    st.info("尚無台灣訂單數據")

else:
    st.info("👋 歡迎老闆！左側可上傳舊檔還原資料，或建立新資料。")
