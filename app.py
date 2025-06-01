import streamlit as st
import pandas as pd
from datetime import date
import plotly.express as px
import io

# 簡易登入
def login():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.title("🔐 請登入")
        username = st.text_input("使用者名稱")
        password = st.text_input("密碼", type="password")
        if st.button("登入"):
            if username == "user" and password == "1234":  # 你可以改這裡
                st.session_state.logged_in = True
                st.experimental_rerun()
            else:
                st.error("❌ 帳號或密碼錯誤")
        st.stop()

login()

# 初始化 session_state
if "records" not in st.session_state:
    st.session_state.records = []

if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

st.set_page_config(page_title="記帳 App", page_icon="💰")
st.title("💰 我的記帳小幫手")
st.markdown("快速記錄每筆支出，並自動統計分類支出。")

# 篩選月份
all_dates = [r["日期"] for r in st.session_state.records]
all_dates = sorted(list(set(all_dates)))
all_months = sorted(list(set([d.strftime("%Y-%m") for d in all_dates])))

selected_month = st.selectbox("📅 選擇月份篩選（全部顯示請選空白）", [""] + all_months)

def filter_by_month(records, month):
    if month == "" or month is None:
        return records
    else:
        return [r for r in records if r["日期"].strftime("%Y-%m") == month]

filtered_records = filter_by_month(st.session_state.records, selected_month)

# 輸入表單區
st.header("✏️ 輸入或修改資料")
col1, col2 = st.columns(2)
with col1:
    input_date = st.date_input("📅 日期", value=date.today())
    input_category = st.selectbox("📂 分類", ["🍔 餐飲", "🚇 交通", "🍿 娛樂", "🛒 生活用品", "📦 其他"])
with col2:
    input_amount = st.number_input("💵 金額", min_value=0.0, format="%.2f")
    input_note = st.text_input("📝 備註", "")

if st.session_state.edit_index is None:
    if st.button("➕ 新增帳目"):
        if input_amount > 0:
            st.session_state.records.append({
                "日期": input_date,
                "分類": input_category,
                "金額": input_amount,
                "備註": input_note
            })
            st.success("✅ 新增成功！")
        else:
            st.error("⚠️ 金額需大於 0")
else:
    if st.button("✅ 確認修改"):
        st.session_state.records[st.session_state.edit_index] = {
            "日期": input_date,
            "分類": input_category,
            "金額": input_amount,
            "備註": input_note
        }
        st.session_state.edit_index = None
        st.success("✏️ 修改完成！")

# 顯示帳目清單
st.header("📋 帳目清單（依日期排序）")
if filtered_records:
    df = pd.DataFrame(filtered_records)
    df = df.sort_values(by="日期", ascending=False).reset_index(drop=True)

    grouped = df.groupby("日期")
    for date_value, group_df in grouped:
        st.subheader(f"📅 {date_value}")
        for i, row in group_df.iterrows():
            st.markdown(f"**{row['分類']}** - NT${row['金額']:.2f}　📝 {row['備註']}")
            cols = st.columns([1, 1])
            if cols[0].button("✏️ 修改", key=f"edit{i}"):
                st.session_state.edit_index = st.session_state.records.index(filtered_records[i])
                input_date = row["日期"]
                input_category = row["分類"]
                input_amount = row["金額"]
                input_note = row["備註"]
            if cols[1].button("🗑️ 刪除", key=f"delete{i}"):
                idx = st.session_state.records.index(filtered_records[i])
                st.session_state.records.pop(idx)
                st.experimental_rerun()
            st.markdown("---")
else:
    st.info("目前尚無紀錄")

# 匯出 CSV 按鈕
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8-sig')

if filtered_records:
    csv_df = pd.DataFrame(filtered_records)
    csv_data = convert_df_to_csv(csv_df)
    st.download_button(
        label="📥 下載目前資料（CSV）",
        data=csv_data,
        file_name="accounting_records.csv",
        mime="text/csv"
    )

# 圖表
if filtered_records:
    st.subheader("📊 各分類支出圖表（互動式）")
    chart_data = pd.DataFrame(filtered_records).groupby("分類")["金額"].sum().reset_index()
    fig = px.bar(chart_data, x="分類", y="金額", color="分類",
                 text="金額", title="分類支出總覽",
                 labels={"分類": "分類", "金額": "金額 (元)"})
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
