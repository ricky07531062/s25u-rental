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

# 📢 客群來源選項
SOURCE_OPTIONS = ["Threads", "FB", "IG", "其他"]

# 🏙️ 台灣縣市完整清單
CITY_OPTIONS = [
    "臺北市", "新北市", "基隆市", "桃園市", "新竹市", "新竹縣", "宜蘭縣",
    "臺中市", "苗栗縣", "彰化縣", "南投縣", "雲林縣",
    "高雄市", "臺南市", "嘉義市", "嘉義縣", "屏東縣",
    "花蓮縣", "臺東縣",
    "澎湖縣", "金門縣", "連江縣",
    "國外/其他"
]

st.set_page_config(page_title="手機租賃管理系統", layout="wide", page_icon="📱")

# --- 標題區 ---
st.title("📱 演唱會手機租賃管理系統")
st.caption("老闆專用後台 | 行銷數據分析 | 來源追蹤")

# --- 1. 左側邊欄：新增訂單 ---
with st.sidebar:
    st.header("📝 新增租借單")
    with st.form(key='rental_form'):
        col1, col2 = st.columns(2)
        with col1:
            customer_name = st.text_input("客戶姓名")
            gender = st.selectbox("性別", ["女", "男", "其他"])
        with col2:
            source = st.selectbox("客群來源", SOURCE_OPTIONS)
            age = st.number_input("年齡", 15, 80, 25)

        st.markdown("---")
        target_country = st.selectbox("前往國家", COUNTRY_OPTIONS)
        target_city = st.selectbox("演唱會縣市", CITY_OPTIONS)
        concert_name = st.text_input("演唱會名稱 (選填)")
        
        date_range = st.date_input("租借日期區間", value=(date.today(), date.today()), format="YYYY/MM/DD")
        
        st.markdown("---")
        selected_phone = st.selectbox("指派手機", PHONE_INVENTORY)
        
        rent_fee = st.number_input("租金收入 ($)", min_value=0, value=1200, step=100)
        deposit = st.number_input("收取押金 ($)", min_value=0, value=3000, step=500)
        
        status = st.selectbox("訂單狀態", ["預約確認", "已取機(租借中)", "已歸還(結案)", "取消"])
        
        submit = st.form_submit_button("✅ 建立訂單")

    # --- 資料保險箱 ---
    st.markdown("---")
    st.header("📂 資料保險箱")
    
    if os.path.exists(DATA_FILE):
        current_df = pd.read_csv(DATA_FILE)
        csv_export = current_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 下載 Excel 備份",
            data=csv_export,
            file_name=f"backup_rentals_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    uploaded_file = st.file_uploader("📤 上傳舊檔還原", type=['csv'])
    if uploaded_file is not None:
        try:
            uploaded_df = pd.read_csv(uploaded_file)
            uploaded_df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')
            st.success("✅ 還原成功！")
            st.rerun()
        except Exception as e:
            st.error(f"還原失敗：{e}")

# --- 2. 邏輯處理 ---
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
        "來源": source,
        "性別": gender,
        "年齡": age,
        "國家": target_country,
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
    
    # --- 防呆與資料清洗 ---
    if '手機編號' not in df.columns:
        df['手機編號'] = df.get('手機型號', "未知型號")
    if '國家' not in df.columns:
        df['國家'] = '台灣'
    
    if '來源' not in df.columns:
        df['來源'] = '舊資料'
    else:
        df['來源'] = df['來源'].fillna('未紀錄')
        
    df['開始日期'] = pd.to_datetime(df['開始日期'], errors='coerce').dt.date
    df['結束日期'] = pd.to_datetime(df['結束日期'], errors='coerce').dt.date

    # KPI
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
    tab1, tab2, tab3 = st.tabs(["✏️ 訂單管理", "🔍 庫存表", "📊 客群數據"])

    with tab1:
        # 月份篩選
        temp_df = df.copy()
        temp_df['日期物件'] = pd.to_datetime(temp_df['開始日期'])
        temp_df['月份'] = temp_df['日期物件'].dt.strftime('%Y-%m')
        available_months = sorted(temp_df['月份'].dropna().unique().tolist(), reverse=True)
        
        col_filter, _ = st.columns([1, 3])
        with col_filter:
            selected_month = st.selectbox("📅 選擇月份：", ["全部顯示"] + available_months)

        if selected_month == "全部顯示":
            display_df = df.sort_values(by="開始日期", ascending=False)
        else:
            display_df = df[temp_df['月份'] == selected_month].copy()

        # 🔥 關鍵修改：只選擇我們要顯示的欄位 (這裡手動排除 '電話')
        # 定義顯示順序
        cols_to_show = [
            "建檔時間", "狀態", "手機編號", "來源", 
            "開始日期", "結束日期", "姓名", 
            "性別", "年齡", "國家", "縣市", "演唱會", 
            "租金", "押金"
        ]
        
        # 只保留資料庫裡真的有的欄位 (防呆)
        final_cols = [c for c in cols_to_show if c in display_df.columns]
        
        # 使用篩選後的欄位進行顯示
        edited_df = st.data_editor(
            display_df[final_cols], 
            use_container_width=True,
            num_rows="dynamic",
            column_config={
                "狀態": st.column_config.SelectboxColumn("狀態", options=["預約確認", "已取機(租借中)", "已歸還(結案)", "取消"], required=True),
                "手機編號": st.column_config.SelectboxColumn("手機型號", options=PHONE_INVENTORY, required=True),
                "來源": st.column_config.SelectboxColumn("客群來源", options=SOURCE_OPTIONS, required=True),
                "國家": st.column_config.SelectboxColumn("國家", options=COUNTRY_OPTIONS, required=True),
                "縣市": st.column_config.SelectboxColumn("縣市", options=CITY_OPTIONS, required=True),
                "租金": st.column_config.NumberColumn(format="$%d"),
                "押金": st.column_config.NumberColumn(format="$%d"),
                "開始日期": st.column_config.DateColumn(format="YYYY-MM-DD"),
                "結束日期": st.column_config.DateColumn(format="YYYY-MM-DD"),
            }
        )

        if st.button("💾 儲存修改", type="primary"):
            if selected_month == "全部顯示":
                final_df = edited_df
            else:
                # 這裡要小心，因為 edited_df 少了電話欄位，我們只更新存在的欄位
                df.update(edited_df)
                final_df = df
            final_df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')
            st.success("✅ 資料已更新！")
            st.rerun()

        with st.expander("🗑️ 刪除訂單"):
            delete_options = [f"{i}: {row['姓名']} - {row['手機編號']} ({row['開始日期']})" for i, row in df.iterrows()]
            if delete_options:
                del_sel = st.selectbox("刪除對象：", delete_options)
                if st.button("確認刪除 ❌"):
                    idx = int(del_sel.split(":")[0])
                    df.drop(idx).to_csv(DATA_FILE, index=False, encoding='utf-8-sig')
                    st.success("已刪除！")
                    st.rerun()

    with tab2:
        st.subheader("手機預約狀況")
        occupied = df[df['狀態'].isin(['預約確認', '已取機(租借中)'])]
        if not occupied.empty:
            # 這裡也移除電話，加入來源
            show_cols_tab2 = [c for c in ['手機編號', '開始日期', '結束日期', '姓名', '來源', '狀態'] if c in occupied.columns]
            st.dataframe(occupied[show_cols_tab2], use_container_width=True)
        else:
            st.success("目前無租用中手機")

    with tab3:
        st.subheader("📊 客群數據儀表板")
        
        st.write("📢 **客群來源分佈**")
        if '來源' in df.columns and not df['來源'].empty:
            st.bar_chart(df['來源'].value_counts(), horizontal=True)
        
        st.divider()

        st.write("👫 **男女比例分析**")
        if '性別' in df.columns and not df['性別'].empty:
            gender_counts = df['性別'].value_counts()
            g_col1, g_col2, g_col3 = st.columns(3)
            total_people = gender_counts.sum()
            male_count = gender_counts.get('男', 0)
            female_count = gender_counts.get('女', 0)
            
            g_col1.metric("總人數", f"{total_people} 人")
            g_col2.metric("女性佔比", f"{female_count/total_people:.0%}" if total_people > 0 else "0%", f"{female_count} 人")
            g_col3.metric("男性佔比", f"{male_count/total_people:.0%}" if total_people > 0 else "0%", f"{male_count} 人")
            st.bar_chart(gender_counts, horizontal=True)
            
        st.divider()

        col_a, col_b = st.columns(2)
        with col_a:
            st.write("🌏 **租客前往國家**")
            if '國家' in df.columns and not df['國家'].empty:
                st.bar_chart(df['國家'].value_counts(), horizontal=True)
                
        with col_b:
            st.write("📍 **台灣熱門演唱會縣市**")
            if '縣市' in df.columns and not df['縣市'].empty:
                tw_data = df[df['國家'] == '台灣']
                if not tw_data.empty:
                    st.bar_chart(tw_data['縣市'].value_counts(), horizontal=True)
                else:
                    st.info("尚無台灣訂單數據")

else:
    st.info("👋 歡迎老闆！左側可上傳舊檔還原資料，或建立新資料。")
